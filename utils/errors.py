"""Custom exception classes for the application."""

import logging


logger = logging.getLogger(__name__)


class FinanceManagerException(Exception):
    """Base exception for Finance Manager."""
    
    def __init__(self, message: str):
        """Initialize custom exception."""
        self.message = message
        logger.error(f"{self.__class__.__name__}: {message}")
        super().__init__(self.message)


class ValidationError(FinanceManagerException):
    """Raised when validation fails."""
    pass


class StorageError(FinanceManagerException):
    """Raised when storage operations fail."""
    pass


class TransactionError(FinanceManagerException):
    """Raised when transaction operations fail."""
    pass


class BudgetError(FinanceManagerException):
    """Raised when budget operations fail."""
    pass


class AnalysisError(FinanceManagerException):
    """Raised when financial analysis fails."""
    pass
