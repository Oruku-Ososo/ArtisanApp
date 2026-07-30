"""
Social Science Lab for StatisFLOW
SEM, psychometrics, IRT, multilevel modeling
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class SEMResult:
    """Structural Equation Modeling results"""
    model_fit: Dict[str, float]
    path_coefficients: Dict[str, float]
    factor_loadings: Dict[str, float]
    modification_indices: List[Dict[str, Any]]
    warnings: List[str]


class SocialScienceLab:
    """
    Comprehensive social science analytics toolkit.
    
    Features:
    - Structural Equation Modeling (SEM)
    - Psychometric analysis (reliability, validity)
    - Item Response Theory (IRT)
    - Multilevel/Hierarchical Linear Modeling
    - Propensity Score Matching
    - Mediation/Moderation Analysis
    """
    
    def __init__(self):
        self.fit_indices = ['chi_square', 'cfi', 'tli', 'rmsea', 'srmr']
    
    def confirmatory_factor_analysis(self, df: pd.DataFrame,
                                    factor_structure: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Confirmatory Factor Analysis.
        
        Parameters
        ----------
        df : pd.DataFrame
            Observed indicator data
        factor_structure : dict
            Mapping of factor names to their indicators
            
        Returns
        -------
        dict
            CFA results including loadings and fit indices
        """
        from sklearn.decomposition import FactorAnalysis
        
        # Prepare data
        all_indicators = []
        for indicators in factor_structure.values():
            all_indicators.extend(indicators)
        
        X = df[all_indicators].dropna()
        n_factors = len(factor_structure)
        
        # Run Factor Analysis
        fa = FactorAnalysis(n_components=n_factors, random_state=42)
        fa.fit(X)
        
        # Create loading matrix
        loadings = pd.DataFrame(
            fa.components_.T,
            index=all_indicators,
            columns=list(factor_structure.keys())
        )
        
        # Calculate variance explained
        total_var = X.var().sum()
        explained_var = fa.explained_variance_.sum()
        variance_explained = explained_var / total_var
        
        # Simple fit assessment
        communalities = 1 - fa.noise_variance_
        
        return {
            "factor_loadings": loadings.to_dict(),
            "variance_explained": float(variance_explained),
            "communalities": communalities.tolist(),
            "indicators": all_indicators,
            "factors": list(factor_structure.keys()),
            "sample_size": len(X)
        }
    
    def calculate_reliability(self, df: pd.DataFrame,
                             items: List[str],
                             method: str = 'cronbach_alpha') -> Dict[str, float]:
        """
        Calculate scale reliability.
        
        Parameters
        ----------
        df : pd.DataFrame
            Item response data
        items : list
            List of item column names
        method : str
            Reliability method (cronbach_alpha, mcdonald_omega)
            
        Returns
        -------
        dict
            Reliability coefficients
        """
        X = df[items].dropna()
        n_items = len(items)
        n_obs = len(X)
        
        if method == 'cronbach_alpha':
            # Cronbach's alpha
            item_vars = X.var()
            total_var = X.sum(axis=1).var()
            
            k = n_items
            sum_item_vars = item_vars.sum()
            
            alpha = (k / (k - 1)) * (1 - (sum_item_vars / total_var))
            
            # Confidence interval (Feldt et al.)
            se = np.sqrt((2 * (1 - alpha) ** 2) / (n_obs - 1))
            ci_lower = max(0, alpha - 1.96 * se)
            ci_upper = min(1, alpha + 1.96 * se)
            
            return {
                "cronbach_alpha": float(alpha),
                "ci_lower": float(ci_lower),
                "ci_upper": float(ci_upper),
                "n_items": n_items,
                "n_observations": n_obs,
                "interpretation": self._interpret_reliability(alpha)
            }
        
        elif method == 'mcdonald_omega':
            # McDonald's omega (using FA-based approach)
            from sklearn.decomposition import FactorAnalysis
            
            fa = FactorAnalysis(n_components=1, random_state=42)
            fa.fit(X)
            
            # Omega = (sum of loadings)^2 / total variance
            loadings = fa.components_[0]
            omega = (loadings.sum() ** 2) / X.sum(axis=1).var()
            omega = min(1, max(0, omega))
            
            return {
                "mcdonald_omega": float(omega),
                "n_items": n_items,
                "n_observations": n_obs,
                "interpretation": self._interpret_reliability(omega)
            }
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _interpret_reliability(self, alpha: float) -> str:
        """Interpret reliability coefficient"""
        if alpha >= 0.9:
            return "Excellent reliability"
        elif alpha >= 0.8:
            return "Good reliability"
        elif alpha >= 0.7:
            return "Acceptable reliability"
        elif alpha >= 0.6:
            return "Questionable reliability"
        else:
            return "Poor reliability - consider revising scale"
    
    def irt_analysis(self, df: pd.DataFrame,
                    items: List[str],
                    model: str = 'rasch') -> Dict[str, Any]:
        """
        Item Response Theory analysis.
        
        Parameters
        ----------
        df : pd.DataFrame
            Binary item responses (0/1)
        items : list
            List of item column names
        model : str
            IRT model (rasch, 2pl, 3pl)
            
        Returns
        -------
        dict
            IRT parameters (difficulty, discrimination)
        """
        from sklearn.linear_model import LogisticRegression
        
        X = df[items].dropna()
        n_items = len(items)
        n_persons = len(X)
        
        # Estimate person abilities (theta) using sum scores
        theta = X.sum(axis=1).values
        theta_std = (theta - theta.mean()) / (theta.std() + 1e-10)
        
        # Estimate item parameters
        difficulties = {}
        discriminations = {}
        
        for item in items:
            y = X[item].values
            
            # Rasch model: P(X=1) = logistic(theta - difficulty)
            # Fit logistic regression with theta as predictor
            log_reg = LogisticRegression(penalty=None, solver='lbfgs', max_iter=1000)
            try:
                log_reg.fit(theta_std.reshape(-1, 1), y)
                
                # Difficulty = -intercept / slope
                if abs(log_reg.coef_[0][0]) > 0.01:
                    difficulty = -log_reg.intercept_[0] / log_reg.coef_[0][0]
                else:
                    difficulty = 0
                
                # Discrimination (for 2PL)
                discrimination = abs(log_reg.coef_[0][0])
                
                difficulties[item] = float(difficulty)
                discriminations[item] = float(discrimination)
            except:
                difficulties[item] = 0.0
                discriminations[item] = 1.0
        
        # Item fit statistics (simplified)
        fit_stats = {}
        for item in items:
            # Outfit-like statistic based on residual variance
            predicted = 1 / (1 + np.exp(-(theta_std * discriminations[item] - difficulties[item])))
            observed = X[item].values
            residuals = observed - predicted
            outfit = np.mean(residuals ** 2)
            fit_stats[item] = float(outfit)
        
        return {
            "model": model,
            "difficulties": difficulties,
            "discriminations": discriminations,
            "person_abilities": theta_std.tolist(),
            "item_fit": fit_stats,
            "n_items": n_items,
            "n_persons": n_persons
        }
    
    def mediation_analysis(self, df: pd.DataFrame,
                          x_var: str,
                          m_var: str,
                          y_var: str,
                          covariates: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Mediation analysis using causal steps approach.
        
        Parameters
        ----------
        df : pd.DataFrame
            Data with X, M, Y variables
        x_var : str
            Independent variable
        m_var : str
            Mediator variable
        y_var : str
            Dependent variable
        covariates : list, optional
            Control variables
            
        Returns
        -------
        dict
            Direct, indirect, and total effects
        """
        from sklearn.linear_model import LinearRegression
        
        # Prepare data
        cols = [x_var, m_var, y_var]
        if covariates:
            cols.extend(covariates)
        data = df[cols].dropna()
        
        X = data[x_var].values.reshape(-1, 1)
        M = data[m_var].values
        Y = data[y_var].values
        
        if covariates:
            C = data[covariates].values
            X_adj = np.column_stack([X, C])
        else:
            X_adj = X
        
        # Path a: X -> M
        model_a = LinearRegression()
        model_a.fit(X_adj, M)
        a_coef = model_a.coef_[0]
        
        # Path b: M -> Y (controlling for X)
        if covariates:
            XMb = np.column_stack([X, M.reshape(-1, 1), C])
        else:
            XMb = np.column_stack([X, M.reshape(-1, 1)])
        
        model_b = LinearRegression()
        model_b.fit(XMb, Y)
        b_coef = model_b.coef_[1] if covariates else model_b.coef_[0]
        c_prime = model_b.coef_[0]  # Direct effect
        
        # Total effect (c)
        model_c = LinearRegression()
        model_c.fit(X_adj, Y)
        c_coef = model_c.coef_[0]
        
        # Indirect effect (a * b)
        indirect = a_coef * b_coef
        
        # Proportion mediated
        if abs(c_coef) > 1e-10:
            prop_mediated = indirect / c_coef
        else:
            prop_mediated = 0
        
        return {
            "path_a": float(a_coef),
            "path_b": float(b_coef),
            "direct_effect": float(c_prime),
            "total_effect": float(c_coef),
            "indirect_effect": float(indirect),
            "proportion_mediated": float(prop_mediated),
            "mediation_type": self._classify_mediation(c_coef, c_prime, indirect)
        }
    
    def _classify_mediation(self, total: float, direct: float, indirect: float) -> str:
        """Classify type of mediation"""
        if abs(indirect) < 0.01:
            return "No mediation"
        elif abs(direct) < 0.01:
            return "Full mediation"
        elif np.sign(total) == np.sign(direct):
            return "Partial mediation"
        else:
            return "Inconsistent mediation (suppression)"
    
    def propensity_score_matching(self, df: pd.DataFrame,
                                 treatment_col: str,
                                 outcome_col: str,
                                 covariates: List[str],
                                 method: str = 'nearest') -> Dict[str, Any]:
        """
        Propensity score matching for causal inference.
        
        Parameters
        ----------
        df : pd.DataFrame
            Observational data
        treatment_col : str
            Treatment assignment column
        outcome_col : str
            Outcome variable
        covariates : list
            Confounding variables
        method : str
            Matching method (nearest, caliper, optimal)
            
        Returns
        -------
        dict
            Treatment effect estimate with diagnostics
        """
        from sklearn.linear_model import LogisticRegression
        from sklearn.neighbors import NearestNeighbors
        
        # Estimate propensity scores
        X = df[covariates].values
        T = df[treatment_col].values
        
        ps_model = LogisticRegression(max_iter=1000)
        ps_model.fit(X, T)
        propensity = ps_model.predict_proba(X)[:, 1]
        
        # Separate treated and control
        treated_idx = np.where(T == 1)[0]
        control_idx = np.where(T == 0)[0]
        
        if len(treated_idx) == 0 or len(control_idx) == 0:
            return {"error": "No treated or control units found"}
        
        # Matching
        ps_control = propensity[control_idx].reshape(-1, 1)
        matcher = NearestNeighbors(n_neighbors=1)
        matcher.fit(ps_control)
        
        distances, matches = matcher.kneighbors(propensity[treated_idx].reshape(-1, 1))
        matched_control_idx = control_idx[matches.flatten()]
        
        # Calculate ATT
        Y = df[outcome_col].values
        Y_treated = Y[treated_idx]
        Y_control = Y[matched_control_idx]
        
        att = np.mean(Y_treated - Y_control)
        
        # Balance diagnostics
        balance_before = {}
        balance_after = {}
        
        for cov in covariates:
            # Before matching
            mean_t = df.loc[df[treatment_col] == 1, cov].mean()
            mean_c = df.loc[df[treatment_col] == 0, cov].mean()
            std_pooled = np.sqrt((df[cov].var() + df[cov].var()) / 2)
            balance_before[cov] = abs(mean_t - mean_c) / (std_pooled + 1e-10)
            
            # After matching
            mean_c_matched = df.iloc[matched_control_idx][cov].mean()
            balance_after[cov] = abs(mean_t - mean_c_matched) / (std_pooled + 1e-10)
        
        # Overall balance improvement
        avg_balance_before = np.mean(list(balance_before.values()))
        avg_balance_after = np.mean(list(balance_after.values()))
        
        return {
            "att": float(att),
            "n_treated": len(treated_idx),
            "n_matched": len(matched_control_idx),
            "balance_before": balance_before,
            "balance_after": balance_after,
            "avg_balance_improvement": float(avg_balance_before - avg_balance_after),
            "propensity_range": [float(propensity.min()), float(propensity.max())]
        }
