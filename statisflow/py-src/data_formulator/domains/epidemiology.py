"""
Epidemiology Module for StatisFLOW
Survival analysis, meta-analysis, infectious disease modeling
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class SurvivalResult:
    """Survival analysis results"""
    median_survival: float
    survival_curve: Dict[str, List]
    hazard_ratio: Optional[float]
    log_rank_p: Optional[float]
    cox_coefficients: Optional[Dict[str, float]]


class EpidemiologyModule:
    """
    Comprehensive epidemiology analytics toolkit.
    
    Features:
    - Survival analysis (Kaplan-Meier, Cox PH)
    - Meta-analysis (fixed/random effects)
    - Infectious disease modeling (SIR, SEIR)
    - Case-control analysis
    - Incidence/prevalence calculations
    """
    
    def kaplan_meier(self, df: pd.DataFrame,
                    time_col: str,
                    event_col: str,
                    group_col: Optional[str] = None) -> Dict[str, Any]:
        """
        Kaplan-Meier survival estimation.
        
        Parameters
        ----------
        df : pd.DataFrame
            Survival data
        time_col : str
            Time-to-event column
        event_col : str
            Event indicator (1=event, 0=censored)
        group_col : str, optional
            Grouping variable for comparison
            
        Returns
        -------
        dict
            Survival curves and statistics
        """
        times = df[time_col].values
        events = df[event_col].values
        
        if group_col:
            groups = df[group_col].unique()
            results = {}
            
            for group in groups:
                mask = df[group_col] == group
                km = self._km_estimate(times[mask], events[mask])
                results[str(group)] = km
            
            # Log-rank test if two groups
            log_rank_p = None
            if len(groups) == 2:
                log_rank_p = self._log_rank_test(
                    times[df[group_col] == groups[0]],
                    events[df[group_col] == groups[0]],
                    times[df[group_col] == groups[1]],
                    events[df[group_col] == groups[1]]
                )
            
            return {
                "survival_curves": results,
                "log_rank_p_value": log_rank_p,
                "groups": list(str(g) for g in groups)
            }
        else:
            km = self._km_estimate(times, events)
            return {
                "survival_curve": km,
                "median_survival": self._median_survival(km['times'], km['survival'])
            }
    
    def _km_estimate(self, times: np.ndarray, events: np.ndarray) -> Dict[str, List]:
        """Calculate Kaplan-Meier estimate"""
        # Sort by time
        order = np.argsort(times)
        times_sorted = times[order]
        events_sorted = events[order]
        
        n = len(times)
        at_risk = n
        survival = 1.0
        
        times_list = [0]
        survival_list = [1.0]
        
        i = 0
        while i < n:
            current_time = times_sorted[i]
            
            # Count events and censored at this time
            event_count = 0
            censored_count = 0
            
            while i < n and times_sorted[i] == current_time:
                if events_sorted[i] == 1:
                    event_count += 1
                else:
                    censored_count += 1
                i += 1
            
            # Update survival probability
            if event_count > 0:
                survival *= (at_risk - event_count) / at_risk
            
            times_list.append(current_time)
            survival_list.append(survival)
            
            at_risk -= (event_count + censored_count)
        
        return {
            "times": times_list,
            "survival": survival_list,
            "at_risk": list(range(n, -1, -1))[:len(times_list)]
        }
    
    def _median_survival(self, times: List, survival: List) -> Optional[float]:
        """Find median survival time"""
        for t, s in zip(times, survival):
            if s <= 0.5:
                return float(t)
        return None
    
    def _log_rank_test(self, t1, e1, t2, e2) -> float:
        """Log-rank test for comparing survival curves"""
        from scipy import stats
        
        # Simplified log-rank implementation
        all_times = np.concatenate([t1, t2])
        unique_times = np.unique(all_times)
        
        O1, E1 = 0, 0
        
        for time in unique_times:
            n1 = np.sum(t1 >= time)
            n2 = np.sum(t2 >= time)
            d1 = np.sum((t1 == time) & (e1 == 1))
            d2 = np.sum((t2 == time) & (e2 == 1))
            
            n = n1 + n2
            d = d1 + d2
            
            if n > 0:
                E1 += n1 * d / n
                O1 += d1
        
        # Chi-square statistic
        if E1 > 0:
            chi2 = (O1 - E1) ** 2 / E1
            p_val = 1 - stats.chi2.cdf(chi2, 1)
        else:
            p_val = 1.0
        
        return float(p_val)
    
    def cox_proportional_hazards(self, df: pd.DataFrame,
                                 time_col: str,
                                 event_col: str,
                                 covariates: List[str]) -> Dict[str, Any]:
        """
        Cox proportional hazards model.
        
        Parameters
        ----------
        df : pd.DataFrame
            Survival data with covariates
        time_col : str
            Time-to-event column
        event_col : str
            Event indicator
        covariates : list
            Predictor variables
            
        Returns
        -------
        dict
            Model coefficients and statistics
        """
        from sklearn.linear_model import LogisticRegression
        
        # Simplified Cox using logistic approximation
        data = df[[time_col, event_col] + covariates].dropna()
        
        X = data[covariates].values
        y = data[event_col].values
        
        # Fit logistic regression as approximation
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        
        coefficients = dict(zip(covariates, model.coef_[0].tolist()))
        hazard_ratios = {k: np.exp(v) for k, v in coefficients.items()}
        
        return {
            "coefficients": coefficients,
            "hazard_ratios": hazard_ratios,
            "concordance": float(model.score(X, y)),
            "n_events": int(y.sum()),
            "n_observations": len(y)
        }
    
    def meta_analysis(self, studies: List[Dict[str, Any]],
                     effect_measure: str = 'or') -> Dict[str, Any]:
        """
        Meta-analysis with fixed and random effects.
        
        Parameters
        ----------
        studies : list
            List of study data with effect sizes and SEs
        effect_measure : str
            Effect measure (or, rr, md, smd)
            
        Returns
        -------
        dict
            Pooled effect estimates
        """
        # Extract effect sizes and standard errors
        effects = []
        ses = []
        
        for study in studies:
            if 'effect_size' in study and 'se' in study:
                effects.append(study['effect_size'])
                ses.append(study['se'])
        
        if len(effects) == 0:
            return {"error": "No valid studies provided"}
        
        effects = np.array(effects)
        ses = np.array(ses)
        
        # Fixed effects (inverse variance weighted)
        weights = 1 / (ses ** 2 + 1e-10)
        fe_effect = np.sum(weights * effects) / np.sum(weights)
        fe_se = np.sqrt(1 / np.sum(weights))
        fe_ci = (fe_effect - 1.96 * fe_se, fe_effect + 1.96 * fe_se)
        
        # Random effects (DerSimonian-Laird)
        Q = np.sum(weights * (effects - fe_effect) ** 2)
        df = len(effects) - 1
        
        if Q > df:
            tau2 = (Q - df) / (np.sum(weights) - np.sum(weights ** 2) / np.sum(weights) + 1e-10)
            tau2 = max(0, tau2)
        else:
            tau2 = 0
        
        re_weights = 1 / (ses ** 2 + tau2 + 1e-10)
        re_effect = np.sum(re_weights * effects) / np.sum(re_weights)
        re_se = np.sqrt(1 / np.sum(re_weights))
        re_ci = (re_effect - 1.96 * re_se, re_effect + 1.96 * re_se)
        
        # Heterogeneity
        I2 = max(0, (Q - df) / Q * 100) if Q > 0 else 0
        
        return {
            "fixed_effects": {
                "estimate": float(fe_effect),
                "se": float(fe_se),
                "ci": list(fe_ci)
            },
            "random_effects": {
                "estimate": float(re_effect),
                "se": float(re_se),
                "ci": list(re_ci),
                "tau_squared": float(tau2)
            },
            "heterogeneity": {
                "Q_statistic": float(Q),
                "I_squared": float(I2),
                "n_studies": len(effects)
            },
            "effect_measure": effect_measure
        }
    
    def sir_model(self, df: pd.DataFrame,
                 time_col: str,
                 cases_col: str,
                 population: int,
                 initial_infected: int = 1) -> Dict[str, Any]:
        """
        SIR (Susceptible-Infected-Recovered) epidemic model fitting.
        
        Parameters
        ----------
        df : pd.DataFrame
            Time series of case counts
        time_col : str
            Time column
        cases_col : str
            New cases column
        population : int
            Total population size
        initial_infected : int
            Initial number of infected
            
        Returns
        -------
        dict
            Estimated R0 and model fit
        """
        from scipy.optimize import minimize
        
        times = df[time_col].values
        cases = df[cases_col].values
        
        def sir_ode(y, beta, gamma):
            S, I, R = y
            dS = -beta * S * I / population
            dI = beta * S * I / population - gamma * I
            dR = gamma * I
            return np.array([dS, dI, dR])
        
        def simulate_sir(params):
            beta, gamma = params
            S, I, R = population - initial_infected, initial_infected, 0
            simulated = []
            
            for _ in range(len(times)):
                simulated.append(I)
                dy = sir_ode([S, I, R], beta, gamma)
                S += dy[0]
                I += dy[1]
                R += dy[2]
            
            return np.array(simulated)
        
        def loss(params):
            simulated = simulate_sir(params)
            return np.sum((simulated - cases) ** 2)
        
        # Optimize
        result = minimize(loss, [0.3, 0.1], bounds=[(0.01, 1), (0.01, 0.5)])
        
        beta, gamma = result.x
        R0 = beta / gamma
        
        return {
            "R0": float(R0),
            "beta": float(beta),
            "gamma": float(gamma),
            "recovery_time_days": float(1/gamma) if gamma > 0 else None,
            "peak_infected": int(max(simulate_sir([beta, gamma]))),
            "fit_quality": float(1 - result.fun / np.sum(cases ** 2))
        }
    
    def calculate_incidence_prevalence(self, df: pd.DataFrame,
                                      population: int,
                                      time_period: float) -> Dict[str, float]:
        """
        Calculate incidence and prevalence rates.
        
        Parameters
        ----------
        df : pd.DataFrame
            Data with case information
        population : int
            Population at risk
        time_period : float
            Time period in years
            
        Returns
        -------
        dict
            Incidence and prevalence rates
        """
        # Incident cases (new cases during period)
        incident_cases = df.get('incident', pd.Series([0])).sum()
        
        # Prevalent cases (existing cases at point in time)
        prevalent_cases = df.get('prevalent', pd.Series([0])).sum()
        
        # Rates per 100,000
        incidence_rate = (incident_cases / population) * 100000 / time_period
        prevalence = (prevalent_cases / population) * 100000
        
        return {
            "incidence_rate_per_100k": float(incidence_rate),
            "prevalence_per_100k": float(prevalence),
            "incident_cases": int(incident_cases),
            "prevalent_cases": int(prevalent_cases),
            "population": population,
            "time_period_years": time_period
        }
