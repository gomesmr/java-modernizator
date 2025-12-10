# main.py
"""
Main entry point for Java Modernizator with Action orchestration
"""
import sys
import json
from pathlib import Path
from application.modernization_service import ModernizationService
from application.report_generator import ReportGenerator
from config.settings import settings
from infrastructure.file_system import JavaFileRepository
from infrastructure.stackspot_client import StackspotApiClient
from infrastructure.stackspot_action_runner import StackspotActionRunner
from infrastructure.file_collector import FileCollectorService


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

    # Validate main-paths.txt exists
    if not settings.MAIN_PATHS_FILE.exists():
        errors.append(
            f"❌ Main paths file not found: {settings.MAIN_PATHS_FILE}\n"
            f"   Create this file with the list of files to collect"
        )

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


def run_file_collection(cloned_repo_path: str) -> str:
    """
    Execute file collection step

    Args:
        cloned_repo_path: Path to cloned repository

    Returns:
        Path to generated payload file
    """
    print("\n" + "📄 STEP 2: Collecting Files".center(60, "="))

    try:
        file_collector = FileCollectorService()
        payload_file = file_collector.generate_payload_file(
            cloned_repo_path=cloned_repo_path,
            paths_file_path=str(settings.MAIN_PATHS_FILE),
            output_file_path=str(settings.MAIN_PAYLOAD_FILE)
        )
        return payload_file

    except Exception as e:
        print(f"❌ Failed to collect files: {e}")
        raise


def run_stackspot_processing(payload_file: str) -> dict:
    """
    Execute StackSpot processing step

    Args:
        payload_file: Path to payload file

    Returns:
        Processing results
    """
    print("\n" + "🤖 STEP 3: Processing with StackSpot AI".center(60, "="))

    try:
        # Read payload content
        with open(payload_file, 'r', encoding='utf-8') as f:
            payload_content = f.read()

        # Initialize StackSpot client
        api_client = StackspotApiClient(str(settings.CREDENTIALS_PATH))

        # Execute quick command
        print(f"🚀 Executing quick command: {settings.QUICK_COMMAND_SLUG}")
        execution_id = api_client.execute_quick_command(
            settings.QUICK_COMMAND_SLUG,
            payload_content
        )

        # Poll for results
        print(f"⏳ Polling for results...")
        result = api_client.poll_execution_result(execution_id)

        return {
            'execution_id': execution_id,
            'result': result,
            'success': result is not None
        }

    except Exception as e:
        print(f"❌ Failed to process with StackSpot: {e}")
        raise


def run_callback_fetch(execution_id: str) -> dict:
    """
    Execute callback fetch step

    Args:
        execution_id: Execution ID from StackSpot processing

    Returns:
        Callback results
    """
    print("\n" + "📞 STEP 4: Fetching Callback Result".center(60, "="))

    try:
        # Initialize StackSpot client
        api_client = StackspotApiClient(str(settings.CREDENTIALS_PATH))

        # Get callback result
        callback_result = api_client.get_callback_result(execution_id)

        if callback_result:
            # Save callback result to file
            callback_file = settings.PROJECT_ROOT / "assets" / "callback-result.json"
            with open(callback_file, 'w', encoding='utf-8') as f:
                json.dump(callback_result, f, indent=2, ensure_ascii=False)

            print(f"💾 Callback result saved to: {callback_file}")

            return {
                'success': True,
                'callback_result': callback_result,
                'callback_file': str(callback_file)
            }
        else:
            return {
                'success': False,
                'callback_result': None,
                'message': 'Callback result not available'
            }

    except Exception as e:
        print(f"❌ Failed to fetch callback: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def main():
    """Main execution function"""
    print("🎵 Modern Jazz - Java Modernizator".center(60, "="))
    print("🎯 Hackathon Future Minds Edition\n")

    # Validate setup
    validate_setup()

    # Configuration
    use_cloned_repo = True  # Set to False to skip cloning

    try:
        # Step 1: Clone repository
        if use_cloned_repo:
            cloned_repo_path = run_clone_step()
        else:
            cloned_repo_path = settings.GIT_CLONE_TARGET
            print(f"\n📁 Using existing path: {cloned_repo_path}")

        # Step 2: Collect files and generate payload
        payload_file = run_file_collection(cloned_repo_path)

        # Step 3: Process with StackSpot AI
        stackspot_result = run_stackspot_processing(payload_file)

        # Step 4: Fetch callback result
        callback_result = run_callback_fetch(stackspot_result['execution_id'])

        # Final summary
        print("\n" + "✅ PROCESS COMPLETED".center(60, "="))
        print(f"\n📊 Results:")
        print(f"   📁 Cloned repo: {cloned_repo_path}")
        print(f"   📄 Payload file: {payload_file}")
        print(f"   🔗 Execution ID: {stackspot_result['execution_id']}")
        print(f"   ✅ Processing Success: {stackspot_result['success']}")

        if stackspot_result['result']:
            print(f"   📝 Processing Result length: {len(stackspot_result['result'])} chars")

        print(f"   📞 Callback Success: {callback_result['success']}")
        if callback_result['success']:
            print(f"   💾 Callback file: {callback_result['callback_file']}")
        else:
            print(f"   ⚠️ Callback issue: {callback_result.get('message', 'Unknown error')}")

        print("\n" + "=" * 60)

        return 0

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())