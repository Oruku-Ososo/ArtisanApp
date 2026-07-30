"""StatisFLOW Statistics Module - Exception Hierarchy"""


class StatisFlowError(Exception):
    """Base exception for all StatisFLOW errors."""
    def __init__(self, message: str, correlation_id: str = None):
        self.message = message
        self.correlation_id = correlation_id or "unknown"
        super().__init__(self.message)


class DataValidationError(StatisFlowError):
    """Raised when data validation fails."""
    pass


class SchemaMismatchError(StatisFlowError):
    """Raised when data doesn't match expected schema."""
    pass


class ModelConvergenceError(StatisFlowError):
    """Raised when statistical model fails to converge."""
    pass


class AssumptionViolationError(StatisFlowError):
    """Raised when statistical assumptions are violated."""
    pass


class OverdispersionError(StatisFlowError):
    """Raised when overdispersion is detected in count/binomial models."""
    pass


class SeparationError(StatisFlowError):
    """Raised when complete/quasi-complete separation is detected in logistic regression."""
    pass
