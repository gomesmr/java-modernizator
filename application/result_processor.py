# application/result_processor.py
"""
Result processor for StackSpot AI callback results
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """Structured analysis result"""
    timestamp: str
    repository: str
    java_version: str
    spring_boot_version: Optional[str]
    frameworks: List[Dict]
    outdated_dependencies: List[Dict]
    legacy_patterns: List[Dict]
    code_smells: List[Dict]
    architecture_notes: Dict
    summary: str


@dataclass
class PlanResult:
    """Structured plan result"""
    timestamp: str
    strategy: str
    estimated_duration: str
    steps: List[Dict]
    milestones: List[Dict]
    risks: List[Dict]
    recommendations: List[str]


@dataclass
class RefactorResult:
    """Structured refactor result"""
    timestamp: str
    step_id: str
    status: str
    changes: List[Dict]
    issues: List[Dict]
    compilation_status: str
    tests_run: bool
    next_step: str


@dataclass
class MetricsResult:
    """Structured metrics result"""
    metadata: Dict
    execution: Dict
    agents_metrics: Dict
    totals: Dict
    modernization_impact: Dict
    quality_metrics: Dict
    versions: Dict


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
            print(f"📊 Execution ID: {self.raw_result.get('execution_id')}")
            print(f"🎯 Command: {self.raw_result.get('quick_command_slug')}")
            print(f"⏱️ Status: {self.raw_result.get('progress', {}).get('status')}")

            return self.raw_result

        except Exception as e:
            print(f"❌ Error loading callback result: {e}")
            return {}

    def extract_step_results(self) -> Dict[str, Any]:
        """Extract results from each step"""
        if not self.raw_result:
            return {}

        steps = self.raw_result.get('steps', [])
        extracted = {}

        for step in steps:
            step_name = step.get('step_name')
            step_result = step.get('step_result', {})
            answer = step_result.get('answer', '')

            if step_name == 'step-analyze':
                extracted['analysis'] = self._parse_json_answer(answer)
            elif step_name == 'step-plan':
                extracted['plan'] = self._parse_json_answer(answer)
            elif step_name == 'step-refactor':
                extracted['refactor'] = self._parse_json_answer(answer)
            elif step_name == 'step-metrics':
                extracted['metrics'] = self._parse_json_answer(answer)

        return extracted

    def _parse_json_answer(self, answer: str) -> Dict:
        """Parse JSON from step answer"""
        try:
            # Remove markdown code blocks if present
            if '```json' in answer:
                start = answer.find('```json') + 7
                end = answer.find('```', start)
                json_str = answer[start:end].strip()
            else:
                json_str = answer.strip()

            return json.loads(json_str)
        except Exception as e:
            print(f"⚠️ Error parsing JSON answer: {e}")
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

    def generate_summary_report(self) -> str:
        """Generate a comprehensive summary report"""
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

        # Generate report
        report = []
        report.append("🎵 MODERN JAZZ - ANÁLISE COMPLETA")
        report.append("=" * 60)

        # Execution info
        progress = self.raw_result.get('progress', {})
        report.append(f"\n📊 INFORMAÇÕES DA EXECUÇÃO")
        report.append(f"🔗 Execution ID: {self.raw_result.get('execution_id')}")
        report.append(f"🎯 Command: {self.raw_result.get('quick_command_slug')}")
        report.append(f"⏱️ Status: {progress.get('status')}")
        report.append(f"🕐 Duração: {progress.get('duration')} segundos")
        report.append(f"📅 Início: {progress.get('start')}")
        report.append(f"🏁 Fim: {progress.get('end')}")

        # Analysis summary
        if analysis:
            report.append(f"\n🔍 ANÁLISE DO PROJETO")
            report.append(f"📁 Repositório: {analysis.repository}")
            report.append(f"☕ Java Version: {analysis.java_version}")
            report.append(f"🌱 Spring Boot: {analysis.spring_boot_version or 'Não detectado'}")

            report.append(f"\n📚 FRAMEWORKS DESATUALIZADOS ({len(analysis.frameworks)}):")
            for fw in analysis.frameworks:
                status = "❌" if fw.get('isOutdated') else "✅"
                report.append(
                    f"  {status} {fw.get('name')}: {fw.get('currentVersion')} → {fw.get('latestStableVersion')}")

            report.append(f"\n⚠️ PADRÕES LEGADOS ({len(analysis.legacy_patterns)}):")
            for pattern in analysis.legacy_patterns:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(pattern.get('severity'), "⚪")
                report.append(f"  {severity_icon} {pattern.get('type')} - {pattern.get('location')}")

            report.append(f"\n🦨 CODE SMELLS ({len(analysis.code_smells)}):")
            for smell in analysis.code_smells:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(smell.get('severity'), "⚪")
                report.append(f"  {severity_icon} {smell.get('type')} - {smell.get('location')}")

        # Plan summary
        if plan:
            report.append(f"\n📋 PLANO DE MODERNIZAÇÃO")
            report.append(f"🎯 Estratégia: {plan.strategy}")
            report.append(f"⏱️ Duração Estimada: {plan.estimated_duration}")
            report.append(f"📝 Total de Steps: {len(plan.steps)}")

            report.append(f"\n🎯 MILESTONES:")
            for milestone in plan.milestones:
                report.append(f"  📍 {milestone.get('name')}")
                report.append(f"     Steps: {', '.join(milestone.get('completedSteps', []))}")

        # Refactor summary
        if refactor:
            report.append(f"\n🔧 REFATORAÇÃO EXECUTADA")
            report.append(f"📝 Step ID: {refactor.step_id}")
            report.append(f"✅ Status: {refactor.status}")
            report.append(f"🔨 Compilação: {refactor.compilation_status}")
            report.append(f"🧪 Testes Executados: {'Sim' if refactor.tests_run else 'Não'}")

            report.append(f"\n📁 ARQUIVOS MODIFICADOS ({len(refactor.changes)}):")
            for change in refactor.changes:
                report.append(f"  📝 {change.get('file')} - {change.get('description')}")

        # Metrics summary
        if metrics:
            report.append(f"\n📊 MÉTRICAS E IMPACTO")
            totals = metrics.totals
            impact = metrics.modernization_impact

            report.append(f"💰 Custo Total: ${totals.get('total_cost_usd', 0):.3f}")
            report.append(f"🎯 Tokens Consumidos: {totals.get('total_tokens', 0):,}")
            report.append(f"📁 Arquivos Modificados: {impact.get('files_modified', 0)}")
            report.append(f"📦 Dependências Atualizadas: {impact.get('dependencies_updated', 0)}")
            report.append(f"🦨 Code Smells Corrigidos: {impact.get('code_smells_fixed', 0)}")

            versions = metrics.versions
            if 'before' in versions and 'after' in versions:
                report.append(f"\n🔄 VERSÕES (ANTES → DEPOIS):")
                before = versions['before']
                after = versions['after']
                for key in before:
                    report.append(f"  📦 {key}: {before[key]} → {after.get(key, 'N/A')}")

        report.append(f"\n" + "=" * 60)
        report.append(f"✅ Relatório gerado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(report)

    def save_structured_results(self, output_dir: str) -> Dict[str, str]:
        """Save structured results to separate files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        saved_files = {}

        if not self.raw_result:
            return saved_files

        # Extract and save step results
        step_results = self.extract_step_results()

        for step_name, data in step_results.items():
            if data:
                file_path = output_path / f"{step_name}-result.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                saved_files[step_name] = str(file_path)

        # Save summary report
        summary_report = self.generate_summary_report()
        report_path = output_path / "modernization-report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(summary_report)
        saved_files['report'] = str(report_path)

        return saved_files