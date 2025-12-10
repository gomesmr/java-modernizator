# config/settings.py
"""
Application settings and configuration
"""
from pathlib import Path
import json


class Settings:
    """Application settings"""

    def __init__(self):
        # Ensure assets directory exists
        self.ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # Path configurations
    PROJECT_ROOT = Path(__file__).parent.parent
    ASSETS_DIR = PROJECT_ROOT / "assets"  # Added missing assets directory
    CREDENTIALS_PATH = PROJECT_ROOT / 'secrets.json'
    REPORT_OUTPUT_PATH = PROJECT_ROOT / 'modernization_report.json'

    # File paths using assets directory
    MAIN_PATHS_FILE = ASSETS_DIR / "main-paths.txt"
    MAIN_PAYLOAD_FILE = ASSETS_DIR / "main-payload.md"
    CALLBACK_FILE = ASSETS_DIR / "callback-result.json"  # Added callback file path

    # StackSpot configuration
    QUICK_COMMAND_SLUG = 'modernize-legacy-java-code'
    POLLING_DELAY = 23  # Seconds between polling attempts

    # Git configuration
    GIT_REPO_URL = "https://github.com/gomesmr/desafio-hackathon-zup-byte-t3"
    GIT_CLONE_TARGET = "../desafio-hackathon-zup-byte-t3"
    CLONE_ACTION_PATH = r"C:\Users\marcelo.gomes\gomesmr\Hackathon\clone-repository-action"

    RESULTS_DIR = ASSETS_DIR / "results"
    STK_UI_URL = "azeite"

    # Security configurations
    IGNORED_DIRECTORIES = {
        '.git', '.idea', '__pycache__', 'target', 'build',
        'out', '.gradle', 'node_modules'
    }

    def load_credentials(self) -> dict:
        """Load credentials from secrets.json"""
        if not self.CREDENTIALS_PATH.exists():
            raise FileNotFoundError(
                f"Credentials file not found: {self.CREDENTIALS_PATH}\n"
                f"Create it from template: {self.PROJECT_ROOT / 'secrets-example.json'}"
            )

        with open(self.CREDENTIALS_PATH, 'r') as f:
            return json.load(f)

    def get_git_token(self) -> str:
        """Get Git token from credentials"""
        return self.load_credentials().get('git_token', '')

    # Add StackSpot credentials methods
    def get_stackspot_credentials(self) -> dict:
        """Get StackSpot credentials"""
        return {
            'client_id': self.load_credentials().get('STK_CLIENT_ID'),
            'client_key': self.load_credentials().get('STK_CLIENT_KEY'),
            'realm': self.load_credentials().get('STK_REALM')
        }


settings = Settings()

# Debug configuration
if __name__ == '__main__':
    print("🔧 Active Settings:")
    print(f"📁 Project Root: {settings.PROJECT_ROOT}")
    print(f"📦 Assets Directory: {settings.ASSETS_DIR}")
    print(f"🔐 Credentials Path: {settings.CREDENTIALS_PATH}")
    print(f"🔄 Callback File: {settings.CALLBACK_FILE}")
    print(f"✅ Assets Dir Exists: {settings.ASSETS_DIR.exists()}")