from pathlib import Path
import json
from typing import Dict, Any

from domain.entities import StepResult
from config.settings import settings
from infrastructure.stackspot_client import StackspotApiClient


class RefactoringStep:

    def __init__(self):
        self.api_client = StackspotApiClient(str(settings.CREDENTIALS_PATH))
        self.quick_command_slug = "java-modern-jazz"

    def execute(self) -> StepResult:
        try:
            main_paths_file = Path(settings.ASSETS_DIR) / "main-paths.txt"
            if not main_paths_file.exists():
                return StepResult(
                    success=False,
                    error="main-paths.txt not found"
                )

            with open(main_paths_file, 'r', encoding='utf-8') as f:
                file_paths = [line.strip() for line in f if line.strip()]

            analysis_file = Path(settings.RESULTS_DIR) / "analysis-result.json"
            plan_file = Path(settings.RESULTS_DIR) / "plan-result.json"

            if not analysis_file.exists() or not plan_file.exists():
                return StepResult(
                    success=False,
                    error="Analysis or plan results not found"
                )

            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)

            with open(plan_file, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)

            refactored_files = []
            for file_path in file_paths:
                print(f"Processing refactoring for: {file_path}")
                result = self._refactor_file(file_path, analysis_data, plan_data)
                if result:
                    refactored_files.append(result)

            output_file = Path(settings.RESULTS_DIR) / "refactor-result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total_files': len(refactored_files),
                    'files': refactored_files
                }, f, indent=2, ensure_ascii=False)

            return StepResult(
                success=True,
                data={
                    'refactored_files': refactored_files,
                    'output_file': str(output_file)
                }
            )

        except Exception as e:
            return StepResult(
                success=False,
                error=f"Error in refactoring step: {str(e)}"
            )

    def _refactor_file(
            self,
            file_path: str,
            analysis_data: Dict[str, Any],
            plan_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()

            input_data = self._build_input_data(
                file_path,
                original_code,
                analysis_data,
                plan_data
            )

            execution_id = self.api_client.execute_quick_command(
                command_slug=self.quick_command_slug,
                input_content=input_data
            )

            print(f"  Execution created: {execution_id}")

            result = self.api_client.poll_execution_result(execution_id)

            refactored_content = json.loads(result).get('result', '') if isinstance(result, str) else result.get(
                'result', '')
            refactored_file = self._save_refactored_code(file_path, refactored_content)

            return {
                'original_file': file_path,
                'refactored_file': refactored_file,
                'execution_id': execution_id,
                'success': True
            }

        except Exception as e:
            print(f"  Error refactoring {file_path}: {str(e)}")
            return {
                'original_file': file_path,
                'error': str(e),
                'success': False
            }

    def _build_input_data(
            self,
            file_path: str,
            original_code: str,
            analysis_data: Dict[str, Any],
            plan_data: Dict[str, Any]
    ) -> str:
        file_analysis = self._extract_file_analysis(file_path, analysis_data)
        file_plan = self._extract_file_plan(file_path, plan_data)

        input_data = f"""# Tarefa de Refatoração

## Arquivo: {file_path}

## Código Original:
```java
{original_code}
```
## Relatório de Análise:
{file_analysis}

## Plano de Modernização:
{file_plan}

## Tarefa:
Refatore o código seguindo as recomendações acima, mantendo a funcionalidade original.

Retorne APENAS o código refatorado, sem explicações adicionais."""


        return input_data


    def _extract_file_analysis(
            self,
            file_path: str,
            analysis_data: Dict[str, Any]
    ) -> str:
        result = analysis_data.get('result', '')

        if file_path in result:
            lines = result.split('\n')
            relevant_lines = []
            capturing = False

            for line in lines:
                if file_path in line:
                    capturing = True
                elif capturing and line.startswith('##'):
                    break
                elif capturing:
                    relevant_lines.append(line)

            return '\n'.join(relevant_lines) if relevant_lines else result

        return result


    def _extract_file_plan(
            self,
            file_path: str,
            plan_data: Dict[str, Any]
    ) -> str:
        result = plan_data.get('result', '')

        if file_path in result:
            lines = result.split('\n')
            relevant_lines = []
            capturing = False

            for line in lines:
                if file_path in line:
                    capturing = True
                elif capturing and line.startswith('##'):
                    break
                elif capturing:
                    relevant_lines.append(line)

            return '\n'.join(relevant_lines) if relevant_lines else result

        return result


    def _save_refactored_code(self, original_path: str, refactored_code: str) -> str:
        refactored_dir = Path(settings.RESULTS_DIR) / "refactored"
        refactored_dir.mkdir(parents=True, exist_ok=True)

        original_name = Path(original_path).name
        output_file = refactored_dir / f"refactored_{original_name}"

        cleaned_code = self._clean_code_output(refactored_code)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_code)

        return str(output_file)


    def _clean_code_output(self, code: str) -> str:
        lines = code.split('\n')
        cleaned_lines = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if not in_code_block or line.strip():
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()