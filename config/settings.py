"""
Application settings and configuration
"""
from pathlib import Path


class Settings:
    """Application settings"""

    # Paths - Corrigido para apontar para o diretório correto
    PROJECT_ROOT = Path(__file__).parent.parent  # modern-jazz/
    CREDENTIALS_PATH = PROJECT_ROOT / 'secrets.json'
    REPORT_OUTPUT_PATH = PROJECT_ROOT / 'modernization_report.json'

    # Stackspot
    QUICK_COMMAND_SLUG = 'modernize-legacy-java-code'
    POLLING_DELAY = 23

    # File System
    IGNORED_DIRECTORIES = {
        '.git', '.idea', '__pycache__', 'target',
        'build', 'out', '.gradle', 'node_modules'
    }

    def __repr__(self):
        """String representation for debugging"""
        return (
            f"Settings(\n"
            f"  PROJECT_ROOT={self.PROJECT_ROOT}\n"
            f"  CREDENTIALS_PATH={self.CREDENTIALS_PATH}\n"
            f"  REPORT_OUTPUT_PATH={self.REPORT_OUTPUT_PATH}\n"
            f")"
        )


settings = Settings()


# Debug: Print settings when module is imported
if __name__ == '__main__':
    print("🔍 Settings Debug:")
    print(settings)
    print(f"\n📁 Credentials file exists: {settings.CREDENTIALS_PATH.exists()}")