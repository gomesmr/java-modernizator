# application/result_processor.py
"""
Result processor for StackSpot AI callback results
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class AnalysisResult:
    """Structured analysis result"""
    timestamp: str = ""
    repository: str = ""
    java_version: str = ""
    spring_boot_version: Optional[str] = None
    frameworks: List[Dict] = field(default_factory=list)
    outdated_dependencies: List[Dict] = field(default_factory=list)
    legacy_patterns: List[Dict] = field(default_factory=list)
    code_smells: List[Dict] = field(default_factory=list)
    architecture_notes: Dict = field(default_factory=dict)
    summary: str = ""


@dataclass
class PlanResult:
    """Structured plan result"""
    timestamp: str = ""
    strategy: str = ""
    estimated_duration: str = ""
    steps: List[Dict] = field(default_factory=list)
    milestones: List[Dict] = field(default_factory=list)
    risks: List[Dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class RefactorResult:
    """Structured refactor result"""
    timestamp: str = ""
    step_id: str = ""
    status: str = ""
    changes: List[Dict] = field(default_factory=list)
    issues: List[Dict] = field(default_factory=list)
    compilation_status: str = ""
    tests_run: bool = False
    next_step: str = ""


@dataclass
class MetricsResult:
    """Structured metrics result"""
    metadata: Dict = field(default_factory=dict)
    execution: Dict = field(default_factory=dict)
    agents_metrics: Dict = field(default_factory=dict)
    totals: Dict = field(default_factory=dict)
    modernization_impact: Dict = field(default_factory=dict)
    quality_metrics: Dict = field(default_factory=dict)
    versions: Dict = field(default_factory=dict)


class StackSpotResultProcessor:
    """Process and analyze StackSpot AI callback results"""

    def __init__(self):
        self.raw_result = None
        self.analysis = None
        self.plan = None
        self.refactor = None
        self.metrics = None

    def load_callback_result(self, callback_file_path: str) -> Dict:
        """Load callback result from JSON file"""
        try:
            with open(callback_file_path, 'r', encoding='utf-8') as f:
                self.raw_result = json.load(f)

            print(f"✅ Callback result loaded successfully")
            print(f"📊 Execution ID: {self.raw_result.get('execution_id', 'N/A')}")
            print(f"🎯 Command: {self.raw_result.get('quick_command_slug', 'N/A')}")

            progress = self.raw_result.get('progress', {})
            print(f"⏱️ Status: {progress.get('status', 'N/A')}")

            return self.raw_result

        except FileNotFoundError:
            print(f"❌ File not found: {callback_file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in file: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error loading callback result: {e}")
            return {}

    def extract_step_results(self) -> Dict[str, Any]:
        """Extract results from each step"""
        if not self.raw_result:
            print("⚠️ No raw result available")
            return {}

        steps = self.raw_result.get('steps', [])
        if not steps:
            print("⚠️ No steps found in result")
            return {}

        extracted = {}

        for step in steps:
            step_name = step.get('step_name', '')
            step_result = step.get('step_result', {})
            answer = step_result.get('answer', '')

            if not answer:
                print(f"⚠️ No answer found for step: {step_name}")
                continue

            # Map step names to result keys
            step_mapping = {
                'step-analyze': 'analysis',
                'step-plan': 'plan',
                'step-refactor': 'refactor',
                'step-metrics': 'metrics'
            }

            result_key = step_mapping.get(step_name)
            if result_key:
                parsed_data = self._parse_json_answer(answer)
                if parsed_data:
                    extracted[result_key] = parsed_data
                    print(f"✅ Extracted {result_key} data")
                else:
                    print(f"⚠️ Failed to parse {result_key} data")

        return extracted

    def _parse_json_answer(self, answer: str) -> Dict:
        """Parse JSON from step answer with multiple strategies"""
        if not answer or not isinstance(answer, str):
            return {}

        # Strategy 1: Try direct JSON parse
        try:
            return json.loads(answer.strip())
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract from markdown code blocks
        try:
            # Match ```json ... ``` or ``` ... ```
            patterns = [
                r'```json\s*\n(.*?)\n```',
                r'```\s*\n(.*?)\n```',
                r'```json(.*?)```',
                r'```(.*?)```'
            ]

            for pattern in patterns:
                match = re.search(pattern, answer, re.DOTALL)
                if match:
                    json_str = match.group(1).strip()
                    return json.loads(json_str)
        except (json.JSONDecodeError, AttributeError):
            pass

        # Strategy 3: Try to find JSON object/array in text
        try:
            # Find first { or [ and last } or ]
            start_brace = answer.find('{')
            start_bracket = answer.find('[')

            # Determine which comes first
            if start_brace == -1:
                start = start_bracket
                end_char = ']'
            elif start_bracket == -1:
                start = start_brace
                end_char = '}'
            else:
                start = min(start_brace, start_bracket)
                end_char = '}' if start == start_brace else ']'

            if start != -1:
                end = answer.rfind(end_char)
                if end != -1:
                    json_str = answer[start:end + 1]
                    return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass

        print(f"⚠️ Could not parse JSON from answer (length: {len(answer)})")
        return {}

    def process_analysis(self, analysis_data: Dict) -> AnalysisResult:
        """Process analysis step result"""
        return AnalysisResult(
            timestamp=analysis_data.get('timestamp', ''),
            repository=analysis_data.get('repository', ''),
            java_version=analysis_data.get('javaVersion', ''),
            spring_boot_version=analysis_data.get('springBootVersion'),
            frameworks=analysis_data.get('frameworks', []),
            outdated_dependencies=analysis_data.get('outdatedDependencies', []),
            legacy_patterns=analysis_data.get('legacyPatterns', []),
            code_smells=analysis_data.get('codeSmells', []),
            architecture_notes=analysis_data.get('architectureNotes', {}),
            summary=analysis_data.get('summary', '')
        )

    def process_plan(self, plan_data: Dict) -> PlanResult:
        """Process plan step result"""
        return PlanResult(
            timestamp=plan_data.get('timestamp', ''),
            strategy=plan_data.get('strategy', ''),
            estimated_duration=plan_data.get('estimatedDuration', ''),
            steps=plan_data.get('steps', []),
            milestones=plan_data.get('milestones', []),
            risks=plan_data.get('risks', []),
            recommendations=plan_data.get('recommendations', [])
        )

    def process_refactor(self, refactor_data: Dict) -> RefactorResult:
        """Process refactor step result"""
        return RefactorResult(
            timestamp=refactor_data.get('timestamp', ''),
            step_id=refactor_data.get('stepId', ''),
            status=refactor_data.get('status', ''),
            changes=refactor_data.get('changes', []),
            issues=refactor_data.get('issues', []),
            compilation_status=refactor_data.get('compilationStatus', ''),
            tests_run=refactor_data.get('testsRun', False),
            next_step=refactor_data.get('nextStep', '')
        )

    def process_metrics(self, metrics_data: Dict) -> MetricsResult:
        """Process metrics step result"""
        return MetricsResult(
            metadata=metrics_data.get('metadata', {}),
            execution=metrics_data.get('execution', {}),
            agents_metrics=metrics_data.get('agents_metrics', {}),
            totals=metrics_data.get('totals', {}),
            modernization_impact=metrics_data.get('modernization_impact', {}),
            quality_metrics=metrics_data.get('quality_metrics', {}),
            versions=metrics_data.get('versions', {})
        )

    def _safe_get(self, data: Dict, *keys, default='N/A'):
        """Safely get nested dictionary values"""
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, {})
            else:
                return default
        return data if data else default

    def _format_duration(self, seconds: Any) -> str:
        """Format duration in seconds to human readable"""
        try:
            seconds = int(seconds)
            if seconds < 60:
                return f"{seconds}s"
            elif seconds < 3600:
                minutes = seconds // 60
                secs = seconds % 60
                return f"{minutes}m {secs}s"
            else:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                return f"{hours}h {minutes}m"
        except (ValueError, TypeError):
            return str(seconds)

    def generate_summary_report(self) -> str:
        """Generate a comprehensive summary report with proper Markdown formatting"""
        if not self.raw_result:
            return "❌ No callback result loaded"

        # Extract step results
        step_results = self.extract_step_results()

        # Process each step
        analysis = None
        plan = None
        refactor = None
        metrics = None

        if 'analysis' in step_results:
            analysis = self.process_analysis(step_results['analysis'])
        if 'plan' in step_results:
            plan = self.process_plan(step_results['plan'])
        if 'refactor' in step_results:
            refactor = self.process_refactor(step_results['refactor'])
        if 'metrics' in step_results:
            metrics = self.process_metrics(step_results['metrics'])

        # Generate report with proper Markdown formatting
        lines = []

        # Header
        lines.extend([
            "# 🎵 MODERN JAZZ - ANÁLISE COMPLETA",
            "",
            "=" * 60,
            ""
        ])

        # Execution info
        progress = self.raw_result.get('progress', {})
        lines.extend([
            "## 📊 INFORMAÇÕES DA EXECUÇÃO",
            "",
            f"🔗 **Execution ID:** `{self.raw_result.get('execution_id', 'N/A')}`",
            "",
            f"🎯 **Command:** `{self.raw_result.get('quick_command_slug', 'N/A')}`",
            "",
            f"⏱️ **Status:** {progress.get('status', 'N/A')}",
            "",
            f"🕐 **Duração:** {self._format_duration(progress.get('duration', 0))}",
            "",
            f"📅 **Início:** {progress.get('start', 'N/A')}",
            "",
            f"🏁 **Fim:** {progress.get('end', 'N/A')}",
            ""
        ])

        # Analysis summary
        if analysis:
            lines.extend([
                "## 🔍 ANÁLISE DO PROJETO",
                "",
                f"📁 **Repositório:** {analysis.repository}",
                "",
                f"☕ **Java Version:** {analysis.java_version}",
                "",
                f"🌱 **Spring Boot:** {analysis.spring_boot_version or 'Não detectado'}",
                ""
            ])

            # Frameworks
            if analysis.frameworks:
                lines.extend([
                    f"### 📚 FRAMEWORKS DESATUALIZADOS ({len(analysis.frameworks)}):",
                    ""
                ])
                for fw in analysis.frameworks:
                    is_outdated = fw.get('isOutdated', False)
                    status = "❌" if is_outdated else "✅"
                    current = fw.get('currentVersion', 'N/A')
                    latest = fw.get('latestStableVersion', 'N/A')
                    lines.append(f"- {status} **{fw.get('name', 'Unknown')}:** {current} → {latest}")
                lines.append("")

            # Legacy patterns
            if analysis.legacy_patterns:
                lines.extend([
                    f"### ⚠️ PADRÕES LEGADOS ({len(analysis.legacy_patterns)}):",
                    ""
                ])
                for pattern in analysis.legacy_patterns:
                    severity = pattern.get('severity', 'medium')
                    severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
                    pattern_type = pattern.get('type', 'Unknown')
                    location = pattern.get('location', 'N/A')
                    lines.append(f"- {severity_icon} **{pattern_type}** - `{location}`")
                lines.append("")

            # Code smells
            if analysis.code_smells:
                lines.extend([
                    f"### 🦨 CODE SMELLS ({len(analysis.code_smells)}):",
                    ""
                ])
                for smell in analysis.code_smells:
                    severity = smell.get('severity', 'low')
                    severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
                    smell_type = smell.get('type', 'Unknown')
                    location = smell.get('location', 'N/A')
                    lines.append(f"- {severity_icon} **{smell_type}** - `{location}`")
                lines.append("")

        # Plan summary
        if plan:
            lines.extend([
                "## 📋 PLANO DE MODERNIZAÇÃO",
                "",
                f"🎯 **Estratégia:** {plan.strategy}",
                "",
                f"⏱️ **Duração Estimada:** {plan.estimated_duration}",
                "",
                f"📝 **Total de Steps:** {len(plan.steps)}",
                ""
            ])

            # Milestones
            if plan.milestones:
                lines.extend([
                    "### 🎯 MILESTONES:",
                    ""
                ])
                for milestone in plan.milestones:
                    name = milestone.get('name', 'Unknown')
                    description = milestone.get('description', '')
                    steps = milestone.get('steps', [])
                    lines.extend([
                        f"- 📍 **[{name}]** {description}",
                        f"  - Steps: {', '.join(steps) if steps else 'N/A'}",
                        ""
                    ])

        # Refactor summary
        if refactor:
            lines.extend([
                "## 🔧 REFATORAÇÃO EXECUTADA",
                "",
                f"📝 **Step ID:** {refactor.step_id}",
                "",
                f"✅ **Status:** {refactor.status}",
                "",
                f"🔨 **Compilação:** {refactor.compilation_status}",
                "",
                f"🧪 **Testes Executados:** {'Sim' if refactor.tests_run else 'Não'}",
                ""
            ])

            # Modified files
            if refactor.changes:
                lines.extend([
                    f"### 📁 ARQUIVOS MODIFICADOS ({len(refactor.changes)}):",
                    ""
                ])
                for change in refactor.changes:
                    file_path = change.get('file', 'Unknown')
                    description = change.get('description', 'No description')
                    lines.append(f"- 📝 **{file_path}** - {description}")
                lines.append("")

        # Metrics summary
        if metrics:
            lines.extend([
                "## 📊 MÉTRICAS E IMPACTO",
                ""
            ])

            totals = metrics.totals
            impact = metrics.modernization_impact

            lines.extend([
                f"💰 **Custo Total:** ${totals.get('total_cost_usd', 0):.3f}",
                "",
                f"🎯 **Tokens Consumidos:** {totals.get('total_tokens', 0):,}",
                "",
                f"📁 **Arquivos Modificados:** {impact.get('files_modified', 0)}",
                "",
                f"📦 **Dependências Atualizadas:** {impact.get('dependencies_updated', 0)}",
                "",
                f"🦨 **Code Smells Corrigidos:** {impact.get('code_smells_fixed', 0)}",
                ""
            ])

            # Version changes
            versions = metrics.versions
            if versions and 'before' in versions and 'after' in versions:
                lines.extend([
                    "### 🔄 VERSÕES (ANTES → DEPOIS):",
                    ""
                ])
                before = versions['before']
                after = versions['after']
                for key in before:
                    before_val = before.get(key, 'N/A')
                    after_val = after.get(key, 'N/A')
                    lines.append(f"- 📦 **{key}:** {before_val} → {after_val}")
                lines.append("")

        # Footer
        lines.extend([
            "",
            "=" * 60,
            "",
            f"✅ **Relatório gerado em** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ])

        return "\n".join(lines)

    def save_structured_results(self, output_dir: str) -> Dict[str, str]:
        """Save structured results to separate files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        saved_files = {}

        if not self.raw_result:
            print("⚠️ No raw result to save")
            return saved_files

        # Extract and save step results
        step_results = self.extract_step_results()

        for step_name, data in step_results.items():
            if data:
                file_path = output_path / f"{step_name}-result.json"
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    saved_files[step_name] = str(file_path)
                    print(f"✅ Saved {step_name} to {file_path}")
                except Exception as e:
                    print(f"❌ Failed to save {step_name}: {e}")

        # Save summary report
        try:
            summary_report = self.generate_summary_report()
            report_path = output_path / "modernization-report.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(summary_report)
            saved_files['report'] = str(report_path)
            print(f"✅ Saved report to {report_path}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")

        return saved_files