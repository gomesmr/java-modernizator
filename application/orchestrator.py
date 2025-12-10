"""
Execution orchestrator
"""
from typing import Optional

from domain.entities import ExecutionResult, StepResult
from domain.enums.execution_mode import ExecutionMode
from application.steps import (
    CloneStep,
    CollectionStep,
    ProcessingStep,
    CallbackStep,
    ResultStep
)
from config.settings import settings


class ExecutionOrchestrator:
    """Orchestrates the execution flow"""

    def __init__(self, mode: ExecutionMode, dev_execution_id: Optional[str] = None):
        self.mode = mode
        self.dev_execution_id = dev_execution_id
        self.result = ExecutionResult()

    def execute(self) -> ExecutionResult:
        """
        Execute the complete flow based on mode

        Returns:
            ExecutionResult with complete execution data
        """
        if self.mode.is_dev:
            return self._execute_dev_mode()
        return self._execute_prod_mode()

    def _execute_dev_mode(self) -> ExecutionResult:
        """Execute development mode (steps 4-5 only)"""
        print("\n⚡ Development Mode: Skipping Steps 1-3")

        # Step 4: Fetch callback
        callback_step = CallbackStep()
        callback_result = callback_step.execute(self.dev_execution_id)

        if not callback_result.success:
            self.result.success = False
            self.result.error = callback_result.error
            return self.result

        self.result.execution_id = self.dev_execution_id
        self.result.callback_file = callback_result.data['callback_file']

        # Step 5: Process results
        result_step = ResultStep()
        processing_result = result_step.execute(callback_result.data['callback_file'])

        if processing_result.success:
            self.result.results_directory = processing_result.data['output_dir']
            self.result.success = True
        else:
            self.result.error = processing_result.error

        return self.result

    def _execute_prod_mode(self) -> ExecutionResult:
        """Execute production mode (all steps)"""
        # Step 1: Clone repository
        clone_result = self._execute_clone_step()
        if not clone_result.success:
            return self.result

        # Step 2: Collect files
        collection_result = self._execute_collection_step(clone_result.data)
        if not collection_result.success:
            return self.result

        # Step 3: Process with StackSpot
        processing_result = self._execute_processing_step(collection_result.data)
        if not processing_result.success:
            return self.result

        # Step 4: Fetch callback
        callback_result = self._execute_callback_step(
            processing_result.data['execution_id']
        )
        if not callback_result.success:
            return self.result

        # Step 5: Process results
        result_step_result = self._execute_result_step(
            callback_result.data['callback_file']
        )

        self.result.success = result_step_result.success
        if not result_step_result.success:
            self.result.error = result_step_result.error

        return self.result

    def _execute_clone_step(self) -> StepResult:
        """Execute clone step"""
        clone_step = CloneStep(wsl_enabled=False)
        result = clone_step.execute()

        if result.success:
            self.result.cloned_repo_path = result.data
        else:
            self.result.success = False
            self.result.error = result.error

        return result

    def _execute_collection_step(self, repo_path: str) -> StepResult:
        """Execute collection step"""
        collection_step = CollectionStep()
        result = collection_step.execute(repo_path)

        if result.success:
            self.result.payload_file = result.data
        else:
            self.result.success = False
            self.result.error = result.error

        return result

    def _execute_processing_step(self, payload_file: str) -> StepResult:
        """Execute processing step"""
        processing_step = ProcessingStep()
        result = processing_step.execute(payload_file)

        if result.success:
            self.result.execution_id = result.data['execution_id']
        else:
            self.result.success = False
            self.result.error = result.error

        return result

    def _execute_callback_step(self, execution_id: str) -> StepResult:
        """Execute callback step"""
        callback_step = CallbackStep()
        result = callback_step.execute(execution_id)

        if result.success:
            self.result.callback_file = result.data['callback_file']
        else:
            self.result.success = False
            self.result.error = result.error

        return result

    def _execute_result_step(self, callback_file: str) -> StepResult:
        """Execute result processing step"""
        result_step = ResultStep()
        result = result_step.execute(callback_file)

        if result.success:
            self.result.results_directory = result.data['output_dir']
        else:
            self.result.success = False
            self.result.error = result.error

        return result