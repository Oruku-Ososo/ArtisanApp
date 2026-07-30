"""
StatisFLOW Exception Hierarchy
Production-grade error handling with context tracking
"""

from typing import Optional, Dict, Any
import traceback
from datetime import datetime


class StatisFlowError(Exception):
    """Base exception for all StatisFLOW errors"""
    
    def __init__(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.utcnow().isoformat()
        self.traceback = traceback.format_exc() if original_exception else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize error for API responses"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp,
            "has_traceback": self.traceback is not None
        }


class DataValidationError(StatisFlowError):
    """Raised when data validation fails"""
    pass


class ModelConvergenceError(StatisFlowError):
    """Raised when statistical model fails to converge"""
    pass


class OverdispersionError(StatisFlowError):
    """Raised when overdispersion detected and no suitable model found"""
    pass


class SeparationError(StatisFlowError):
    """Raised when complete/quasi-complete separation detected in logistic regression"""
    pass


class AssumptionViolationError(StatisFlowError):
    """Raised when statistical assumptions are violated"""
    pass


class ConfigurationError(StatisFlowError):
    """Raised when configuration is invalid"""
    pass


class VisualizationError(StatisFlowError):
    """Raised when visualization rendering fails"""
    pass


class ImportDependencyError(StatisFlowError):
    """Raised when required dependency is missing"""
    
    def __init__(self, package_name: str, install_command: Optional[str] = None):
        msg = f"Required package '{package_name}' is not installed"
        if install_command:
            msg += f". Install with: {install_command}"
        super().__init__(msg, context={"package": package_name})
