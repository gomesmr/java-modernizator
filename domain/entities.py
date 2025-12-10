"""
Domain entities for Java modernization
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class JavaFile:
    """Represents a Java source file"""
    absolute_path: str
    relative_path: str
    filename: str
    content: str
    size_in_bytes: int

    @property
    def is_valid(self) -> bool:
        """Check if file has valid content"""
        return bool(self.content and self.content.strip())


@dataclass
class ModernizationResult:
    """Result of a file modernization operation"""
    file_path: str
    is_successful: bool
    execution_id: Optional[str] = None
    error_message: Optional[str] = None
    original_content: Optional[str] = None
    modernized_content: Optional[str] = None

    @property
    def has_changes(self) -> bool:
        """Check if modernization produced changes"""
        return (
            self.is_successful and
            self.modernized_content is not None and
            self.original_content != self.modernized_content
        )