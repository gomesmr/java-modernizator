# infrastructure/stackspot_action_runner.py
"""
Runner for StackSpot Actions via STK CLI
"""
import subprocess
from pathlib import Path
from typing import Optional, Dict
from domain.exceptions import StackspotApiError
from config.settings import settings


class StackspotActionRunner:
    """Execute StackSpot Actions using STK CLI"""

    def __init__(self, wsl_enabled: bool = True):
        self.wsl_enabled = wsl_enabled
        self._validate_stk_cli()

    def _validate_stk_cli(self) -> None:
        """Validate STK CLI is available"""
        try:
            if self.wsl_enabled:
                # Use bash -c para executar o comando no WSL
                cmd = ['wsl', 'bash', '-c', 'stk --version']
            else:
                cmd = ['stk', '--version']

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ STK CLI found: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error output: {e.stderr}")
            raise StackspotApiError(
                "STK CLI not found or not accessible. Please install it first."
            )

    def _build_wsl_command(self, cmd: list) -> list:
        """Build command for WSL execution"""
        # Converte lista de comandos em string para bash -c
        cmd_str = ' '.join(cmd)
        return ['wsl', 'bash', '-c', cmd_str]

    def _normalize_wsl_path(self, path: str) -> str:
        """Normalize WSL path format"""
        # \\wsl.localhost\Ubuntu_Zup\home\... -> /home/...
        if path.startswith('\\\\wsl.localhost\\'):
            parts = path.split('\\')
            # Remove \\wsl.localhost\Ubuntu_Zup
            return '/' + '/'.join(parts[3:])
        return path

    def run_action(
            self,
            action_path: str,
            inputs: Dict[str, str],
            working_dir: Optional[str] = None
    ) -> Dict:
        """
        Run a StackSpot Action

        Args:
            action_path: Path to action directory (Windows or WSL)
            inputs: Dictionary of input values for the action
            working_dir: Directory where action should be executed

        Returns:
            Dictionary with execution results
        """
        print(f"\n{'=' * 60}")
        print(f"🚀 Running StackSpot Action")
        print(f"{'=' * 60}")

        # Normalize action path for WSL
        if self.wsl_enabled:
            action_path = self._normalize_wsl_path(action_path)

        print(f"📁 Action Path: {action_path}")
        print(f"📂 Working Dir: {working_dir or 'current'}")

        # Build inputs string
        inputs_str = ' '.join([
            f'--input {key}="{value}"'
            for key, value in inputs.items()
        ])

        print(f"🔧 Inputs:")
        for key, value in inputs.items():
            # Mask sensitive data
            display_value = value if key != 'git_token' else '***'
            print(f"   {key}: {display_value}")

        try:
            if self.wsl_enabled:
                # Build complete command for WSL
                full_cmd = f'cd {action_path} && stk run action . {inputs_str}'
                print(f"\n🔧 Command: {full_cmd}")

                result = subprocess.run(
                    ['wsl', 'bash', '-c', full_cmd],
                    capture_output=True,
                    text=True,
                    check=True
                )
            else:
                # For non-WSL execution
                cmd = ['stk', 'run', 'action', '.']
                for key, value in inputs.items():
                    cmd.extend(['--input', f'{key}={value}'])

                result = subprocess.run(
                    cmd,
                    cwd=action_path,
                    capture_output=True,
                    text=True,
                    check=True
                )

            print(f"✅ Action executed successfully")
            print(f"\n📄 Output:\n{result.stdout}")

            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }

        except subprocess.CalledProcessError as e:
            print(f"❌ Action failed: {e}")
            print(f"📄 Error output:\n{e.stderr}")
            raise StackspotApiError(
                f"Failed to run action: {e.stderr}"
            )

    def clone_repository(self) -> str:
        """
        Clone repository using fixed configuration from settings

        Returns:
            Path to cloned repository
        """
        print("\n" + "🔄 Cloning Repository".center(60, "="))

        # Get configuration from settings
        repo_url = settings.GIT_REPO_URL
        target_dir = settings.GIT_CLONE_TARGET
        git_token = settings.get_git_token()

        print(f"📦 Repository: {repo_url}")
        print(f"📁 Target: {target_dir}")

        # Prepare inputs for the action
        inputs = {
            'repository_path': repo_url,
            'git_token': git_token,
            'workdir': target_dir
        }

        try:
            # Execute clone action
            result = self.run_action(
                action_path=settings.CLONE_ACTION_PATH,
                inputs=inputs
            )

            print(f"✅ Repository cloned successfully to: {target_dir}")
            return target_dir

        except Exception as e:
            print(f"❌ Failed to clone repository: {e}")
            raise