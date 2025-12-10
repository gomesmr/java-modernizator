# infrastructure/stackspot_workflow_client.py
"""
Client using StackSpot Workflows for Quick Commands
"""
import json
import time
import requests
from typing import Optional, Dict, Any


class StackSpotWorkflowClient:
    """Client using StackSpot Workflows API"""

    def __init__(self, credentials_path: str):
        self.credentials = self._load_credentials(credentials_path)
        self.access_token = None
        self._get_access_token()

    def _load_credentials(self, credentials_path: str) -> dict:
        """Load credentials from JSON file"""
        with open(credentials_path, 'r') as f:
            return json.load(f)

    def _get_access_token(self) -> None:
        """Get JWT token for API calls"""
        auth_url = "https://idm.stackspot.com/zup/oidc/oauth/token"

        data = {
            'client_id': self.credentials.get('client_id'),
            'client_secret': self.credentials.get('client_secret'),
            'grant_type': 'client_credentials'
        }

        response = requests.post(auth_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data.get('access_token')
        print("✅ Access token obtained")

    def execute_quick_command_via_workflow(
            self,
            quick_command_slug: str,
            input_data: str,
            conversation_id: Optional[str] = None
    ) -> str:
        """Execute Quick Command via Workflow API"""

        workflow_payload = {
            "workflow": {
                "name": "stackspot-core/quick-command-executor@1.0.0",
                "label": "Execute Quick Command",
                "type": "reusable",
                "inputs": {
                    "quick_command_slug": quick_command_slug,
                    "input_data": input_data,
                    "conversation_id": conversation_id
                }
            }
        }

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        # Dispatch workflow
        dispatch_url = "https://api.stackspot.com/v3/workflows/dispatch"
        response = requests.post(dispatch_url, json=workflow_payload, headers=headers)
        response.raise_for_status()

        execution_data = response.json()
        execution_id = execution_data.get('execution_id')

        print(f"🚀 Workflow dispatched: {execution_id}")
        return execution_id

    def poll_workflow_result(
            self,
            execution_id: str,
            polling_delay: int = 10,
            timeout: int = 600
    ) -> Dict[str, Any]:
        """Poll workflow execution result"""

        start_time = time.time()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        status_url = f"https://api.stackspot.com/v3/workflows/executions/{execution_id}"

        while (time.time() - start_time) < timeout:
            response = requests.get(status_url, headers=headers)
            response.raise_for_status()

            execution = response.json()
            status = execution.get('status')

            print(f"📊 Status: {status}")

            if status == 'COMPLETED':
                # Extract result from workflow outputs
                outputs = execution.get('outputs', {})
                return self._extract_quick_command_result(outputs)

            elif status in ['FAILED', 'CANCELLED']:
                error = execution.get('error', 'Unknown error')
                raise Exception(f"Workflow {status}: {error}")

            time.sleep(polling_delay)

        raise TimeoutError(f"Workflow timeout after {timeout} seconds")

    def _extract_quick_command_result(self, outputs: Dict) -> Dict[str, Any]:
        """Extract Quick Command result from workflow outputs"""
        # Navigate through workflow outputs to find the Quick Command result
        for job_id, job_outputs in outputs.items():
            for step_id, step_output in job_outputs.items():
                if 'answer' in step_output:
                    return step_output

        raise ValueError("No Quick Command result found in workflow outputs")