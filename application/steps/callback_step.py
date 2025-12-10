"""
Callback fetching step
"""
import json
from pathlib import Path

from domain.entities import StepResult
from infrastructure.stackspot_client import StackspotApiClient
from config.settings import settings


class CallbackStep:
    """Handles callback result fetching"""

    def __init__(self):
        self.api_client = StackspotApiClient(str(settings.CREDENTIALS_PATH))
        self.output_dir = settings.PROJECT_ROOT / "assets"

    def execute(self, execution_id: str) -> StepResult:
        """
        Execute callback fetching

        Args:
            execution_id: Execution ID from StackSpot processing

        Returns:
            StepResult with callback data and file paths
        """
        print("\n" + "📞 STEP 4: Fetching Callback Result".center(60, "="))

        try:
            # Get callback result
            callback_result = self.api_client.get_callback_result(execution_id)

            if not callback_result:
                return StepResult(
                    success=False,
                    error='Callback result not available'
                )

            # Save callback results
            callback_file, pretty_file = self._save_callback_results(callback_result)

            return StepResult(
                success=True,
                data={
                    'callback_result': callback_result,
                    'callback_file': str(callback_file),
                    'pretty_file': str(pretty_file)
                },
                metadata={
                    'callback_file': str(callback_file),
                    'pretty_file': str(pretty_file)
                }
            )

        except Exception as e:
            error_msg = f"Failed to fetch callback: {e}"
            print(f"❌ {error_msg}")
            return StepResult(success=False, error=error_msg)

    def _save_callback_results(self, callback_result: dict) -> tuple[Path, Path]:
        """Save callback results to files"""
        self.output_dir.mkdir(exist_ok=True)

        # Save compact version
        callback_file = self.output_dir / "callback-result.json"
        with open(callback_file, 'w', encoding='utf-8') as f:
            json.dump(callback_result, f, indent=2, ensure_ascii=False)
        print(f"💾 Callback result saved to: {callback_file}")

        # Save pretty version
        pretty_file = self.output_dir / "callback-result-pretty.json"
        with open(pretty_file, 'w', encoding='utf-8') as f:
            json.dump(callback_result, f, indent=4, ensure_ascii=False)
        print(f"📄 Pretty version saved to: {pretty_file}")

        return callback_file, pretty_file