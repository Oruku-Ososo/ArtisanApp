"""
Agri-Tech Suite for StatisFLOW
Spatial yield analysis, precision agriculture, genotype x environment interaction
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class SpatialYieldResult:
    """Results from spatial yield analysis"""
    coordinates: List[Tuple[float, float]]
    yield_values: List[float]
    spatial_autocorrelation: float
    trend_surface: Dict[str, Any]
    hotspots: List[Dict[str, Any]]
    recommendations: List[str]


class AgriTechSuite:
    """
    Comprehensive agricultural analytics toolkit.
    
    Features:
    - Spatial yield analysis and mapping
    - Genotype x Environment (GxE) interaction
    - AMMI and GGE biplot analysis
    - Precision agriculture recommendations
    - Experimental design for field trials (RCBD, Latin Square, Split-plot)
    """
    
    def __init__(self):
        self.experimental_designs = {
            "rcbd": "Randomized Complete Block Design",
            "latin_square": "Latin Square Design",
            "split_plot": "Split-Plot Design",
            "factorial": "Factorial Design",
            "augmented": "Augmented Design"
        }
    
    def analyze_spatial_yield(self, df: pd.DataFrame,
                             lat_col: str,
                             lon_col: str,
                             yield_col: str) -> SpatialYieldResult:
        """
        Analyze spatial patterns in yield data.
        
        Parameters
        ----------
        df : pd.DataFrame
            Data with coordinates and yield
        lat_col : str
            Latitude column name
        lon_col : str
            Longitude column name
        yield_col : str
            Yield measurement column
            
        Returns
        -------
        SpatialYieldResult
            Spatial analysis results
        """
        coords = list(zip(df[lat_col].values, df[lon_col].values))
        yields = df[yield_col].dropna().values
        
        # Calculate spatial autocorrelation (Moran's I approximation)
        from scipy.spatial.distance import pdist, squareform
        from scipy.stats import pearsonr
        
        coord_matrix = np.array(coords)
        dist_matrix = squareform(pdist(coord_matrix))
        
        # Inverse distance weights
        with np.errstate(divide='ignore'):
            weights = 1 / dist_matrix
            np.fill_diagonal(weights, 0)
        
        # Moran's I calculation
        y_mean = np.mean(yields)
        numerator = np.sum(weights * np.outer(yields - y_mean, yields - y_mean))
        denominator = np.sum((yields - y_mean) ** 2)
        n = len(yields)
        
        if denominator > 0:
            morans_i = (n / np.sum(weights)) * (numerator / denominator)
        else:
            morans_i = 0.0
        
        # Trend surface analysis (polynomial regression)
        X = coord_matrix
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import LinearRegression
        
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        
        model = LinearRegression()
        model.fit(X_poly, yields)
        
        trend_surface = {
            "coefficients": model.coef_.tolist(),
            "intercept": float(model.intercept_),
            "r_squared": float(model.score(X_poly, yields))
        }
        
        # Identify hotspots (high-yield clusters)
        yield_threshold = np.percentile(yields, 75)
        hotspot_mask = yields >= yield_threshold
        
        hotspots = []
        for i, is_hotspot in enumerate(hotspot_mask):
            if is_hotspot:
                hotspots.append({
                    "lat": float(coords[i][0]),
                    "lon": float(coords[i][1]),
                    "yield": float(yields[i])
                })
        
        # Generate recommendations
        recommendations = []
        if morans_i > 0.3:
            recommendations.append("Strong spatial autocorrelation detected - consider spatial models")
        if morans_i < -0.3:
            recommendations.append("Negative spatial autocorrelation - check for measurement issues")
        if len(hotspots) > 0:
            recommendations.append(f"Identified {len(hotspots)} high-yield locations for further investigation")
        if trend_surface["r_squared"] > 0.5:
            recommendations.append("Strong spatial trend - consider trend removal before analysis")
        
        return SpatialYieldResult(
            coordinates=coords,
            yield_values=yields.tolist(),
            spatial_autocorrelation=morans_i,
            trend_surface=trend_surface,
            hotspots=hotspots,
            recommendations=recommendations
        )
    
    def ammi_analysis(self, df: pd.DataFrame,
                     genotype_col: str,
                     environment_col: str,
                     yield_col: str) -> Dict[str, Any]:
        """
        AMMI (Additive Main Effects and Multiplicative Interaction) analysis.
        
        Parameters
        ----------
        df : pd.DataFrame
            Multi-environment trial data
        genotype_col : str
            Genotype identifier column
        environment_col : str
            Environment identifier column
        yield_col : str
            Yield measurement column
            
        Returns
        -------
        dict
            AMMI analysis results including IPCA scores
        """
        # Create genotype x environment matrix
        pivot = df.pivot_table(
            index=genotype_col,
            columns=environment_col,
            values=yield_col,
            aggfunc='mean'
        )
        
        # Two-way ANOVA decomposition
        grand_mean = pivot.values.mean()
        genotype_effects = pivot.mean(axis=1).values - grand_mean
        environment_effects = pivot.mean(axis=0).values - grand_mean
        
        # Interaction matrix
        interaction = pivot.values - grand_mean - genotype_effects[:, None] - environment_effects[None, :]
        
        # SVD of interaction matrix
        from scipy.linalg import svd
        U, s, Vt = svd(interaction, full_matrices=False)
        
        # IPCA scores (first two components)
        ipca1_scores_g = U[:, 0] * s[0]
        ipca2_scores_g = U[:, 1] * s[1] if len(s) > 1 else np.zeros(len(U))
        
        ipca1_scores_e = Vt[0, :] * s[0]
        ipca2_scores_e = Vt[1, :] * s[1] if len(Vt) > 1 else np.zeros(len(Vt[0]))
        
        # Variance explained
        total_ss = np.sum(interaction ** 2)
        variance_explained = [(s[i] ** 2) / total_ss for i in range(min(2, len(s)))]
        
        # Stability parameters
        stability = {}
        for i, geno in enumerate(pivot.index):
            # AMMI Stability Value (ASV)
            asv = np.sqrt(ipca1_scores_g[i] ** 2 + ipca2_scores_g[i] ** 2)
            stability[geno] = {
                "ipca1": float(ipca1_scores_g[i]),
                "ipca2": float(ipca2_scores_g[i]),
                "asv": float(asv),
                "mean_yield": float(pivot.loc[geno].mean())
            }
        
        return {
            "grand_mean": float(grand_mean),
            "genotype_effects": dict(zip(pivot.index, genotype_effects)),
            "environment_effects": dict(zip(pivot.columns, environment_effects)),
            "variance_explained": variance_explained,
            "ipca_scores_genotypes": dict(zip(pivot.index, list(zip(ipca1_scores_g, ipca2_scores_g)))),
            "ipca_scores_environments": dict(zip(pivot.columns, list(zip(ipca1_scores_e, ipca2_scores_e)))),
            "stability_parameters": stability,
            "biplot_data": {
                "genotypes": list(pivot.index),
                "environments": list(pivot.columns),
                "ipca1_g": ipca1_scores_g.tolist(),
                "ipca2_g": ipca2_scores_g.tolist(),
                "ipca1_e": ipca1_scores_e.tolist(),
                "ipca2_e": ipca2_scores_e.tolist()
            }
        }
    
    def recommend_precision_ag(self, df: pd.DataFrame,
                               location_cols: List[str],
                               management_zones: int = 3) -> Dict[str, Any]:
        """
        Generate precision agriculture recommendations.
        
        Parameters
        ----------
        df : pd.DataFrame
            Field data with spatial and yield information
        location_cols : list
            Columns with spatial coordinates
        management_zones : int
            Number of management zones to create
            
        Returns
        -------
        dict
            Zone recommendations and variable rate prescriptions
        """
        from sklearn.cluster import KMeans
        
        # Prepare spatial features
        X = df[location_cols].values
        
        # Cluster into management zones
        kmeans = KMeans(n_clusters=management_zones, random_state=42)
        zones = kmeans.fit_predict(X)
        
        # Analyze each zone
        zone_stats = {}
        for z in range(management_zones):
            zone_mask = zones == z
            zone_data = df[zone_mask]
            
            stats = {
                "area_pct": float(zone_mask.sum() / len(df) * 100),
                "mean_yield": float(zone_data.select_dtypes(include=[np.number]).mean().mean()),
                "centroid": kmeans.cluster_centers_[z].tolist(),
                "variability": float(zone_data.select_dtypes(include=[np.number]).std().mean())
            }
            zone_stats[f"zone_{z}"] = stats
        
        # Generate variable rate recommendations
        recommendations = []
        sorted_zones = sorted(zone_stats.items(), key=lambda x: x[1]["mean_yield"])
        
        for zone_name, stats in sorted_zones:
            if stats["mean_yield"] < np.percentile([s["mean_yield"] for s in zone_stats.values()], 33):
                rec = f"{zone_name}: Low productivity - consider increased inputs or soil amendment"
            elif stats["mean_yield"] > np.percentile([s["mean_yield"] for s in zone_stats.values()], 66):
                rec = f"{zone_name}: High productivity - maintain current practices, optimize harvest timing"
            else:
                rec = f"{zone_name}: Medium productivity - fine-tune input application"
            recommendations.append(rec)
        
        return {
            "zone_assignments": zones.tolist(),
            "zone_statistics": zone_stats,
            "variable_rate_prescriptions": recommendations,
            "cluster_centers": kmeans.cluster_centers_.tolist()
        }
    
    def design_field_experiment(self, n_genotypes: int,
                               n_blocks: int,
                               design_type: str = "rcbd",
                               n_replicates: int = 3) -> pd.DataFrame:
        """
        Generate optimal field experimental design.
        
        Parameters
        ----------
        n_genotypes : int
            Number of genotypes/treatments
        n_blocks : int
            Number of blocks
        design_type : str
            Type of design (rcbd, latin_square, split_plot)
        n_replicates : int
            Number of replicates
            
        Returns
        -------
        pd.DataFrame
            Experimental layout
        """
        import random
        random.seed(42)
        
        genotypes = [f"G{i+1}" for i in range(n_genotypes)]
        
        if design_type == "rcbd":
            # Randomized Complete Block Design
            design = []
            for block in range(1, n_blocks + 1):
                treatments = genotypes.copy()
                random.shuffle(treatments)
                for plot, treatment in enumerate(treatments, 1):
                    design.append({
                        "block": block,
                        "plot": plot,
                        "genotype": treatment,
                        "replicate": block
                    })
        
        elif design_type == "latin_square":
            # Latin Square Design
            if n_genotypes != n_blocks:
                raise ValueError("For Latin Square, number of genotypes must equal number of blocks")
            
            # Generate Latin Square
            square = np.zeros((n_genotypes, n_genotypes), dtype=int)
            for i in range(n_genotypes):
                for j in range(n_genotypes):
                    square[i, j] = (i + j) % n_genotypes
            
            design = []
            for row in range(n_genotypes):
                for col in range(n_genotypes):
                    design.append({
                        "row": row + 1,
                        "column": col + 1,
                        "genotype": genotypes[square[row, col]],
                        "block": row + 1
                    })
        
        else:
            # Default to CRD
            design = []
            all_plots = genotypes * n_replicates
            random.shuffle(all_plots)
            for i, geno in enumerate(all_plots):
                design.append({
                    "plot": i + 1,
                    "genotype": geno,
                    "block": 1
                })
        
        return pd.DataFrame(design)
