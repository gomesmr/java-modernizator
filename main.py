# main.py
"""
Main entry point for Java Modernizator with Action orchestration
"""
import sys
from pathlib import Path
from application.modernization_service import ModernizationService
from application.report_generator import ReportGenerator
from config.settings import settings
from infrastructure.file_system import JavaFileRepository
from infrastructure.stackspot_client import StackspotApiClient
from infrastructure.stackspot_action_runner import StackspotActionRunner

def validate_setup() -> None:
    """Validate that all required files and directories exist"""
    errors = []

    if not settings.CREDENTIALS_PATH.exists():
        errors.append(
            f"❌ Credentials file not found: {settings.CREDENTIALS_PATH}\n"
            f"   Create it from: {settings.PROJECT_ROOT / 'secrets-example.json'}"
        )

    # Validate git_token exists in credentials
    try:
        git_token = settings.get_git_token()
        if not git_token:
            errors.append(
                f"❌ Git token not found in credentials file\n"
                f"   Add 'git_token' to: {settings.CREDENTIALS_PATH}"
            )
    except Exception as e:
        errors.append(f"❌ Error loading credentials: {e}")

    if errors:
        print("\n" + "\n\n".join(errors))
        sys.exit(1)

def run_clone_step() -> str:
    """
    Execute clone repository action

    Returns:
        Path to cloned repository
    """
    print("\n" + "🔄 STEP 1: Cloning Repository".center(60, "="))

    try:
        action_runner = StackspotActionRunner(wsl_enabled=False)
        repo_path = action_runner.clone_repository()
        return repo_path

    except Exception as e:
        print(f"❌ Failed to clone repository: {e}")
        raise

def run_modernization(java_project_path: str, save_changes: bool = True) -> dict:
    """
    Execute modernization process

    Args:
        java_project_path: Path to Java project
        save_changes: Whether to save changes

    Returns:
        Statistics dictionary
    """
    print("\n" + "🔧 STEP 2: Modernizing Code".center(60, "="))

    # Initialize components
    file_repository = JavaFileRepository(java_project_path)
    api_client = StackspotApiClient(str(settings.CREDENTIALS_PATH))
    service = ModernizationService(file_repository, api_client)

    # Execute modernization
    stats = service.modernize_all_files(save_changes=save_changes)

    # Generate report
    print("\n📝 Generating report...")
    report_generator = ReportGenerator(service.get_results())
    report_generator.generate_json_report(str(settings.REPORT_OUTPUT_PATH))

    return stats

def main():
    """Main execution function"""
    print("🎵 Modern Jazz - Java Modernizator".center(60, "="))
    print("🎯 Hackathon Future Minds Edition\n")

    # Validate setup
    validate_setup()

    # Configuration
    save_changes = True
    use_cloned_repo = True  # Set to False to skip cloning

    try:
        # Step 1: Clone repository
        if use_cloned_repo:
            java_project_path = run_clone_step()
        else:
            java_project_path = settings.GIT_CLONE_TARGET
            print(f"\n📁 Using existing path: {java_project_path}")

        # Step 2: Modernize code
        stats = run_modernization(java_project_path, save_changes)

        # Final summary
        print("\n" + "✅ PROCESS COMPLETED".center(60, "="))
        print(f"\n📊 Final Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        print(f"\n📄 Report: {settings.REPORT_OUTPUT_PATH}")
        print("\n" + "="*60)

        return 0

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())