"""
Setup validation logic
"""
from pathlib import Path
from typing import List

from config.settings import settings


class SetupValidator:
    """Validates application setup and requirements"""

    def __init__(self):
        self.errors: List[str] = []

    def validate(self) -> bool:
        """
        Validate all requirements

        Returns:
            True if validation passes, False otherwise
        """
        self._validate_credentials()
        self._validate_git_token()
        self._validate_paths_file()
        return len(self.errors) == 0

    def _validate_credentials(self) -> None:
        """Validate credentials file exists"""
        if not settings.CREDENTIALS_PATH.exists():
            self.errors.append(
                f"❌ Credentials file not found: {settings.CREDENTIALS_PATH}\n"
                f"   Create it from: {settings.PROJECT_ROOT / 'secrets-example.json'}"
            )

    def _validate_git_token(self) -> None:
        """Validate git token exists in credentials"""
        try:
            git_token = settings.get_git_token()
            if not git_token:
                self.errors.append(
                    f"❌ Git token not found in credentials file\n"
                    f"   Add 'git_token' to: {settings.CREDENTIALS_PATH}"
                )
        except Exception as e:
            self.errors.append(f"❌ Error loading credentials: {e}")

    def _validate_paths_file(self) -> None:
        """Validate main paths file exists"""
        if not settings.MAIN_PATHS_FILE.exists():
            self.errors.append(
                f"❌ Main paths file not found: {settings.MAIN_PATHS_FILE}\n"
                f"   Create this file with the list of files to collect"
            )

    def get_errors(self) -> str:
        """Get formatted error messages"""
        return "\n\n".join(self.errors)