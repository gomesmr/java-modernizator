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

"""
Execution result models
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class StepResult:
    """Result of a single execution step"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_error(self) -> bool:
        """Check if step has error"""
        return self.error is not None


@dataclass
class ExecutionResult:
    """Complete execution result"""
    execution_id: Optional[str] = None
    cloned_repo_path: Optional[str] = None
    payload_file: Optional[str] = None
    callback_file: Optional[str] = None
    results_directory: Optional[str] = None
    success: bool = False
    error: Optional[str] = None

    def add_step_result(self, step_name: str, result: StepResult) -> None:
        """Add a step result to execution"""
        if not result.success:
            self.success = False
            self.error = f"{step_name}: {result.error}"