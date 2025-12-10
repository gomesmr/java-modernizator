"""
Repository cloning step
"""
from domain.entities import StepResult
from infrastructure.stackspot_action_runner import StackspotActionRunner


class CloneStep:
    """Handles repository cloning"""

    def __init__(self, wsl_enabled: bool = False):
        self.wsl_enabled = wsl_enabled

    def execute(self) -> StepResult:
        """
        Execute repository cloning

        Returns:
            StepResult with cloned repository path
        """
        print("\n" + "🔄 STEP 1: Cloning Repository".center(60, "="))

        try:
            action_runner = StackspotActionRunner(wsl_enabled=self.wsl_enabled)
            repo_path = action_runner.clone_repository()

            return StepResult(
                success=True,
                data=repo_path,
                metadata={'repo_path': repo_path}
            )

        except Exception as e:
            error_msg = f"Failed to clone repository: {e}"
            print(f"❌ {error_msg}")
            return StepResult(success=False, error=error_msg)