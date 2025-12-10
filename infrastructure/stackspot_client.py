"""
Client for Stackspot AI API
"""
import json
from pathlib import Path
from typing import Optional, Callable

from domain.exceptions import CredentialsNotFoundError, StackspotApiError


class StackspotApiClient:
    """Client for interacting with Stackspot AI API"""

    def __init__(self, credentials_path: str):
        self.credentials = self._load_credentials(credentials_path)
        self.client = self._initialize_client()

    def _load_credentials(self, credentials_path: str) -> dict:
        """Load credentials from JSON file"""
        path = Path(credentials_path)

        if not path.exists():
            raise CredentialsNotFoundError(
                f"Credentials file not found: {credentials_path}"
            )

        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError as e:
            raise CredentialsNotFoundError(
                f"Invalid JSON in credentials file: {e}"
            )

    def _initialize_client(self):
        """Initialize Stackspot SDK client"""
        try:
            from stackspot import Stackspot
            return Stackspot(self.credentials)
        except ImportError:
            raise StackspotApiError(
                "Stackspot SDK not installed. Run: pip install stackspot-sdk"
            )
        except Exception as e:
            raise StackspotApiError(
                f"Failed to initialize Stackspot client: {e}"
            )

    def execute_quick_command(
            self,
            command_slug: str,
            input_content: str
    ) -> str:
        """Execute a quick command and return execution ID"""
        try:
            execution_id = self.client.ai.quick_command.create_execution(
                command_slug,
                input_content
            )
            return execution_id
        except Exception as e:
            raise StackspotApiError(
                f"Failed to execute quick command: {e}"
            )

    def poll_execution_result(
            self,
            execution_id: str,
            polling_delay: int = 23,
            status_callback: Optional[Callable] = None
    ) -> Optional[str]:
        """Poll for execution result"""
        try:
            config = {
                'delay': polling_delay,
                'on_callback_response': status_callback or self._default_callback
            }

            execution = self.client.ai.quick_command.poll_execution(
                execution_id,
                config
            )

            return self._extract_result(execution)
        except Exception as e:
            raise StackspotApiError(
                f"Failed to poll execution result: {e}"
            )

    def _default_callback(self, event: dict) -> None:
        """Default callback for status updates"""
        status = event.get('progress', {}).get('status', 'UNKNOWN')
        print(f"   Status: {status}")

    def _extract_result(self, execution: dict) -> Optional[str]:
        """Extract result from execution response"""
        if execution['progress']['status'] != 'COMPLETED':
            return None

        result = execution.get('result')

        if isinstance(result, dict):
            return (
                    result.get('codigo_java') or
                    result.get('code') or
                    result.get('content')
            )
        elif isinstance(result, str):
            return result

        return None