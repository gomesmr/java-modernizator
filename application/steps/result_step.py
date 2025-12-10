"""
Result processing step
"""
from application.result_processor import StackSpotResultProcessor
from config.settings import settings
from domain.entities import StepResult


class ResultStep:
    """Handles result processing and report generation"""

    def __init__(self):
        self.processor = StackSpotResultProcessor()
        self.output_dir = settings.PROJECT_ROOT / "assets" / "results"

    def execute(self, callback_file: str) -> StepResult:
        """
        Execute result processing

        Args:
            callback_file: Path to callback result JSON file

        Returns:
            StepResult with processed results
        """
        print("\n" + "📊 STEP 5: Processing Results".center(60, "="))

        try:
            # Load callback result
            callback_data = self.processor.load_callback_result(callback_file)
            if not callback_data:
                return StepResult(
                    success=False,
                    error='Failed to load callback data'
                )

            # Generate summary report
            print("📝 Generating summary report...")
            summary_report = self.processor.generate_summary_report()

            # Save structured results
            print("💾 Saving structured results...")
            saved_files = self.processor.save_structured_results(str(self.output_dir))

            # Print summary
            self._print_summary(summary_report)

            return StepResult(
                success=True,
                data={
                    'summary_report': summary_report,
                    'saved_files': saved_files,
                    'output_dir': str(self.output_dir)
                },
                metadata={
                    'output_dir': str(self.output_dir),
                    'files_count': len(saved_files)
                }
            )

        except Exception as e:
            error_msg = f"Failed to process results: {e}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return StepResult(success=False, error=error_msg)

    @staticmethod
    def _print_summary(summary_report: str) -> None:
        """Print summary report to console"""
        print("\n" + "📋 SUMMARY REPORT".center(60, "="))
        print(summary_report)