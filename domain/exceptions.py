"""
Custom exceptions for the modernization domain
"""


class ModernizationError(Exception):
    """Base exception for modernization errors"""
    pass


class CredentialsNotFoundError(ModernizationError):
    """Raised when credentials file is not found"""
    pass


class InvalidDirectoryError(ModernizationError):
    """Raised when directory is invalid"""
    pass


class StackspotApiError(ModernizationError):
    """Raised when Stackspot API fails"""
    pass


class FileProcessingError(ModernizationError):
    """Raised when file processing fails"""
    pass

class RQCExecutionTimeoutError(ModernizationError):
    """Raised when file processing fails"""
    pass