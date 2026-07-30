"""
Auto-Methodologist AI Agent
Designs optimal analysis plans based on research questions, data characteristics, and domain knowledge.
Surpasses JASP/Jamovi by providing intelligent, context-aware methodological recommendations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class ResearchGoal(Enum):
    """Types of research goals"""
    DESCRIPTION = "description"
    EXPLORATION = "exploration"
    HYPOTHESIS_TESTING = "hypothesis_testing"
    PREDICTION = "prediction"
    CAUSAL_INFERENCE = "causal_inference"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    DIMENSION_REDUCTION = "dimension_reduction"
    TIME_SERIES_FORECAST = "time_series_forecast"


class DataStructure(Enum):
    """Data structure types"""
    CROSS_SECTIONAL = "cross_sectional"
    LONGITUDINAL = "longitudinal"
    PANEL = "panel"
    TIME_SERIES = "time_series"
    HIERARCHICAL = "hierarchical"
    SPATIAL = "spatial"
    NETWORK = "network"


@dataclass
class VariableProfile:
    """Profile of a single variable"""
    name: str
    type: str  # continuous, ordinal, nominal, binary, count, datetime
    role: str  # outcome, predictor, covariate, id, weight
    missing_pct: float
    unique_values: int
    skewness: float
    kurtosis: float
    outliers_detected: bool
    distribution_fit: str
    suggestions: List[str] = field(default_factory=list)


@dataclass
class AnalysisPlan:
    """Comprehensive analysis plan"""
    goal: ResearchGoal
    recommended_methods: List[Dict[str, Any]]
    assumptions_to_check: List[str]
    data_requirements: Dict[str, Any]
    potential_pitfalls: List[str]
    alternative_approaches: List[Dict[str, Any]]
    power_analysis: Optional[Dict[str, Any]] = None
    sample_size_recommendation: Optional[int] = None
    confidence_level: float = 0.95
    reasoning: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "goal": self.goal.value,
            "recommended_methods": self.recommended_methods,
            "assumptions_to_check": self.assumptions_to_check,
            "data_requirements": self.data_requirements,
            "potential_pitfalls": self.potential_pitfalls,
            "alternative_approaches": self.alternative_approaches,
            "power_analysis": self.power_analysis,
            "sample_size_recommendation": self.sample_size_recommendation,
            "confidence_level": self.confidence_level,
            "reasoning": self.reasoning
        }


class AutoMethodologistAgent:
    """
    AI-powered methodological advisor that designs optimal analysis plans.
    
    Features:
    - Automatic research goal detection
    - Data-driven method selection
    - Assumption checking roadmap
    - Power analysis integration
    - Domain-specific recommendations
    """
    
    def __init__(self):
        self.method_knowledge_base = self._load_method_knowledge()
        self.domain_rules = self._load_domain_rules()
        
    def _load_method_knowledge(self) -> Dict:
        """Load comprehensive statistical method knowledge base"""
        return {
            "t_test": {
                "goals": [ResearchGoal.HYPOTHESIS_TESTING],
                "data_structures": [DataStructure.CROSS_SECTIONAL],
                "outcome_types": ["continuous"],
                "predictor_types": ["binary", "nominal"],
                "n_predictors": (0, 1),
                "assumptions": ["normality", "homogeneity_of_variance", "independence"],
                "robust_alternatives": ["Mann-Whitney U", "Welch's t-test", "Bootstrap t-test"],
                "min_sample": 20,
                "power_notes": "Requires ~64 subjects per group for medium effect (d=0.5) at 80% power"
            },
            "anova": {
                "goals": [ResearchGoal.HYPOTHESIS_TESTING],
                "data_structures": [DataStructure.CROSS_SECTIONAL],
                "outcome_types": ["continuous"],
                "predictor_types": ["nominal", "ordinal"],
                "n_predictors": (1, 3),
                "assumptions": ["normality", "homogeneity_of_variance", "independence", "sphericity"],
                "robust_alternatives": ["Kruskal-Wallis", "Welch ANOVA", "Aligned Rank Transform"],
                "min_sample": 30,
                "power_notes": "Sample size depends on number of groups and expected effect size"
            },
            "linear_regression": {
                "goals": [ResearchGoal.HYPOTHESIS_TESTING, ResearchGoal.PREDICTION],
                "data_structures": [DataStructure.CROSS_SECTIONAL, DataStructure.LONGITUDINAL],
                "outcome_types": ["continuous"],
                "predictor_types": ["continuous", "ordinal", "nominal", "binary"],
                "n_predictors": (1, 20),
                "assumptions": ["linearity", "normality_of_residuals", "homoscedasticity", 
                               "independence", "no_multicollinearity"],
                "robust_alternatives": ["Robust regression", "Quantile regression", "GLM"],
                "min_sample": 50,
                "power_notes": "Rule of thumb: 10-20 observations per predictor"
            },
            "logistic_regression": {
                "goals": [ResearchGoal.HYPOTHESIS_TESTING, ResearchGoal.CLASSIFICATION],
                "data_structures": [DataStructure.CROSS_SECTIONAL],
                "outcome_types": ["binary", "nominal"],
                "predictor_types": ["continuous", "ordinal", "nominal", "binary"],
                "n_predictors": (1, 20),
                "assumptions": ["linearity_of_logit", "independence", "no_multicollinearity", 
                               "large_sample_size"],
                "robust_alternatives": ["Firth's penalized likelihood", "Exact logistic regression"],
                "min_sample": 100,
                "power_notes": "Need at least 10 events per predictor variable"
            },
            "mixed_effects": {
                "goals": [ResearchGoal.HYPOTHESIS_TESTING, ResearchGoal.PREDICTION],
                "data_structures": [DataStructure.HIERARCHICAL, DataStructure.LONGITUDINAL, DataStructure.PANEL],
                "outcome_types": ["continuous", "binary", "count"],
                "predictor_types": ["continuous", "ordinal", "nominal", "binary"],
                "n_predictors": (1, 15),
                "assumptions": ["normality_of_random_effects", "homoscedasticity", "correct_random_structure"],
                "robust_alternatives": ["Bayesian hierarchical models", "GEE"],
                "min_sample": 30,
                "power_notes": "Power depends on number of clusters and cluster size"
            },
            "survival_analysis": {
                "goals": [ResearchGoal.HYPOTHESIS_TESTING, ResearchGoal.PREDICTION],
                "data_structures": [DataStructure.LONGITUDINAL, DataStructure.TIME_SERIES],
                "outcome_types": ["time_to_event"],
                "predictor_types": ["continuous", "ordinal", "nominal", "binary"],
                "n_predictors": (1, 15),
                "assumptions": ["proportional_hazards", "independent_censoring", "linearity_of_log_hazard"],
                "robust_alternatives": ["Accelerated failure time models", "Random survival forests"],
                "min_sample": 50,
                "power_notes": "Power depends on number of events, not total sample"
            },
            "sem": {
                "goals": [ResearchGoal.HYPOTHESIS_TESTING, ResearchGoal.CAUSAL_INFERENCE],
                "data_structures": [DataStructure.CROSS_SECTIONAL, DataStructure.LONGITUDINAL],
                "outcome_types": ["continuous", "ordinal"],
                "predictor_types": ["continuous", "ordinal", "nominal"],
                "n_predictors": (2, 50),
                "assumptions": ["multivariate_normality", "large_sample", "correct_model_specification",
                               "identification"],
                "robust_alternatives": ["Bayesian SEM", "PLS-SEM", "Robust ML estimation"],
                "min_sample": 200,
                "power_notes": "Minimum 5-10 observations per estimated parameter"
            },
            "arima": {
                "goals": [ResearchGoal.TIME_SERIES_FORECAST, ResearchGoal.PREDICTION],
                "data_structures": [DataStructure.TIME_SERIES],
                "outcome_types": ["continuous"],
                "predictor_types": [],
                "n_predictors": (0, 0),
                "assumptions": ["stationarity", "no_autocorrelation_in_residuals", "normality_of_errors"],
                "robust_alternatives": ["ARIMAX", "VAR", "Prophet", "LSTM"],
                "min_sample": 50,
                "power_notes": "At least 50 observations recommended for reliable estimation"
            },
            "random_forest": {
                "goals": [ResearchGoal.PREDICTION, ResearchGoal.CLASSIFICATION],
                "data_structures": [DataStructure.CROSS_SECTIONAL, DataStructure.LONGITUDINAL],
                "outcome_types": ["continuous", "binary", "nominal"],
                "predictor_types": ["continuous", "ordinal", "nominal", "binary"],
                "n_predictors": (1, 1000),
                "assumptions": ["iid_samples"],
                "robust_alternatives": ["Gradient boosting", "XGBoost", "Neural networks"],
                "min_sample": 100,
                "power_notes": "Performance improves with more data; less interpretable"
            },
            "propensity_score": {
                "goals": [ResearchGoal.CAUSAL_INFERENCE],
                "data_structures": [DataStructure.CROSS_SECTIONAL, DataStructure.LONGITUDINAL],
                "outcome_types": ["continuous", "binary"],
                "predictor_types": ["continuous", "ordinal", "nominal", "binary"],
                "n_predictors": (3, 30),
                "assumptions": ["unconfoundedness", "overlap", "correct_propensity_model", "suta"],
                "robust_alternatives": ["Inverse probability weighting", "Doubly robust estimators",
                                       "Causal forests"],
                "min_sample": 100,
                "power_notes": "Effective sample size reduced after matching/weighting"
            }
        }
    
    def _load_domain_rules(self) -> Dict:
        """Load domain-specific methodological rules"""
        return {
            "agriculture": {
                "common_designs": ["RCBD", "Split-plot", "Latin Square", "Factorial"],
                "special_considerations": ["Spatial autocorrelation", "Genotype x Environment interaction"],
                "preferred_methods": ["Mixed models", "Spatial analysis", "AMMI", "GGE biplot"]
            },
            "biology": {
                "common_designs": ["Completely randomized", "Block design", "Repeated measures"],
                "special_considerations": ["Phylogenetic non-independence", "Allometric scaling"],
                "preferred_methods": ["Phylogenetic comparative methods", "GLMM", "Survival analysis"]
            },
            "ecology": {
                "common_designs": ["Transect sampling", "Quadrat sampling", "Mark-recapture"],
                "special_considerations": ["Zero-inflation", "Detection probability", "Spatial autocorrelation"],
                "preferred_methods": ["Occupancy models", "N-mixture models", "Distance sampling", "ORDINATION"]
            },
            "social_sciences": {
                "common_designs": ["Survey", "Experimental", "Quasi-experimental", "Longitudinal"],
                "special_considerations": ["Measurement error", "Common method bias", "Missing data"],
                "preferred_methods": ["SEM", "Multilevel modeling", "IRT", "Propensity score matching"]
            },
            "epidemiology": {
                "common_designs": ["Cohort", "Case-control", "Cross-sectional", "RCT"],
                "special_considerations": ["Confounding", "Selection bias", "Information bias"],
                "preferred_methods": ["Survival analysis", "Logistic regression", "Poisson regression", "Meta-analysis"]
            }
        }
    
    def analyze_data(self, df: pd.DataFrame, 
                    research_question: Optional[str] = None,
                    domain: Optional[str] = None,
                    goal: Optional[ResearchGoal] = None) -> AnalysisPlan:
        """
        Analyze dataset and generate optimal analysis plan.
        
        Parameters
        ----------
        df : pd.DataFrame
            Input dataset
        research_question : str, optional
            Natural language research question
        domain : str, optional
            Research domain (agriculture, biology, ecology, social_sciences, epidemiology)
        goal : ResearchGoal, optional
            Pre-specified research goal
            
        Returns
        -------
        AnalysisPlan
            Comprehensive analysis plan with recommendations
        """
        # Profile variables
        variable_profiles = self._profile_variables(df)
        
        # Detect data structure
        data_structure = self._detect_data_structure(df)
        
        # Infer or validate research goal
        if goal is None:
            goal = self._infer_research_goal(df, research_question, variable_profiles)
        
        # Select candidate methods
        candidate_methods = self._select_candidate_methods(
            goal=goal,
            data_structure=data_structure,
            variable_profiles=variable_profiles,
            domain=domain
        )
        
        # Rank methods
        ranked_methods = self._rank_methods(candidate_methods, df, variable_profiles, domain)
        
        # Generate analysis plan
        plan = self._generate_analysis_plan(
            goal=goal,
            ranked_methods=ranked_methods,
            variable_profiles=variable_profiles,
            data_structure=data_structure,
            domain=domain,
            research_question=research_question
        )
        
        return plan
    
    def _profile_variables(self, df: pd.DataFrame) -> Dict[str, VariableProfile]:
        """Create detailed profiles for all variables"""
        profiles = {}
        
        for col in df.columns:
            series = df[col].dropna()
            
            # Determine variable type
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                var_type = "datetime"
            elif pd.api.types.is_bool_dtype(df[col]) or (df[col].nunique() == 2):
                var_type = "binary"
            elif pd.api.types.is_categorical_dtype(df[col]) or (
                df[col].nunique() < 10 and pd.api.types.is_integer_dtype(df[col])
            ):
                if df[col].nunique() <= 2:
                    var_type = "binary"
                else:
                    var_type = "ordinal" if df[col].nunique() <= 5 else "nominal"
            elif pd.api.types.is_numeric_dtype(df[col]):
                if df[col].nunique() <= 10:
                    var_type = "ordinal"
                else:
                    var_type = "continuous"
                    # Check for count-like distribution
                    if (df[col] >= 0).all() and (df[col] == df[col].astype(int)).all():
                        var_type = "count"
            else:
                var_type = "nominal"
            
            # Calculate statistics
            missing_pct = (df[col].isna().sum() / len(df)) * 100
            
            if pd.api.types.is_numeric_dtype(df[col]):
                skewness = series.skew() if len(series) > 2 else 0.0
                kurtosis = series.kurtosis() if len(series) > 3 else 0.0
                
                # Simple distribution fit assessment
                if abs(skewness) < 0.5 and abs(kurtosis) < 1:
                    dist_fit = "normal"
                elif skewness > 1:
                    dist_fit = "right_skewed"
                elif skewness < -1:
                    dist_fit = "left_skewed"
                else:
                    dist_fit = "unknown"
                
                # Outlier detection (IQR method)
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                outliers_detected = ((series < Q1 - 1.5 * IQR) | (series > Q3 + 1.5 * IQR)).any()
            else:
                skewness = 0.0
                kurtosis = 0.0
                dist_fit = "categorical"
                outliers_detected = False
            
            # Generate suggestions
            suggestions = []
            if missing_pct > 5:
                suggestions.append(f"Consider imputation for {missing_pct:.1f}% missing values")
            if var_type == "continuous" and abs(skewness) > 2:
                suggestions.append("Consider transformation due to high skewness")
            if outliers_detected:
                suggestions.append("Outliers detected - consider robust methods or investigation")
            if pd.api.types.is_numeric_dtype(df[col]) and df[col].nunique() < 5:
                suggestions.append("Few unique values - consider treating as ordinal/categorical")
            
            profiles[col] = VariableProfile(
                name=col,
                type=var_type,
                role="unknown",  # Will be determined later
                missing_pct=missing_pct,
                unique_values=df[col].nunique(),
                skewness=skewness,
                kurtosis=kurtosis,
                outliers_detected=outliers_detected,
                distribution_fit=dist_fit,
                suggestions=suggestions
            )
        
        return profiles
    
    def _detect_data_structure(self, df: pd.DataFrame) -> DataStructure:
        """Detect the structure of the data"""
        n_rows, n_cols = df.shape
        
        # Check for datetime columns
        datetime_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
        
        # Check for panel/longitudinal indicators
        potential_id_cols = [col for col in df.columns if 
                            df[col].nunique() < n_rows * 0.1 and 
                            df[col].nunique() > 1]
        
        if len(datetime_cols) > 0:
            if len(potential_id_cols) > 0:
                return DataStructure.PANEL
            else:
                return DataStructure.TIME_SERIES
        
        if len(potential_id_cols) > 1:
            return DataStructure.HIERARCHICAL
        
        # Default to cross-sectional
        return DataStructure.CROSS_SECTIONAL
    
    def _infer_research_goal(self, df: pd.DataFrame, 
                            research_question: Optional[str],
                            variable_profiles: Dict[str, VariableProfile]) -> ResearchGoal:
        """Infer research goal from data and question"""
        
        # If research question provided, use NLP to infer goal
        if research_question:
            rq_lower = research_question.lower()
            
            if any(word in rq_lower for word in ["predict", "forecast", "estimate"]):
                return ResearchGoal.PREDICTION
            elif any(word in rq_lower for word in ["cause", "effect", "impact", "influence"]):
                return ResearchGoal.CAUSAL_INFERENCE
            elif any(word in rq_lower for word in ["classify", "categorize", "group"]):
                return ResearchGoal.CLASSIFICATION
            elif any(word in rq_lower for word in ["cluster", "segment"]):
                return ResearchGoal.CLUSTERING
            elif any(word in rq_lower for word in ["difference", "compare", "test"]):
                return ResearchGoal.HYPOTHESIS_TESTING
            elif any(word in rq_lower for word in ["describe", "summarize", "explore"]):
                return ResearchGoal.EXPLORATION
        
        # Infer from data characteristics
        outcomes = [name for name, prof in variable_profiles.items() 
                   if prof.type in ["continuous", "binary", "count"]]
        
        if len(outcomes) == 0:
            return ResearchGoal.CLUSTERING
        
        outcome = variable_profiles[outcomes[0]]
        
        if outcome.type == "binary":
            return ResearchGoal.CLASSIFICATION
        elif outcome.type == "continuous":
            return ResearchGoal.HYPOTHESIS_TESTING
        
        return ResearchGoal.EXPLORATION
    
    def _select_candidate_methods(self, goal: ResearchGoal,
                                  data_structure: DataStructure,
                                  variable_profiles: Dict[str, VariableProfile],
                                  domain: Optional[str]) -> List[str]:
        """Select candidate methods based on constraints"""
        candidates = []
        
        outcome_vars = [name for name, prof in variable_profiles.items() 
                       if prof.type in ["continuous", "binary", "count", "time_to_event"]]
        
        if not outcome_vars:
            # No clear outcome - unsupervised methods
            return ["pca", "factor_analysis", "clustering", "mds"]
        
        outcome_type = variable_profiles[outcome_vars[0]].type
        n_predictors = len(variable_profiles) - len(outcome_vars)
        
        for method_name, method_info in self.method_knowledge_base.items():
            # Check goal match
            if goal not in method_info["goals"]:
                continue
            
            # Check data structure match
            if data_structure not in method_info["data_structures"]:
                continue
            
            # Check outcome type
            if outcome_type not in method_info["outcome_types"]:
                continue
            
            # Check predictor count
            min_pred, max_pred = method_info["n_predictors"]
            if not (min_pred <= n_predictors <= max_pred):
                continue
            
            candidates.append(method_name)
        
        # Add domain-specific methods
        if domain and domain in self.domain_rules:
            domain_prefs = self.domain_rules[domain]["preferred_methods"]
            for pref in domain_prefs:
                pref_lower = pref.lower().replace(" ", "_").replace("-", "_")
                if pref_lower not in candidates:
                    # Map to known methods
                    if "mixed" in pref_lower or "hierarch" in pref_lower:
                        if "mixed_effects" not in candidates:
                            candidates.append("mixed_effects")
        
        return candidates if candidates else ["descriptive_statistics", "data_visualization"]
    
    def _rank_methods(self, candidates: List[str],
                     df: pd.DataFrame,
                     variable_profiles: Dict[str, VariableProfile],
                     domain: Optional[str]) -> List[Dict[str, Any]]:
        """Rank candidate methods by suitability"""
        ranked = []
        
        for method in candidates:
            if method not in self.method_knowledge_base:
                continue
            
            info = self.method_knowledge_base[method]
            score = 100.0
            reasons = []
            
            # Check assumptions feasibility
            assumption_violations = []
            for assumption in info["assumptions"]:
                if assumption == "normality":
                    continuous_vars = [p for p in variable_profiles.values() 
                                      if p.type == "continuous"]
                    non_normal = [p for p in continuous_vars if p.distribution_fit != "normal"]
                    if len(non_normal) > len(continuous_vars) * 0.5:
                        assumption_violations.append("normality")
                        score -= 15
                        reasons.append("Many variables violate normality")
                
                elif assumption == "large_sample":
                    if len(df) < info.get("min_sample", 50):
                        assumption_violations.append("sample_size")
                        score -= 20
                        reasons.append(f"Sample size ({len(df)}) below recommended minimum")
            
            # Domain bonus
            if domain and domain in self.domain_rules:
                domain_prefs = [p.lower().replace(" ", "_").replace("-", "_") 
                               for p in self.domain_rules[domain]["preferred_methods"]]
                if method in domain_prefs or any(m in method for m in domain_prefs):
                    score += 20
                    reasons.append(f"Preferred method in {domain}")
            
            ranked.append({
                "method": method,
                "score": max(score, 0),
                "assumptions": info["assumptions"],
                "assumption_violations": assumption_violations,
                "robust_alternatives": info["robust_alternatives"],
                "min_sample": info.get("min_sample", 50),
                "power_notes": info.get("power_notes", ""),
                "reasons": reasons
            })
        
        # Sort by score
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked
    
    def _generate_analysis_plan(self, goal: ResearchGoal,
                               ranked_methods: List[Dict[str, Any]],
                               variable_profiles: Dict[str, VariableProfile],
                               data_structure: DataStructure,
                               domain: Optional[str],
                               research_question: Optional[str]) -> AnalysisPlan:
        """Generate comprehensive analysis plan"""
        
        if not ranked_methods:
            return AnalysisPlan(
                goal=goal,
                recommended_methods=[],
                assumptions_to_check=[],
                data_requirements={},
                potential_pitfalls=["No suitable methods found for this data configuration"],
                alternative_approaches=[],
                reasoning="Insufficient data or unclear research goal."
            )
        
        top_method = ranked_methods[0]
        method_info = self.method_knowledge_base.get(top_method["method"], {})
        
        # Collect all assumptions to check
        all_assumptions = set()
        for method in ranked_methods[:3]:  # Top 3 methods
            all_assumptions.update(method["assumptions"])
        
        # Identify potential pitfalls
        pitfalls = []
        for method in ranked_methods[:3]:
            if method["assumption_violations"]:
                pitfalls.append(f"{method['method']}: Violates {', '.join(method['assumption_violations'])}")
            if method["score"] < 70:
                pitfalls.append(f"{method['method']}: Low suitability score ({method['score']:.0f})")
        
        # Sample size recommendation
        sample_rec = None
        power_info = None
        if len(variable_profiles) > 0:
            max_min_sample = max(m.get("min_sample", 50) for m in ranked_methods[:3])
            sample_rec = max(max_min_sample, len(list(variable_profiles.keys())) * 15)
            power_info = {"current_n": sum(1 for _ in variable_profiles), 
                         "recommended_n": sample_rec}
        
        # Build reasoning
        reasoning_parts = [
            f"Based on your {'research goal' if research_question else 'data structure'}",
            f"detected as {goal.value.replace('_', ' ')}.",
            f"Data structure: {data_structure.value}.",
            f"Primary recommendation: {top_method['method'].replace('_', ' ').title()}",
            f"(suitability score: {top_method['score']:.0f}/100)."
        ]
        
        if top_method["reasons"]:
            reasoning_parts.append("Key factors: " + "; ".join(top_method["reasons"]))
        
        if domain:
            reasoning_parts.append(f"Domain context: {domain.replace('_', ' ').title()}.")
        
        # Alternative approaches
        alternatives = []
        for method in ranked_methods[1:4]:  # Next 3 best
            alternatives.append({
                "method": method["method"],
                "rationale": f"Alternative with score {method['score']:.0f}/100",
                "when_to_use": f"Consider if {', '.join(method['assumption_violations'])} cannot be resolved"
            })
        
        return AnalysisPlan(
            goal=goal,
            recommended_methods=[{
                "method": top_method["method"],
                "description": f"{top_method['method'].replace('_', ' ').title()} analysis",
                "score": top_method["score"],
                "assumptions": top_method["assumptions"],
                "robust_alternatives": top_method["robust_alternatives"]
            }],
            assumptions_to_check=list(all_assumptions),
            data_requirements={
                "min_sample_size": top_method["min_sample"],
                "outcome_variables": [k for k, v in variable_profiles.items() 
                                     if v.type in ["continuous", "binary", "count"]][:1],
                "predictor_variables": [k for k, v in variable_profiles.items() 
                                       if v.type not in ["datetime"]]
            },
            potential_pitfalls=pitfalls,
            alternative_approaches=alternatives,
            power_analysis=power_info,
            sample_size_recommendation=sample_rec,
            reasoning=" ".join(reasoning_parts)
        )
    
    def explain_method(self, method_name: str) -> Dict[str, Any]:
        """Provide detailed explanation of a statistical method"""
        if method_name not in self.method_knowledge_base:
            return {"error": f"Method '{method_name}' not found in knowledge base"}
        
        info = self.method_knowledge_base[method_name]
        
        return {
            "method": method_name,
            "description": f"{method_name.replace('_', ' ').title()} is a statistical method for...",
            "appropriate_for": [g.value for g in info["goals"]],
            "data_requirements": {
                "outcome_types": info["outcome_types"],
                "predictor_types": info["predictor_types"],
                "predictor_count_range": info["n_predictors"],
                "minimum_sample": info.get("min_sample", 50)
            },
            "assumptions": info["assumptions"],
            "how_to_check_assumptions": self._get_assumption_checks(info["assumptions"]),
            "what_if_violated": info["robust_alternatives"],
            "interpretation_guide": self._get_interpretation_guide(method_name),
            "example_code": self._generate_example_code(method_name)
        }
    
    def _get_assumption_checks(self, assumptions: List[str]) -> Dict[str, str]:
        """Get guidance on how to check each assumption"""
        checks = {
            "normality": "Shapiro-Wilk test, Q-Q plots, histogram inspection",
            "homogeneity_of_variance": "Levene's test, Bartlett's test, residual plots",
            "independence": "Study design review, Durbin-Watson test for time series",
            "linearity": "Scatter plots, component-plus-residual plots",
            "homoscedasticity": "Residual vs fitted plots, Breusch-Pagan test",
            "no_multicollinearity": "VIF (Variance Inflation Factor), correlation matrix",
            "proportional_hazards": "Schoenfeld residuals, log-log survival plots",
            "sphericity": "Mauchly's test",
            "multivariate_normality": "Mardia's test, Henze-Zirkler test"
        }
        return {a: checks.get(a, "Consult statistical literature") for a in assumptions}
    
    def _get_interpretation_guide(self, method_name: str) -> str:
        """Get interpretation guidance for method results"""
        guides = {
            "t_test": "Look at p-value (< 0.05 indicates significant difference) and effect size (Cohen's d)",
            "anova": "Significant F-test indicates at least one group differs; follow up with post-hoc tests",
            "linear_regression": "Examine R² for model fit, coefficients for direction/magnitude, p-values for significance",
            "logistic_regression": "Interpret odds ratios (OR > 1 increases odds, OR < 1 decreases odds)",
            "survival_analysis": "Hazard ratio > 1 indicates increased risk, < 1 indicates protective effect"
        }
        return guides.get(method_name, "Refer to method-specific documentation")
    
    def _generate_example_code(self, method_name: str) -> str:
        """Generate example Python code for the method"""
        examples = {
            "t_test": """
# Independent samples t-test
from scipy import stats
result = stats.ttest_ind(group1, group2)
print(f"t({df}) = {result.statistic:.3f}, p = {result.pvalue:.4f}")
""",
            "anova": """
# One-way ANOVA
import statsmodels.api as sm
from statsmodels.formula.api import ols
model = ols('outcome ~ C(group)', data=df).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)
""",
            "linear_regression": """
# Linear regression
import statsmodels.api as sm
model = sm.OLS(y, sm.add_constant(X)).fit()
print(model.summary())
""",
            "logistic_regression": """
# Logistic regression
import statsmodels.api as sm
model = sm.Logit(y, sm.add_constant(X)).fit()
print(model.summary())
print(f"Odds Ratios: {np.exp(model.params)}")
"""
        }
        return examples.get(method_name, "# Example code not available for this method")
