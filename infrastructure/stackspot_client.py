# infrastructure/stackspot_client.py
"""
Client for Stackspot AI API
"""
import json
import logging
import time

import requests
from pathlib import Path
from typing import Optional, Callable

from domain.exceptions import CredentialsNotFoundError, StackspotApiError, RQCExecutionTimeoutError


class StackspotApiClient:
    """Client for interacting with Stackspot AI API"""

    def __init__(self, credentials_path: str):
        self.credentials = self._load_credentials(credentials_path)
        self.client = None
        self.access_token = None
        self._initialize_client()

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
            self.client = Stackspot(self.credentials)
            # Obter token de acesso para chamadas diretas à API
            self._get_access_token()
            print(f"✅ StackSpot client initialized successfully")
        except ImportError:
            print("⚠️ Stackspot SDK not installed, using direct API calls only")
            self.client = None
        except Exception as e:
            print(f"⚠️ Failed to initialize Stackspot client: {e}")
            self.client = None

    def _get_access_token(self):
        """Get access token for direct API calls"""
        if not self.client:
            print("⚠️ No StackSpot client available for token generation")
            return

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
        if not self.client:
            raise StackspotApiError("StackSpot client not available")

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
            polling_delay: int = 5,
            timeout: int = 600,
            status_callback: Optional[Callable] = None
    ) -> dict:
        """Poll for execution result with enhanced error handling and timeout"""
        logger = logging.getLogger(__name__)

        if not self.client or not hasattr(self.client, 'ai'):
            raise StackspotApiError("StackSpot client not properly initialized")

        start_time = time.time()
        attempts = 0
        last_status = None

        try:
            logger.info(f"Polling execution {execution_id}...")
            print(f"🔗 Tracking execution: /executions/{execution_id}")

            while (time.time() - start_time) < timeout:
                attempts += 1



                execution = self.client.ai.quick_command.get_execution(execution_id)
                current_status = execution.get('status')

                # Status change logging
                if current_status != last_status:
                    logger.debug(f"Status changed to {current_status}")
                    last_status = current_status

                # Handle completion
                if current_status == 'COMPLETED':
                    if 'result' not in execution:
                        raise StackspotApiError("Completed execution missing result field")

                    logger.info(f"Execution completed in {attempts} attempts")
                    return self._parse_execution_result(execution)

                # Handle terminal states
                if current_status in ['FAILED', 'CANCELLED']:
                    error_msg = execution.get('error', 'Unknown error')
                    raise StackspotApiError(f"Execution {current_status}: {error_msg}")

                # Execute callback and wait
                if status_callback:
                    status_callback(execution)

                time.sleep(polling_delay)

            raise RQCExecutionTimeoutError(f"Timeout after {timeout} seconds")

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise StackspotApiError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON response")
            raise StackspotApiError("Failed to parse API response")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    def _parse_execution_result(self, execution: dict) -> dict:
        """Validate and parse execution result"""
        try:
            result = execution['result']

            if isinstance(result, str):
                result = json.loads(result)

            if not isinstance(result, dict):
                raise ValueError("Unexpected result format")

            return result

        except (KeyError, json.JSONDecodeError, ValueError) as e:
            raise StackspotApiError(f"Invalid result format: {str(e)}")

    def get_callback_result(self, execution_id: str) -> Optional[dict]:
        """
        Get callback result using direct API call

        Args:
            execution_id: The execution ID returned from execute_quick_command

        Returns:
            Dictionary with the callback result or None if not available
        """
        # Tentar obter token se não tiver
        if not self.access_token and self.client:
            self._get_access_token()

        if not self.access_token:
            print("⚠️ No access token available for callback API")
            print("💡 Trying to get token using credentials directly...")

            # Fallback: tentar obter token diretamente
            token = self._get_token_direct()
            if token:
                self.access_token = token
            else:
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

    def _get_token_direct(self) -> Optional[str]:
        """Get token using direct API call as fallback"""
        try:
            # URL para obter token (pode variar conforme a API da StackSpot)
            auth_url = "https://idm.stackspot.com/zup/oidc/oauth/token"

            data = {
                'client_id': self.credentials.get('client_id'),
                'client_secret': self.credentials.get('client_secret'),
                'grant_type': 'client_credentials'
            }

            response = requests.post(auth_url, data=data, timeout=30)

            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get('access_token')
                print(f"✅ Token obtained via direct API call")
                return token
            else:
                print(f"❌ Failed to get token: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error getting token directly: {e}")
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