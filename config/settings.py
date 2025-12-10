# config/settings.py
"""
Application settings and configuration
"""
from pathlib import Path
import json

class Settings:
    """Application settings"""

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    CREDENTIALS_PATH = PROJECT_ROOT / 'secrets.json'
    REPORT_OUTPUT_PATH = PROJECT_ROOT / 'modernization_report.json'

    # StackSpot
    QUICK_COMMAND_SLUG = 'modernize-legacy-java-code'
    POLLING_DELAY = 23

    # Git Repository Configuration (FIXED VALUES)
    GIT_REPO_URL = "https://github.com/gomesmr/desafio-hackathon-zup-byte-t3"
    GIT_CLONE_TARGET = "../desafio-hackathon-zup-byte-t3"

    # Action Paths
    CLONE_ACTION_PATH = r"C:\Users\marcelo.gomes\gomesmr\Hackathon\clone-repository-action"

    # File System
    IGNORED_DIRECTORIES = {
        '.git', '.idea', '__pycache__', 'target', 'build',
        'out', '.gradle', 'node_modules'
    }

    def load_credentials(self) -> dict:
        """Load credentials from secrets.json"""
        if not self.CREDENTIALS_PATH.exists():
            raise FileNotFoundError(
                f"Credentials file not found: {self.CREDENTIALS_PATH}\n"
                f"Create it from: {self.PROJECT_ROOT / 'secrets-example.json'}"
            )

        with open(self.CREDENTIALS_PATH, 'r') as f:
            return json.load(f)

    def get_git_token(self) -> str:
        """Get Git token from credentials"""
        creds = self.load_credentials()
        return creds.get('git_token', '')

settings = Settings()


# Debug: Print settings when module is imported
if __name__ == '__main__':
    print("🔍 Settings Debug:")
    print(settings)
    print(f"\n📁 Credentials file exists: {settings.CREDENTIALS_PATH.exists()}")