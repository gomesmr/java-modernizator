"""
Client for Stackspot AI API
"""
import json
import requests
from pathlib import Path
from typing import Optional, Callable

from domain.exceptions import CredentialsNotFoundError, StackspotApiError


class StackspotApiClient:
    """Client for interacting with Stackspot AI API"""

    def __init__(self, credentials_path: str):
        self.credentials = self._load_credentials(credentials_path)
        self.client = self._initialize_client()
        self.access_token = None

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
            client = Stackspot(self.credentials)
            # Obter token de acesso para chamadas diretas à API
            self._get_access_token()
            return client
        except ImportError:
            raise StackspotApiError(
                "Stackspot SDK not installed. Run: pip install stackspot-sdk"
            )
        except Exception as e:
            raise StackspotApiError(
                f"Failed to initialize Stackspot client: {e}"
            )

    def _get_access_token(self):
        """Get access token for direct API calls"""
        try:
            # Usar o SDK para obter o token
            self.access_token = self.client.get_access_token()
            print(f"✅ Access token obtained")
        except Exception as e:
            print(f"⚠️ Could not get access token: {e}")
            self.access_token = None

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
            print(f"   🔗 Execution ID: {execution_id}")

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

    def get_callback_result(self, execution_id: str) -> Optional[dict]:
        """
        Get callback result using direct API call

        Args:
            execution_id: The execution ID returned from execute_quick_command

        Returns:
            Dictionary with the callback result or None if not available
        """
        if not self.access_token:
            print("⚠️ No access token available for callback API")
            return None

        try:
            print(f"\n{'=' * 60}")
            print(f"📞 Fetching Callback Result")
            print(f"{'=' * 60}")
            print(f"🔗 Execution ID: {execution_id}")

            url = f"https://genai-code-buddy-api.stackspot.com/v1/quick-commands/callback/{execution_id}"

            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'User-Agent': 'modern-jazz/1.0.0',
                'Accept': 'application/json'
            }

            print(f"🌐 URL: {url}")

            response = requests.get(url, headers=headers, timeout=30)

            print(f"📊 Status Code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Callback result retrieved successfully")
                print(f"📝 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                return result
            elif response.status_code == 404:
                print(f"⚠️ Callback not found (404) - may not be ready yet")
                return None
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return None

        except requests.exceptions.Timeout:
            print(f"⏰ Timeout while fetching callback")
            return None
        except requests.exceptions.RequestException as e:
            print(f"🌐 Network error: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None

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