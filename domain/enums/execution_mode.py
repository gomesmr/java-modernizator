"""
Execution mode enumeration
"""
from enum import Enum


class ExecutionMode(Enum):
    """Defines the execution mode for the application"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"

    @property
    def is_dev(self) -> bool:
        """Check if mode is development"""
        return self == ExecutionMode.DEVELOPMENT

    @property
    def is_prod(self) -> bool:
        """Check if mode is production"""
        return self == ExecutionMode.PRODUCTION