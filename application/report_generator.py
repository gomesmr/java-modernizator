"""
Report generation for modernization results
"""
import json
from pathlib import Path
from typing import List

from domain.entities import ModernizationResult


class ReportGenerator:
    """Generate reports from modernization results"""

    def __init__(self, results: List[ModernizationResult]):
        self.results = results

    def generate_json_report(self, output_path: str) -> None:
        """Generate JSON report"""
        report = {
            'summary': self._generate_summary(),
            'results': self._generate_results_list()
        }

        Path(output_path).write_text(
            json.dumps(report, indent=2, ensure_ascii=False)
        )

        print(f"📄 Report saved: {output_path}")

    def _generate_summary(self) -> dict:
        """Generate summary statistics"""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.is_successful)
        failed = total - successful
        with_changes = sum(1 for r in self.results if r.has_changes)

        return {
            'total_files': total,
            'successful': successful,
            'failed': failed,
            'files_with_changes': with_changes,
            'success_rate': f"{(successful / total * 100):.2f}%" if total > 0 else "0%"
        }

    def _generate_results_list(self) -> list:
        """Generate list of individual results"""
        return [
            {
                'file_path': r.file_path,
                'is_successful': r.is_successful,
                'execution_id': r.execution_id,
                'error_message': r.error_message,
                'has_changes': r.has_changes
            }
            for r in self.results
        ]