"""
Modern Jazz - Java Modernizator
Main entry point
"""
import sys

from application.validators.setup_validator import SetupValidator
from application.orchestrator import ExecutionOrchestrator
from domain.enums.execution_mode import ExecutionMode


def print_header() -> None:
    """Print application header"""
    print("🎵 Modern Jazz - Java Modernizator".center(60, "="))
    print("🎯 Hackathon Future Minds Edition\n")


def print_results(result, mode: ExecutionMode) -> None:
    """Print execution results"""
    status = "✅ COMPLETED" if result.success else "❌ FAILED"
    print(f"\n{status} PROCESS".center(60, "="))
    print(f"\n📊 Results:")

    if result.execution_id:
        print(f"   🔗 Execution ID: {result.execution_id}")
    if result.cloned_repo_path:
        print(f"   📁 Cloned repo: {result.cloned_repo_path}")
    if result.payload_file:
        print(f"   📄 Payload file: {result.payload_file}")
    if result.callback_file:
        print(f"   💾 Callback file: {result.callback_file}")
    if result.results_directory:
        print(f"   📁 Results directory: {result.results_directory}")

    print(f"   ✅ Success: {result.success}")

    if result.error:
        print(f"   ⚠️ Error: {result.error}")

    print("\n" + "=" * 60)


def main() -> int:
    """
    Main execution function

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print_header()

    # Always run in production mode
    mode = ExecutionMode.PRODUCTION

    # Validate setup
    validator = SetupValidator()
    if not validator.validate():
        print(validator.get_errors())
        return 1

    try:
        # Execute orchestrated flow
        orchestrator = ExecutionOrchestrator(mode=mode)
        result = orchestrator.execute()

        # Print results
        print_results(result, mode)

        return 0 if result.success else 1

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())