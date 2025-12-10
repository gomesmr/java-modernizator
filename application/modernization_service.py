"""
Service for modernizing Java code
"""
from typing import List

from domain.entities import ModernizationResult, JavaFile
from infrastructure.file_system import JavaFileRepository
from infrastructure.stackspot_client import StackspotApiClient


class ModernizationService:
    """Service for orchestrating Java code modernization"""

    QUICK_COMMAND_SLUG = 'modernize-legacy-java-code'

    def __init__(
        self,
        file_repository: JavaFileRepository,
        api_client: StackspotApiClient
    ):
        self.file_repository = file_repository
        self.api_client = api_client
        self.results: List[ModernizationResult] = []

    def modernize_file(
        self,
        java_file: JavaFile,
        save_changes: bool = True
    ) -> ModernizationResult:
        """Modernize a single Java file"""
        print(f"\n{'=' * 60}")
        print(f"📄 Processing: {java_file.relative_path}")
        print(f"   Size: {java_file.size_in_bytes} bytes")
        print(f"{'=' * 60}")

        # Execute modernization
        try:
            execution_id = self.api_client.execute_quick_command(
                self.QUICK_COMMAND_SLUG,
                java_file.content
            )
        except Exception as e:
            return self._create_failed_result(
                java_file.absolute_path,
                f"Failed to execute command: {e}"
            )

        # Get results
        try:
            modernized_content = self.api_client.poll_execution_result(
                execution_id
            )
        except Exception as e:
            return self._create_failed_result(
                java_file.absolute_path,
                f"Failed to get results: {e}",
                execution_id
            )

        if not modernized_content:
            return self._create_failed_result(
                java_file.absolute_path,
                "Empty or invalid result",
                execution_id
            )

        # Save changes if requested
        if save_changes:
            try:
                self.file_repository.save_file(
                    java_file.absolute_path,
                    modernized_content
                )
                print(f"💾 File updated: {java_file.absolute_path}")
            except Exception as e:
                return self._create_failed_result(
                    java_file.absolute_path,
                    f"Failed to save file: {e}",
                    execution_id
                )

        result = ModernizationResult(
            file_path=java_file.absolute_path,
            is_successful=True,
            execution_id=execution_id,
            original_content=java_file.content,
            modernized_content=modernized_content
        )

        self.results.append(result)
        return result

    def modernize_all_files(self, save_changes: bool = True) -> dict:
        """Modernize all Java files in repository"""
        print(f"\n{'#' * 60}")
        print(f"🚀 STARTING MODERNIZATION")
        print(f"{'#' * 60}\n")

        summary = self.file_repository.get_summary()
        print(f"📊 Total Java files found: {summary['total_files']}")
        print(f"📊 Total size: {summary['total_size_bytes']} bytes\n")

        if summary['total_files'] == 0:
            print("⚠️ No Java files found!")
            return self._create_empty_stats()

        processed = 0
        successful = 0
        failed = 0

        for java_file in self.file_repository.get_all_java_files():
            result = self.modernize_file(java_file, save_changes)
            processed += 1

            if result.is_successful:
                successful += 1
            else:
                failed += 1

        return self._create_stats(
            summary['total_files'],
            processed,
            successful,
            failed
        )

    def _create_failed_result(
        self,
        file_path: str,
        error_message: str,
        execution_id: str = None
    ) -> ModernizationResult:
        """Create a failed modernization result"""
        result = ModernizationResult(
            file_path=file_path,
            is_successful=False,
            execution_id=execution_id,
            error_message=error_message
        )
        self.results.append(result)
        return result

    def _create_empty_stats(self) -> dict:
        """Create empty statistics"""
        return {
            'total_files': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'success_rate': '0%'
        }

    def _create_stats(
        self,
        total: int,
        processed: int,
        successful: int,
        failed: int
    ) -> dict:
        """Create statistics dictionary"""
        success_rate = f"{(successful / processed * 100):.2f}%" if processed > 0 else "0%"

        stats = {
            'total_files': total,
            'processed': processed,
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate
        }

        print(f"\n{'#' * 60}")
        print(f"✅ MODERNIZATION COMPLETED")
        print(f"{'#' * 60}")
        print(f"📊 Total files: {stats['total_files']}")
        print(f"✅ Successful: {stats['successful']}")
        print(f"❌ Failed: {stats['failed']}")
        print(f"📈 Success rate: {stats['success_rate']}")
        print(f"{'#' * 60}\n")

        return stats

    def get_results(self) -> List[ModernizationResult]:
        """Get all modernization results"""
        return self.results