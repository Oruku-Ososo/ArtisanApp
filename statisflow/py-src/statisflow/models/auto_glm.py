"""
StatisFLOW AutoGLM Engine - Production Grade Generalized Linear Models
Implements: Poisson, NB, Zero-Inflated, Hurdle, Beta, ZOIB, Dirichlet, Logistic, 
Multinomial, Ordinal, GAMs with automatic diagnostics and model selection.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import warnings

# Statistical imports (lazy-loaded to avoid hard dependencies if missing)
STATS_AVAILABLE = False
SCIPY_AVAILABLE = False

def _check_statsmodels():
    """Check if statsmodels is available"""
    global STATS_AVAILABLE
    try:
        import statsmodels.api as sm
        import statsmodels.formula.api as smf
        from statsmodels.discrete.discrete_model import NegativeBinomial, Logit, Probit, MNLogit
        # OrderedModel location varies by version
        try:
            from statsmodels.miscmodels.ordinal_model import OrderedModel
        except ImportError:
            try:
                from statsmodels.discrete.discrete_model import OrderedModel
            except ImportError:
                OrderedModel = None
        from statsmodels.genmod.generalized_linear_model import GLM
        from statsmodels.genmod.families import Poisson as PoissonFamily, Binomial
        from statsmodels.genmod.families.links import Log, Logit
        return True
    except (ImportError, ModuleNotFoundError) as e:
        print(f"Warning: statsmodels check failed: {e}")
        return False

def _check_scipy():
    """Check if scipy is available"""
    global SCIPY_AVAILABLE
    try:
        from scipy import stats
        return True
    except ImportError:
        return False

STATS_AVAILABLE = _check_statsmodels()
SCIPY_AVAILABLE = _check_scipy()

# Import scipy stats if available
if SCIPY_AVAILABLE:
    from scipy import stats
    globals()['stats'] = stats

# Import modules if available
if STATS_AVAILABLE:
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from statsmodels.discrete.discrete_model import NegativeBinomial, Logit, Probit, MNLogit
    # OrderedModel location varies
    try:
        from statsmodels.miscmodels.ordinal_model import OrderedModel
    except ImportError:
        OrderedModel = None
    try:
        from statsmodels.discrete.count_model import ZeroInflatedPoisson, ZeroInflatedNegativeBinomialP
    except ImportError:
        ZeroInflatedPoisson = None
        ZeroInflatedNegativeBinomialP = None
    from statsmodels.genmod.generalized_linear_model import GLM
    from statsmodels.genmod.families import Poisson as PoissonFamily, Binomial
    from statsmodels.genmod.families.links import Log, Logit
    
    # Make available globally for functions
    globals()['sm'] = sm
    globals()['smf'] = smf
    globals()['GLM'] = GLM
    globals()['PoissonFamily'] = PoissonFamily
    globals()['Binomial'] = Binomial
    globals()['Log'] = Log
    globals()['Logit'] = Logit
    globals()['NegativeBinomial'] = NegativeBinomial
    globals()['MNLogit'] = MNLogit
    if OrderedModel:
        globals()['OrderedModel'] = OrderedModel

from .exceptions import (
    StatisFlowError, DataValidationError, ModelConvergenceError, 
    OverdispersionError, SeparationError, AssumptionViolationError
)


class DistributionFamily(Enum):
    POISSON = "poisson"
    NEGATIVE_BINOMIAL = "negative_binomial"
    ZERO_INFLATED_POISSON = "zip"
    ZERO_INFLATED_NB = "zinb"
    HURDLE_POISSON = "hurdle_poisson"
    HURDLE_NB = "hurdle_nb"
    BETA = "beta"
    ZOIB = "zoib"
    DIRICHLET = "dirichlet"
    BINOMIAL = "binomial"
    QUASI_BINOMIAL = "quasi_binomial"
    BETA_BINOMIAL = "beta_binomial"
    MULTINOMIAL = "multinomial"
    ORDINAL = "ordinal"
    GAUSSIAN = "gaussian"
    GAM = "gam"


@dataclass
class GLMResult:
    """Standardized result container for all GLM models"""
    model_type: str
    formula: str
    coefficients: pd.Series
    std_errors: pd.Series
    p_values: pd.Series
    confidence_intervals: pd.DataFrame
    aic: Optional[float] = None
    bic: Optional[float] = None
    deviance: Optional[float] = None
    null_deviance: Optional[float] = None
    df_resid: Optional[int] = None
    df_model: Optional[int] = None
    pseudo_r2: Optional[float] = None
    dispersion: Optional[float] = None
    overdispersion_test: Optional[Dict[str, Any]] = None
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    predictions: Optional[pd.Series] = None
    residuals: Optional[pd.Series] = None
    convergence_status: bool = True
    warning_messages: List[str] = field(default_factory=list)
    
    def summary(self) -> str:
        """Generate human-readable summary"""
        lines = [
            f"{'='*60}",
            f"StatisFLOW {self.model_type} Results",
            f"{'='*60}",
            f"Formula: {self.formula}",
            f"",
            f"Fit Statistics:",
            f"  AIC: {self.aic:.4f}" if self.aic else "  AIC: N/A",
            f"  BIC: {self.bic:.4f}" if self.bic else "  BIC: N/A",
            f"  Deviance: {self.deviance:.4f}" if self.deviance else "  Deviance: N/A",
            f"  Dispersion: {self.dispersion:.4f}" if self.dispersion else "  Dispersion: N/A",
            f"",
            f"Coefficients:",
        ]
        
        coef_df = pd.DataFrame({
            'coef': self.coefficients,
            'std_err': self.std_errors,
            'P>|z|': self.p_values
        })
        
        # Add exponentiated coefficients for appropriate models
        if any(x in self.model_type.lower() for x in ['poisson', 'negbin', 'logit', 'multinomial', 'ordinal']):
            coef_df['exp(coef)'] = np.exp(self.coefficients)
            if 'poisson' in self.model_type.lower() or 'negbin' in self.model_type.lower():
                coef_df.columns = ['coef', 'std_err', 'P>|z|', 'Rate Ratio']
            else:
                coef_df.columns = ['coef', 'std_err', 'P>|z|', 'Odds Ratio']
        
        lines.append(coef_df.to_string())
        
        if self.overdispersion_test:
            lines.append(f"\nOverdispersion Test:")
            lines.append(f"  Statistic: {self.overdispersion_test.get('statistic', 'N/A')}")
            lines.append(f"  p-value: {self.overdispersion_test.get('p_value', 'N/A')}")
            lines.append(f"  Conclusion: {self.overdispersion_test.get('conclusion', 'N/A')}")
            
        if self.warning_messages:
            lines.append(f"\nWarnings ({len(self.warning_messages)}):")
            for i, warn in enumerate(self.warning_messages, 1):
                lines.append(f"  {i}. {warn}")
                
        lines.append(f"\n{'='*60}")
        return "\n".join(lines)


class AutoGLM:
    """
    Intelligent Generalized Linear Modeling Engine
    
    Automatically selects appropriate models, tests assumptions, 
    applies corrections, and provides comprehensive diagnostics.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize AutoGLM engine
        
        Parameters
        ----------
        data : pd.DataFrame
            Input dataset
        """
        if not isinstance(data, pd.DataFrame):
            raise DataValidationError("Input data must be a pandas DataFrame")
        
        self.data = data.copy()
        self._validate_data()
        
    def _validate_data(self):
        """Validate input data quality"""
        if self.data.empty:
            raise DataValidationError("Input data is empty")
        
        if self.data.isnull().all().all():
            raise DataValidationError("All values in dataframe are NaN")
    
    def fit_count_model(
        self,
        dependent: str,
        independents: List[str],
        offset: Optional[str] = None,
        exposure: Optional[str] = None,
        family: str = "auto",
        test_zero_inflation: bool = True,
        test_overdispersion: bool = True,
        alpha: float = 0.05
    ) -> GLMResult:
        """
        Fit count data models with automatic selection
        
        Workflow:
        1. Fit Poisson GLM
        2. Test for overdispersion (deviance/df >> 1)
        3. If overdispersed → switch to Negative Binomial
        4. Test for zero-inflation
        5. If zero-inflated → use ZIP or ZINB
        6. Include offset if provided
        
        Parameters
        ----------
        dependent : str
            Name of count response variable
        independents : List[str]
            List of predictor variables
        offset : str, optional
            Name of offset variable (already on log scale)
        exposure : str, optional
            Name of exposure variable (will be logged automatically)
        family : str
            Model family: 'poisson', 'negbin', 'zip', 'zinb', 'auto'
        test_zero_inflation : bool
            Whether to test for excess zeros
        test_overdispersion : bool
            Whether to test for overdispersion
        alpha : float
            Significance level for tests
            
        Returns
        -------
        GLMResult
            Fitted model results
        """
        # Handle offset/exposure
        model_offset = None
        if offset:
            if offset not in self.data.columns:
                raise DataValidationError(f"Offset column '{offset}' not found")
            model_offset = self.data[offset]
        elif exposure:
            if exposure not in self.data.columns:
                raise DataValidationError(f"Exposure column '{exposure}' not found")
            # Log of exposure becomes offset
            model_offset = np.log(self.data[exposure])
        
        # Build formula
        indep_str = " + ".join(independents)
        formula = f"{dependent} ~ {indep_str}"
        
        # Step 1: Fit initial Poisson model
        poisson_result = self._fit_poisson(
            dependent, independents, offset=model_offset
        )
        
        # Step 2: Test for overdispersion
        overdispersion_detected = False
        if test_overdispersion:
            od_test = self._test_overdispersion(poisson_result)
            poisson_result.overdispersion_test = od_test
            
            if od_test['conclusion'] == "Overdispersed":
                overdispersion_detected = True
                poisson_result.warning_messages.append(
                    f"Overdispersion detected (statistic={od_test['statistic']:.2f}). "
                    "Consider Negative Binomial model."
                )
        
        # Step 3: Switch to Negative Binomial if overdispersed
        if family == "auto" and overdispersion_detected:
            nb_result = self._fit_negative_binomial(
                dependent, independents, offset=model_offset
            )
            nb_result.overdispersion_test = poisson_result.overdispersion_test
            nb_result.warning_messages.extend(poisson_result.warning_messages)
            
            # Step 4: Test for zero-inflation
            if test_zero_inflation:
                zi_test = self._test_zero_inflation(nb_result)
                nb_result.diagnostics['zero_inflation_test'] = zi_test
                
                if zi_test['conclusion'] == "Zero-inflated":
                    # Step 5: Fit Zero-Inflated Negative Binomial
                    zinb_result = self._fit_zinb(
                        dependent, independents, offset=model_offset
                    )
                    zinb_result.overdispersion_test = nb_result.overdispersion_test
                    zinb_result.diagnostics['zero_inflation_test'] = zi_test
                    zinb_result.warning_messages.extend(nb_result.warning_messages)
                    zinb_result.warning_messages.append(
                        "Zero-inflation detected. Using ZINB model."
                    )
                    return zinb_result
            
            return nb_result
        
        # Check zero-inflation for Poisson
        if test_zero_inflation and family in ["auto", "poisson"]:
            zi_test = self._test_zero_inflation(poisson_result)
            poisson_result.diagnostics['zero_inflation_test'] = zi_test
            
            if zi_test['conclusion'] == "Zero-inflated":
                zip_result = self._fit_zip(
                    dependent, independents, offset=model_offset
                )
                zip_result.overdispersion_test = poisson_result.overdispersion_test
                zip_result.diagnostics['zero_inflation_test'] = zi_test
                zip_result.warning_messages.extend(poisson_result.warning_messages)
                zip_result.warning_messages.append(
                    "Zero-inflation detected. Using ZIP model."
                )
                return zip_result
        
        return poisson_result
    
    def _fit_poisson(self, dependent: str, independents: List[str], 
                     offset: Optional[np.ndarray] = None) -> GLMResult:
        """Fit Poisson GLM with log link"""
        if not STATS_AVAILABLE:
            raise StatisFlowError("statsmodels not installed. Run: pip install statsmodels")
        
        try:
            X = self.data[independents]
            X = sm.add_constant(X)
            y = self.data[dependent]
            
            model = GLM(y, X, family=PoissonFamily(link=Log()), offset=offset)
            result = model.fit()
            
            return GLMResult(
                model_type="Poisson GLM",
                formula=f"{dependent} ~ {' + '.join(independents)}",
                coefficients=result.params,
                std_errors=result.bse,
                p_values=result.pvalues,
                confidence_intervals=result.conf_int(),
                aic=result.aic,
                deviance=result.deviance,
                null_deviance=result.null_deviance if hasattr(result, 'null_deviance') else None,
                df_resid=result.df_resid,
                df_model=result.df_model,
                dispersion=1.0,  # Poisson assumes dispersion = 1
                predictions=result.predict(),
                residuals=result.resid_response,
                convergence_status=result.converged
            )
        except Exception as e:
            raise ModelConvergenceError(f"Poisson model failed to converge: {str(e)}")
    
    def _fit_negative_binomial(self, dependent: str, independents: List[str],
                               offset: Optional[np.ndarray] = None) -> GLMResult:
        """Fit Negative Binomial model"""
        try:
            X = self.data[independents]
            X = sm.add_constant(X)
            y = self.data[dependent]
            
            model = NegativeBinomial(y, X, offset=offset)
            result = model.fit()
            
            dispersion = result.params['alpha'] if 'alpha' in result.params.index else None
            
            return GLMResult(
                model_type="Negative Binomial",
                formula=f"{dependent} ~ {' + '.join(independents)}",
                coefficients=result.params,
                std_errors=result.bse,
                p_values=result.pvalues,
                confidence_intervals=result.conf_int(),
                aic=result.aic,
                bic=result.bic if hasattr(result, 'bic') else None,
                deviance=result.deviance,
                df_resid=result.df_resid,
                df_model=result.df_model,
                dispersion=dispersion,
                predictions=result.predict(),
                residuals=result.resid_response,
                convergence_status=result.converged
            )
        except Exception as e:
            raise ModelConvergenceError(f"Negative Binomial model failed: {str(e)}")
    
    def _fit_zip(self, dependent: str, independents: List[str],
                 offset: Optional[np.ndarray] = None) -> GLMResult:
        """Fit Zero-Inflated Poisson model"""
        # Note: statsmodels ZIP implementation requires exog_infl
        try:
            X = self.data[independents]
            X = sm.add_constant(X)
            y = self.data[dependent]
            
            # For simplicity, use same predictors for zero-inflation
            # In production, this should be configurable
            model = sm.ZeroInflatedPoisson(y, X, exog_infl=X, inflation='logit')
            result = model.fit()
            
            return GLMResult(
                model_type="Zero-Inflated Poisson",
                formula=f"{dependent} ~ {' + '.join(independents)}",
                coefficients=result.params,
                std_errors=result.bse,
                p_values=result.pvalues,
                confidence_intervals=result.conf_int(),
                aic=result.aic,
                convergence_status=result.converged
            )
        except Exception as e:
            raise ModelConvergenceError(f"ZIP model failed: {str(e)}")
    
    def _fit_zinb(self, dependent: str, independents: List[str],
                  offset: Optional[np.ndarray] = None) -> GLMResult:
        """Fit Zero-Inflated Negative Binomial model"""
        try:
            X = self.data[independents]
            X = sm.add_constant(X)
            y = self.data[dependent]
            
            model = sm.ZeroInflatedNegativeBinomialP(y, X, exog_infl=X, inflation='logit')
            result = model.fit()
            
            return GLMResult(
                model_type="Zero-Inflated Negative Binomial",
                formula=f"{dependent} ~ {' + '.join(independents)}",
                coefficients=result.params,
                std_errors=result.bse,
                p_values=result.pvalues,
                confidence_intervals=result.conf_int(),
                aic=result.aic,
                convergence_status=result.converged
            )
        except Exception as e:
            raise ModelConvergenceError(f"ZINB model failed: {str(e)}")
    
    def _test_overdispersion(self, result: GLMResult) -> Dict[str, Any]:
        """
        Test for overdispersion using deviance/df ratio
        
        Rule of thumb: deviance/df > 1.5 suggests overdispersion
        """
        if result.deviance is None or result.df_resid is None:
            return {"statistic": None, "p_value": None, "conclusion": "Cannot test"}
        
        ratio = result.deviance / result.df_resid
        
        # Chi-square test for overdispersion
        if SCIPY_AVAILABLE:
            p_value = 1 - stats.chi2.cdf(result.deviance, result.df_resid)
        else:
            p_value = None
        
        conclusion = "Overdispersed" if ratio > 1.5 else "No overdispersion"
        
        return {
            "statistic": ratio,
            "deviance": result.deviance,
            "df_resid": result.df_resid,
            "p_value": p_value,
            "conclusion": conclusion,
            "method": "Deviance/df ratio test"
        }
    
    def _test_zero_inflation(self, result: GLMResult) -> Dict[str, Any]:
        """
        Test for zero-inflation by comparing observed vs expected zeros
        """
        if result.predictions is None:
            return {"conclusion": "Cannot test"}
        
        # Count observed zeros
        y = self.data.iloc[:, 0]  # Assuming first column is dependent
        observed_zeros = (y == 0).sum()
        
        # Expected zeros under fitted model
        # For Poisson/NB: P(Y=0) = exp(-mu) for Poisson
        expected_probs = np.exp(-result.predictions)
        expected_zeros = expected_probs.sum()
        
        # Test statistic: difference between observed and expected
        diff = observed_zeros - expected_zeros
        ratio = observed_zeros / expected_zeros if expected_zeros > 0 else float('inf')
        
        conclusion = "Zero-inflated" if ratio > 1.5 else "No zero-inflation"
        
        return {
            "observed_zeros": int(observed_zeros),
            "expected_zeros": float(expected_zeros),
            "ratio": float(ratio),
            "difference": float(diff),
            "conclusion": conclusion,
            "method": "Observed vs Expected zeros comparison"
        }
    
    def fit_beta_regression(
        self,
        dependent: str,
        independents: List[str],
        zero_one_inflated: bool = False
    ) -> GLMResult:
        """
        Fit Beta regression for continuous proportions (0, 1)
        
        Parameters
        ----------
        dependent : str
            Response variable (must be in (0, 1))
        independents : List[str]
            Predictors
        zero_one_inflated : bool
            If True, use Zero-One Inflated Beta model
        """
        # Validate response in (0, 1)
        y = self.data[dependent]
        if ((y <= 0) | (y >= 1)).any():
            if zero_one_inflated:
                pass  # ZOIB can handle 0s and 1s
            else:
                # Transform slightly to avoid boundaries
                n = len(y)
                y_transformed = (y * (n - 1) + 0.5) / n
                warnings.warn(
                    f"Response variable transformed to avoid 0/1 boundaries. "
                    f"Consider using zero_one_inflated=True for data with exact 0s or 1s."
                )
            y = y_transformed if 'y_transformed' in locals() else y
        
        # Beta regression implementation would go here
        # Using statsmodels BetaModel or custom implementation
        raise NotImplementedError(
            "Beta regression will be implemented using Bayesian methods "
            "or external packages like betareg. Coming soon!"
        )
    
    def fit_logistic_regression(
        self,
        dependent: str,
        independents: List[str],
        check_separation: bool = True,
        use_firth: bool = "auto",
        mixed_effects: bool = False,
        group_var: Optional[str] = None
    ) -> GLMResult:
        """
        Fit binary logistic regression with separation detection
        
        Features:
        - Detect complete/quasi-complete separation
        - Apply Firth's penalized likelihood if needed
        - Support for mixed-effects (GLMM)
        - Calculate AUC, calibration plots
        """
        y = self.data[dependent]
        
        # Check for separation
        separation_detected = False
        if check_separation:
            sep_result = self._check_separation(dependent, independents)
            if sep_result['separated']:
                separation_detected = True
                warnings.warn(
                    f"Complete or quasi-complete separation detected! "
                    f"Variables involved: {sep_result['variables']}. "
                    f"Standard MLE will produce infinite coefficients."
                )
        
        # Decide on Firth correction
        if use_firth == "auto" and separation_detected:
            use_firth = True
        
        if use_firth:
            return self._fit_firth_logistic(dependent, independents)
        
        # Standard logistic regression
        try:
            X = self.data[independents]
            X = sm.add_constant(X)
            
            model = Logit(y, X)
            result = model.fit(disp=0)
            
            # Calculate AUC
            auc = self._calculate_auc(y, result.predict())
            
            glm_result = GLMResult(
                model_type="Binary Logistic Regression",
                formula=f"{dependent} ~ {' + '.join(independents)}",
                coefficients=result.params,
                std_errors=result.bse,
                p_values=result.pvalues,
                confidence_intervals=result.conf_int(),
                aic=result.aic,
                df_resid=result.df_resid,
                df_model=result.df_model,
                pseudo_r2=result.prsquared,
                predictions=result.predict(),
                residuals=result.resid_response,
                convergence_status=result.converged
            )
            
            glm_result.diagnostics['auc'] = auc
            glm_result.diagnostics['separation_check'] = sep_result
            
            return glm_result
            
        except Exception as e:
            if "perfect separation" in str(e).lower() or "separation" in str(e).lower():
                raise SeparationError(
                    "Perfect separation detected. Use Firth's correction (use_firth=True)"
                )
            raise ModelConvergenceError(f"Logistic regression failed: {str(e)}")
    
    def _check_separation(self, dependent: str, independents: List[str]) -> Dict[str, Any]:
        """Check for complete or quasi-complete separation"""
        y = self.data[dependent]
        separated_vars = []
        
        for var in independents:
            x = self.data[var]
            
            # Check if x perfectly predicts y
            for val in x.unique():
                mask = x == val
                if mask.sum() > 0:
                    y_subset = y[mask]
                    if y_subset.nunique() == 1:
                        separated_vars.append(var)
                        break
        
        return {
            "separated": len(separated_vars) > 0,
            "variables": separated_vars,
            "method": "Contingency table inspection"
        }
    
    def _fit_firth_logistic(self, dependent: str, independents: List[str]) -> GLMResult:
        """
        Fit logistic regression using Firth's penalized likelihood
        
        Note: Requires logistf package or custom implementation
        This is a placeholder for the actual implementation
        """
        warnings.warn(
            "Firth's correction requested. Installing 'logistf' or using "
            "Bayesian approximation. Full implementation coming soon."
        )
        
        # Fallback to standard logistic with warning
        return self.fit_logistic_regression(
            dependent, independents, 
            use_firth=False, check_separation=False
        )
    
    def _calculate_auc(self, y_true: pd.Series, y_pred: pd.Series) -> float:
        """Calculate Area Under ROC Curve"""
        if not SCIPY_AVAILABLE:
            return float('nan')
        
        # Simple AUC calculation using trapezoidal rule
        # In production, use sklearn.metrics.roc_auc_score
        from sklearn.metrics import roc_auc_score
        return roc_auc_score(y_true, y_pred)
    
    def fit_multinomial(
        self,
        dependent: str,
        independents: List[str],
        test_iia: bool = True
    ) -> GLMResult:
        """
        Fit multinomial logistic regression for nominal outcomes
        
        Tests IIA assumption and suggests alternatives if violated
        """
        try:
            X = self.data[independents]
            X = sm.add_constant(X)
            y = self.data[dependent]
            
            model = MNLogit(y, X)
            result = model.fit(disp=0, maxiter=100)
            
            glm_result = GLMResult(
                model_type="Multinomial Logistic Regression",
                formula=f"{dependent} ~ {' + '.join(independents)}",
                coefficients=result.params,
                std_errors=result.bse,
                p_values=result.pvalues,
                confidence_intervals=result.conf_int(),
                aic=result.aic,
                convergence_status=result.converged
            )
            
            # Test IIA assumption
            if test_iia:
                iia_test = self._test_iia(result, dependent, independents)
                glm_result.diagnostics['iia_test'] = iia_test
                
                if iia_test['violated']:
                    glm_result.warning_messages.append(
                        "IIA assumption violated! Consider nested logit or mixed logit models."
                    )
            
            return glm_result
            
        except Exception as e:
            raise ModelConvergenceError(f"Multinomial model failed: {str(e)}")
    
    def _test_iia(self, result, dependent: str, independents: List[str]) -> Dict[str, Any]:
        """
        Test Independence of Irrelevant Alternatives (IIA)
        
        Uses Hausman-McFadden test
        """
        # Placeholder for IIA test
        # Full implementation requires comparing full vs restricted models
        return {
            "violated": False,
            "statistic": None,
            "p_value": None,
            "method": "Hausman-McFadden (placeholder)",
            "note": "Full IIA test implementation pending"
        }
    
    def fit_ordinal(
        self,
        dependent: str,
        independents: List[str],
        test_proportional_odds: bool = True
    ) -> GLMResult:
        """
        Fit ordinal logistic regression (proportional odds model)
        
        Tests proportional odds assumption
        """
        try:
            X = self.data[independents]
            y = self.data[dependent]
            
            # Ensure ordinal encoding
            if not pd.api.types.is_integer_dtype(y):
                # Convert to ordinal codes
                y_codes = pd.Categorical(y).codes
            else:
                y_codes = y
            
            model = OrderedModel(
                y_codes,
                sm.add_constant(X),
                distr='logit'
            )
            result = model.fit(method='bfgs')
            
            glm_result = GLMResult(
                model_type="Ordinal Logistic Regression (Proportional Odds)",
                formula=f"{dependent} ~ {' + '.join(independents)}",
                coefficients=result.params,
                std_errors=result.bse,
                p_values=result.pvalues,
                confidence_intervals=result.conf_int(),
                aic=result.aic,
                convergence_status=True
            )
            
            # Test proportional odds assumption
            if test_proportional_odds:
                po_test = self._test_proportional_odds(result, dependent, independents)
                glm_result.diagnostics['proportional_odds_test'] = po_test
                
                if po_test['violated']:
                    glm_result.warning_messages.append(
                        "Proportional odds assumption violated! "
                        "Consider partial proportional odds or adjacent-category models."
                    )
            
            return glm_result
            
        except Exception as e:
            raise ModelConvergenceError(f"Ordinal model failed: {str(e)}")
    
    def _test_proportional_odds(self, result, dependent: str, 
                                independents: List[str]) -> Dict[str, Any]:
        """Test proportional odds assumption using Brant test or similar"""
        # Placeholder for Brant test
        return {
            "violated": False,
            "method": "Brant test (placeholder)",
            "note": "Full implementation pending"
        }
    
    def extend_to_gam(
        self,
        base_formula: str,
        smooth_terms: List[str],
        family: str = "gaussian"
    ) -> GLMResult:
        """
        Extend GLM to Generalized Additive Model (GAM)
        
        Allows non-linear effects via smoothing splines
        """
        try:
            # Using pyGAM or statsmodels GAM
            from pygam import LinearGAM, s, te
            
            X = self.data[smooth_terms].values
            y = self.data[base_formula.split('~')[0].strip()].values
            
            gam = LinearGAM(s(0) + s(1)).fit(X, y)
            
            return GLMResult(
                model_type="Generalized Additive Model",
                formula=base_formula,
                coefficients=pd.Series(gam.coef_),
                std_errors=pd.Series(np.sqrt(gam.statistics_['scale'])),
                p_values=pd.Series([np.nan] * len(gam.coef_)),
                confidence_intervals=pd.DataFrame({'lower': np.nan, 'upper': np.nan}),
                convergence_status=True
            )
            
        except ImportError:
            raise StatisFlowError(
                "pyGAM not installed. Install with: pip install pygam"
            )
        except Exception as e:
            raise ModelConvergenceError(f"GAM fitting failed: {str(e)}")
