"""
Modern Jazz - Java Modernizator
Main entry point
"""
import sys

from domain.enums.execution_mode import ExecutionMode
from application.validators.setup_validator import SetupValidator
from application.orchestrator import ExecutionOrchestrator

# 🚀 Configuration
DEV_MODE = False
DEV_EXECUTION_ID = "01KC3WJQRRMWVNDMH9W0S89JWW"


def print_header() -> None:
    """Print application header"""
    print("🎵 Modern Jazz - Java Modernizator".center(60, "="))
    print("🎯 Hackathon Future Minds Edition\n")


def print_mode_info(mode: ExecutionMode, execution_id: str = None) -> None:
    """Print execution mode information"""
    if mode.is_dev:
        print("🚀 DEV MODE ENABLED - Skipping to Step 4".center(60, "🔧"))
        print(f"🔗 Using Execution ID: {execution_id}")
        print("=" * 60)


def print_results(result, mode: ExecutionMode) -> None:
    """Print execution results"""
    status = "✅ COMPLETED" if result.success else "❌ FAILED"
    mode_label = "DEV MODE" if mode.is_dev else "PROCESS"

    print(f"\n{status} {mode_label}".center(60, "="))
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

    # Determine execution mode
    mode = ExecutionMode.DEVELOPMENT if DEV_MODE else ExecutionMode.PRODUCTION
    print_mode_info(mode, DEV_EXECUTION_ID if mode.is_dev else None)

    # Validate setup
    validator = SetupValidator(dev_mode=mode.is_dev)
    if not validator.validate():
        print(validator.get_errors())
        return 1

    try:
        # Execute orchestrated flow
        orchestrator = ExecutionOrchestrator(
            mode=mode,
            dev_execution_id=DEV_EXECUTION_ID if mode.is_dev else None
        )
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