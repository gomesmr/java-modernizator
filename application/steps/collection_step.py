"""
File collection step
"""
from domain.entities import StepResult
from infrastructure.file_collector import FileCollectorService
from config.settings import settings


class CollectionStep:
    """Handles file collection and payload generation"""

    def __init__(self):
        self.file_collector = FileCollectorService()

    def execute(self, cloned_repo_path: str) -> StepResult:
        """
        Execute file collection

        Args:
            cloned_repo_path: Path to cloned repository

        Returns:
            StepResult with payload file path
        """
        print("\n" + "📄 STEP 2: Collecting Files".center(60, "="))

        try:
            payload_file = self.file_collector.generate_payload_file(
                cloned_repo_path=cloned_repo_path,
                paths_file_path=str(settings.MAIN_PATHS_FILE),
                output_file_path=str(settings.MAIN_PAYLOAD_FILE)
            )

            return StepResult(
                success=True,
                data=payload_file,
                metadata={'payload_file': payload_file}
            )

        except Exception as e:
            error_msg = f"Failed to collect files: {e}"
            print(f"❌ {error_msg}")
            return StepResult(success=False, error=error_msg)