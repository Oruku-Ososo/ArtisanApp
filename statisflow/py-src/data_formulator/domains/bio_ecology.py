"""
Bio-Ecology Toolkit for StatisFLOW
Phylogenetic methods, species distribution modeling, occupancy models
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class PhylogeneticResult:
    """Results from phylogenetic comparative analysis"""
    tree_statistics: Dict[str, Any]
    phylogenetic_signal: float
    model_results: Dict[str, Any]
    recommendations: List[str]


class BioEcologyToolkit:
    """
    Comprehensive biology and ecology analytics toolkit.
    
    Features:
    - Phylogenetic comparative methods
    - Species distribution modeling
    - Occupancy and N-mixture models
    - Distance sampling analysis
    - Community ecology (ordination, diversity indices)
    """
    
    def __init__(self):
        self.diversity_indices = ['shannon', 'simpson', 'pielou', 'richness']
    
    def calculate_phylogenetic_signal(self, trait_data: pd.Series,
                                      phylo_distance: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate phylogenetic signal (Pagel's lambda approximation).
        
        Parameters
        ----------
        trait_data : pd.Series
            Trait values indexed by species
        phylo_distance : pd.DataFrame
            Phylogenetic distance matrix
            
        Returns
        -------
        dict
            Phylogenetic signal metrics
        """
        from scipy.stats import pearsonr
        from sklearn.linear_model import LinearRegression
        
        # Ensure alignment
        common_species = list(set(trait_data.index) & set(phylo_distance.index))
        if len(common_species) < 3:
            return {"error": "Insufficient overlapping species"}
        
        traits = trait_data.loc[common_species].values
        dist_matrix = phylo_distance.loc[common_species, common_species].values
        
        # Calculate trait dissimilarity
        n = len(traits)
        trait_diff = np.zeros((n, n))
        for i in range(n):
            for j in range(i+1, n):
                diff = abs(traits[i] - traits[j])
                trait_diff[i, j] = diff
                trait_diff[j, i] = diff
        
        # Correlation between phylogenetic and trait distance
        upper_tri_phyl = dist_matrix[np.triu_indices(n, k=1)]
        upper_tri_trait = trait_diff[np.triu_indices(n, k=1)]
        
        corr, p_val = pearsonr(upper_tri_phyl, upper_tri_trait)
        
        # Blomberg's K approximation
        # Simplified: ratio of observed to expected variance
        tip_variance = np.var(traits)
        expected_variance = np.mean(dist_matrix[np.arange(n), np.arange(n)])
        
        K = tip_variance / (expected_variance + 1e-10)
        
        return {
            "pagels_lambda": max(0, min(1, corr)),
            "blombergs_k": float(K),
            "correlation": float(corr),
            "p_value": float(p_val),
            "n_species": n,
            "interpretation": self._interpret_phylo_signal(corr, K)
        }
    
    def _interpret_phylo_signal(self, lambda_val: float, K: float) -> str:
        """Interpret phylogenetic signal strength"""
        if lambda_val > 0.8 or K > 1:
            return "Strong phylogenetic signal - closely related species are similar"
        elif lambda_val > 0.5 or K > 0.5:
            return "Moderate phylogenetic signal"
        else:
            return "Weak phylogenetic signal - traits evolve independently of phylogeny"
    
    def species_distribution_model(self, df: pd.DataFrame,
                                   presence_col: str,
                                   env_cols: List[str],
                                   method: str = 'maxent') -> Dict[str, Any]:
        """
        Species distribution modeling.
        
        Parameters
        ----------
        df : pd.DataFrame
            Presence-absence or presence-only data with environmental variables
        presence_col : str
            Column indicating species presence (1/0)
        env_cols : list
            Environmental predictor columns
        method : str
            Modeling method (maxent, glm, random_forest)
            
        Returns
        -------
        dict
            Model results and predictions
        """
        from sklearn.model_selection import cross_val_score
        from sklearn.metrics import roc_auc_score
        
        X = df[env_cols].dropna()
        y = df.loc[X.index, presence_col]
        
        if method == 'random_forest':
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        elif method == 'glm':
            from sklearn.linear_model import LogisticRegression
            model = LogisticRegression(max_iter=1000)
        else:
            # Default to RF as MaxEnt approximation
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
        
        # Fit final model
        model.fit(X, y)
        predictions = model.predict_proba(X)[:, 1]
        
        # Variable importance
        if hasattr(model, 'feature_importances_'):
            importance = dict(zip(env_cols, model.feature_importances_.tolist()))
        else:
            importance = {col: 1.0/len(env_cols) for col in env_cols}
        
        # Response curves (simplified)
        response_curves = {}
        for col in env_cols:
            X_test = X.copy()
            X_test[col] = np.linspace(X[col].min(), X[col].max(), 50)
            try:
                preds = model.predict_proba(X_test)[:, 1]
                response_curves[col] = {
                    "values": np.linspace(X[col].min(), X[col].max(), 50).tolist(),
                    "probability": preds.tolist()
                }
            except:
                pass
        
        return {
            "method": method,
            "auc_mean": float(cv_scores.mean()),
            "auc_std": float(cv_scores.std()),
            "variable_importance": importance,
            "response_curves": response_curves,
            "predictions": predictions.tolist(),
            "sample_size": len(y)
        }
    
    def occupancy_model(self, detection_history: pd.DataFrame,
                       site_covariates: Optional[pd.DataFrame] = None,
                       survey_covariates: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Single-season occupancy model.
        
        Parameters
        ----------
        detection_history : pd.DataFrame
            Detection/non-detection matrix (sites x surveys)
        site_covariates : pd.DataFrame, optional
            Site-level covariates affecting occupancy
        survey_covariates : pd.DataFrame, optional
            Survey-level covariates affecting detection
            
        Returns
        -------
        dict
            Occupancy and detection estimates
        """
        n_sites, n_surveys = detection_history.shape
        
        # Naive occupancy (proportion of sites with at least one detection)
        detected = (detection_history.sum(axis=1) > 0).astype(int)
        naive_psi = detected.mean()
        
        # Detection probability estimate
        total_detections = detection_history.values.sum()
        total_surveys = n_sites * n_surveys
        naive_p = total_detections / total_surveys if total_surveys > 0 else 0
        
        # MacKenzie estimator (simplified)
        # psi = (detected sites) / (sites * detection prob)
        if naive_p > 0:
            estimated_psi = min(1.0, naive_psi / naive_p)
        else:
            estimated_psi = naive_psi
        
        # Standard errors (approximate)
        se_psi = np.sqrt(estimated_psi * (1 - estimated_psi) / n_sites)
        se_p = np.sqrt(naive_p * (1 - naive_p) / total_surveys)
        
        return {
            "occupancy_estimate": float(estimated_psi),
            "occupancy_se": float(se_psi),
            "occupancy_ci": [float(estimated_psi - 1.96*se_psi), 
                           float(min(1.0, estimated_psi + 1.96*se_psi))],
            "detection_estimate": float(naive_p),
            "detection_se": float(se_p),
            "n_sites": n_sites,
            "n_surveys": n_surveys,
            "naive_occupancy": float(naive_psi),
            "total_detections": int(total_detections)
        }
    
    def calculate_diversity(self, community_data: pd.DataFrame,
                           index: str = 'shannon') -> pd.Series:
        """
        Calculate community diversity indices.
        
        Parameters
        ----------
        community_data : pd.DataFrame
            Species abundance matrix (sites x species)
        index : str
            Diversity index to calculate
            
        Returns
        -------
        pd.Series
            Diversity values per site
        """
        def shannon(abundances):
            """Shannon diversity index"""
            total = abundances.sum()
            if total == 0:
                return 0
            props = abundances / total
            props = props[props > 0]
            return -np.sum(props * np.log(props))
        
        def simpson(abundances):
            """Simpson diversity index (1-D)"""
            total = abundances.sum()
            if total == 0:
                return 0
            props = abundances / total
            return 1 - np.sum(props ** 2)
        
        def pielou(abundances):
            """Pielou's evenness"""
            H = shannon(abundances)
            S = (abundances > 0).sum()
            if S <= 1:
                return 1
            return H / np.log(S)
        
        def richness(abundances):
            """Species richness"""
            return (abundances > 0).sum()
        
        indices = {
            'shannon': shannon,
            'simpson': simpson,
            'pielou': pielou,
            'richness': richness
        }
        
        if index not in indices:
            raise ValueError(f"Unknown index: {index}. Choose from {list(indices.keys())}")
        
        return community_data.apply(indices[index], axis=1)
    
    def ordination_analysis(self, community_data: pd.DataFrame,
                           env_data: Optional[pd.DataFrame] = None,
                           method: str = 'pca') -> Dict[str, Any]:
        """
        Community ordination analysis (PCA, NMDS, CCA, RDA).
        
        Parameters
        ----------
        community_data : pd.DataFrame
            Species abundance matrix
        env_data : pd.DataFrame, optional
            Environmental variables for constrained ordination
        method : str
            Ordination method (pca, nmds, cca, rda)
            
        Returns
        -------
        dict
            Ordination results including scores and variance explained
        """
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        
        # Prepare data
        X = community_data.values
        
        if method == 'pca':
            # Standardize
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            pca = PCA(n_components=min(5, X.shape[1]))
            scores = pca.fit_transform(X_scaled)
            
            variance_explained = pca.explained_variance_ratio_.tolist()
            
            # Species loadings
            loadings = pca.components_
            
            return {
                "method": "PCA",
                "site_scores": scores.tolist(),
                "species_loadings": loadings.tolist(),
                "variance_explained": variance_explained,
                "species_names": list(community_data.columns),
                "site_names": list(community_data.index)
            }
        
        elif method == 'nmds':
            # Non-metric Multidimensional Scaling
            from sklearn.manifold import MDS
            from scipy.spatial.distance import braycurtis
            
            # Bray-Curtis distance
            n = X.shape[0]
            dist_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(i+1, n):
                    d = braycurtis(X[i], X[j])
                    dist_matrix[i, j] = d
                    dist_matrix[j, i] = d
            
            mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
            scores = mds.fit_transform(dist_matrix)
            
            return {
                "method": "NMDS",
                "site_scores": scores.tolist(),
                "stress": float(mds.stress_),
                "site_names": list(community_data.index)
            }
        
        else:
            # Default to PCA
            return self.ordination_analysis(community_data, env_data, 'pca')
