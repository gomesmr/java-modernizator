"""
Main entry point for Java Modernizator
"""
import sys
from pathlib import Path

from application.modernization_service import ModernizationService
from application.report_generator import ReportGenerator
from config.settings import settings
from infrastructure.file_system import JavaFileRepository
from infrastructure.stackspot_client import StackspotApiClient


def validate_setup() -> None:
    """Validate that all required files and directories exist"""
    errors = []

    # Check credentials file
    if not settings.CREDENTIALS_PATH.exists():
        errors.append(
            f"❌ Credentials file not found: {settings.CREDENTIALS_PATH}\n"
            f"   Create it from: {settings.PROJECT_ROOT / 'secrets-example.json'}\n"
            f"   Command: copy secrets-example.json secrets.json"
        )

    if errors:
        print("\n" + "\n\n".join(errors))
        print("\n💡 Setup Instructions:")
        print("   1. Copy secrets-example.json to secrets.json")
        print("   2. Fill in your Stackspot credentials")
        print("   3. Run the script again")
        sys.exit(1)


def print_configuration(java_project_path: str) -> None:
    """Print current configuration"""
    print("📋 Configuration:")
    print(f"   Project Root: {settings.PROJECT_ROOT}")
    print(f"   Credentials: {settings.CREDENTIALS_PATH}")
    print(f"   Report Output: {settings.REPORT_OUTPUT_PATH}")
    print(f"   Java Project: {java_project_path}")
    print(f"   Credentials Exists: {settings.CREDENTIALS_PATH.exists()}")
    print()


def main():
    """Main execution function"""
    print("🚀 Java Modernizator - Starting...\n")

    # Validate setup
    validate_setup()

    # Configuration
    java_project_path = r"C:\Users\marcelo.gomes\gomesmr\Hackathon\hackathon\src\main"
    save_changes = True  # Set to False for dry-run

    # Print configuration
    print_configuration(java_project_path)

    try:
        # Initialize components
        print("🔧 Initializing components...")
        file_repository = JavaFileRepository(java_project_path)
        api_client = StackspotApiClient(str(settings.CREDENTIALS_PATH))

        # Create service
        service = ModernizationService(file_repository, api_client)

        # Execute modernization
        print("🚀 Starting modernization process...\n")
        stats = service.modernize_all_files(save_changes=save_changes)

        # Generate report
        print("\n📝 Generating report...")
        report_generator = ReportGenerator(service.get_results())
        report_generator.generate_json_report(
            str(settings.REPORT_OUTPUT_PATH)
        )

        print("\n✅ Process completed successfully!")
        print(f"\n📊 Final Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")

        return 0

    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())