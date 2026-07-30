"""StatisFLOW Statistics Module Initialization"""
from .exceptions import (
    StatisFlowError,
    DataValidationError,
    SchemaMismatchError,
    ModelConvergenceError,
    AssumptionViolationError,
    OverdispersionError,
    SeparationError
)
from .validation import validate_dataframe, DataQualityReport

__all__ = [
    # Exceptions
    "StatisFlowError",
    "DataValidationError",
    "SchemaMismatchError",
    "ModelConvergenceError",
    "AssumptionViolationError",
    "OverdispersionError",
    "SeparationError",
    # Validation
    "validate_dataframe",
    "DataQualityReport"
]
