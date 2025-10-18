class DomainError(Exception):
    """
    Base exception for all domain errors
    """

class ValidationError(DomainError):
    """
    Exception raised when invalid parameters are provided
    """
