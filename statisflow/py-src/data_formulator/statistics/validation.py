"""StatisFLOW Statistics Module - Data Validation"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np


@dataclass
class DataQualityReport:
    """Comprehensive data quality report."""
    total_rows: int
    total_columns: int
    missing_values: Dict[str, int]
    duplicate_rows: int
    constant_columns: List[str]
    high_cardinality_columns: List[str]
    outliers_detected: Dict[str, int]
    quality_score: float  # 0-100


def validate_dataframe(df: pd.DataFrame) -> DataQualityReport:
    """Generate a comprehensive data quality report."""
    # Missing values
    missing = df.isna().sum().to_dict()
    
    # Duplicates
    duplicates = df.duplicated().sum()
    
    # Constant columns
    constant = [col for col in df.columns if df[col].nunique() == 1]
    
    # High cardinality (more than 50% unique)
    high_card = [col for col in df.columns 
                 if df[col].nunique() / len(df) > 0.5 and df[col].dtype == 'object']
    
    # Simple outlier detection (values beyond 3 std)
    outliers = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        mean = df[col].mean()
        std = df[col].std()
        if std > 0:
            outlier_count = ((df[col] < mean - 3*std) | (df[col] > mean + 3*std)).sum()
            if outlier_count > 0:
                outliers[col] = int(outlier_count)
    
    # Quality score (simple heuristic)
    missing_penalty = sum(missing.values()) / (len(df) * len(df.columns)) * 100
    duplicate_penalty = duplicates / len(df) * 50
    score = max(0, 100 - missing_penalty - duplicate_penalty)
    
    return DataQualityReport(
        total_rows=len(df),
        total_columns=len(df.columns),
        missing_values=missing,
        duplicate_rows=int(duplicates),
        constant_columns=constant,
        high_cardinality_columns=high_card,
        outliers_detected=outliers,
        quality_score=round(score, 2)
    )
