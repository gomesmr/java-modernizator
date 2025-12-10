"""
StackSpot AI processing step
"""
from domain.entities import StepResult
from infrastructure.stackspot_client import StackspotApiClient
from config.settings import settings


class ProcessingStep:
    """Handles StackSpot AI processing"""

    def __init__(self):
        self.api_client = StackspotApiClient(str(settings.CREDENTIALS_PATH))

    def execute(self, payload_file: str) -> StepResult:
        """
        Execute StackSpot processing

        Args:
            payload_file: Path to payload file

        Returns:
            StepResult with execution ID and result
        """
        print("\n" + "🤖 STEP 3: Processing with StackSpot AI".center(60, "="))

        try:
            # Read payload content
            payload_content = self._read_payload(payload_file)

            # Execute quick command
            print(f"🚀 Executing quick command: {settings.QUICK_COMMAND_SLUG}")
            execution_id = self.api_client.execute_quick_command(
                settings.QUICK_COMMAND_SLUG,
                payload_content
            )

            # Poll for results
            print(f"⏳ Polling for results...")
            result = self.api_client.poll_execution_result(execution_id)

            return StepResult(
                success=result is not None,
                data={'execution_id': execution_id, 'result': result},
                metadata={'execution_id': execution_id}
            )

        except Exception as e:
            error_msg = f"Failed to process with StackSpot: {e}"
            print(f"❌ {error_msg}")
            return StepResult(success=False, error=error_msg)

    @staticmethod
    def _read_payload(payload_file: str) -> str:
        """Read payload file content"""
        with open(payload_file, 'r', encoding='utf-8') as f:
            return f.read()