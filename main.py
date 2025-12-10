# main.py
"""
Main entry point for Java Modernizator with Action orchestration
"""
import json
import sys

from config.settings import settings
from infrastructure.file_collector import FileCollectorService
from infrastructure.stackspot_action_runner import StackspotActionRunner
from infrastructure.stackspot_client import StackspotApiClient

# 🚀 MODO DE DESENVOLVIMENTO - Configure aqui
DEV_MODE = True  # Mude para False para execução completa
DEV_EXECUTION_ID = "01KC3WJQRRMWVNDMH9W0S89JWW"  # Seu ID de execução


def validate_setup() -> None:
    """Validate that all required files and directories exist"""
    errors = []

    if not settings.CREDENTIALS_PATH.exists():
        errors.append(
            f"❌ Credentials file not found: {settings.CREDENTIALS_PATH}\n"
            f"   Create it from: {settings.PROJECT_ROOT / 'secrets-example.json'}"
        )

    # Validate git_token exists in credentials (only if not in dev mode)
    if not DEV_MODE:
        try:
            git_token = settings.get_git_token()
            if not git_token:
                errors.append(
                    f"❌ Git token not found in credentials file\n"
                    f"   Add 'git_token' to: {settings.CREDENTIALS_PATH}"
                )
        except Exception as e:
            errors.append(f"❌ Error loading credentials: {e}")

        # Validate main-paths.txt exists (only if not in dev mode)
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
            callback_file.parent.mkdir(exist_ok=True)

            with open(callback_file, 'w', encoding='utf-8') as f:
                json.dump(callback_result, f, indent=2, ensure_ascii=False)

            print(f"💾 Callback result saved to: {callback_file}")

            # Also save a pretty-printed version
            pretty_file = settings.PROJECT_ROOT / "assets" / "callback-result-pretty.json"
            with open(pretty_file, 'w', encoding='utf-8') as f:
                json.dump(callback_result, f, indent=4, ensure_ascii=False)

            print(f"📄 Pretty version saved to: {pretty_file}")

            return {
                'success': True,
                'callback_result': callback_result,
                'callback_file': str(callback_file),
                'pretty_file': str(pretty_file)
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


def process_callback_results(callback_file: str) -> dict:
    """
    Process callback results and generate structured reports
    Args:
        callback_file: Path to callback result JSON file
    Returns:
        Processing results
    """
    print("\n" + "📊 STEP 5: Processing Results".center(60, "="))

    try:
        from application.result_processor import StackSpotResultProcessor

        # Initialize processor
        processor = StackSpotResultProcessor()

        # Load callback result
        callback_data = processor.load_callback_result(callback_file)

        if not callback_data:
            return {'success': False, 'error': 'Failed to load callback data'}

        # Generate summary report
        print("📝 Generating summary report...")
        summary_report = processor.generate_summary_report()

        # Save structured results
        print("💾 Saving structured results...")
        output_dir = settings.PROJECT_ROOT / "assets" / "results"
        saved_files = processor.save_structured_results(str(output_dir))

        # Print summary to console
        print("\n" + "📋 SUMMARY REPORT".center(60, "="))
        print(summary_report)

        return {
            'success': True,
            'summary_report': summary_report,
            'saved_files': saved_files,
            'output_dir': str(output_dir)
        }

    except Exception as e:
        print(f"❌ Failed to process results: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def main():
    """Main execution function"""
    print("🎵 Modern Jazz - Java Modernizator".center(60, "="))
    print("🎯 Hackathon Future Minds Edition\n")

    if DEV_MODE:
        print("🚀 DEV MODE ENABLED - Skipping to Step 4".center(60, "🔧"))
        print(f"🔗 Using Execution ID: {DEV_EXECUTION_ID}")
        print("=" * 60)

    # Validate setup
    validate_setup()

    try:
        if DEV_MODE:
            # 🚀 MODO DESENVOLVIMENTO: Pular direto para Step 4
            print("\n⚡ Development Mode: Skipping Steps 1-3")

            # Step 4: Fetch callback result
            callback_result = run_callback_fetch(DEV_EXECUTION_ID)

            # Step 5: Process results (AGORA INCLUÍDO!)
            if callback_result['success']:
                processing_result = process_callback_results(callback_result['callback_file'])

                # Final summary for dev mode
                print("\n" + "✅ DEV MODE COMPLETED".center(60, "="))
                print(f"\n📊 Results:")
                print(f" 🔗 Execution ID: {DEV_EXECUTION_ID}")
                print(f" 📞 Callback Success: {callback_result['success']}")
                print(f" 📊 Processing Success: {processing_result['success']}")

                if callback_result['success']:
                    print(f" 💾 Callback file: {callback_result['callback_file']}")
                    print(f" 📄 Pretty file: {callback_result['pretty_file']}")

                if processing_result['success']:
                    print(f" 📁 Results directory: {processing_result['output_dir']}")
                    print(f" 📝 Files generated: {len(processing_result['saved_files'])}")
                    for file_type, file_path in processing_result['saved_files'].items():
                        print(f"   📄 {file_type}: {file_path}")
                else:
                    print(f" ⚠️ Processing issue: {processing_result.get('error', 'Unknown error')}")
            else:
                print(f" ⚠️ Callback issue: {callback_result.get('message', 'Unknown error')}")

        else:
            # 🔄 MODO COMPLETO: Executar todos os steps
            use_cloned_repo = True

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

            # Step 5: Process results
            if callback_result['success']:
                processing_result = process_callback_results(callback_result['callback_file'])

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
                if processing_result['success']:
                    print(f"   📁 Results directory: {processing_result['output_dir']}")

        print("\n" + "=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())