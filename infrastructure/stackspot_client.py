# infrastructure/stackspot_client.py
"""
Client for Stackspot AI API
"""
import json
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
            self.access_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk5YWRmYmI4LWU3ZTEtNDlmNi1iNmFhLTJlYWVlZTYyZDk4ZiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkX3YyIjoiMDFHUlZYTU5WMVAwMjgxTkdXQlg3MUQ3NTIiLCJhY2NvdW50X25hbWUiOiJadXAgSVQgSW5ub3ZhdGlvbiIsImFjY291bnRfc2x1ZyI6Inp1cCIsImFjY291bnRfdHlwZSI6IkVOVEVSUFJJU0UiLCJhdHRyaWJ1dGVzIjp7fSwiYXVkIjpbImM1NDM0MjBmLTk1N2MtNDYwOS1iZTAzLWJmZWM1NDIyZTM4ZCJdLCJhenAiOiIzOTczNGZlMi1mYjEzLTQzMGQtYTJmOC0wMjFjZjI0YjlhZWIiLCJjbGllbnRJZCI6ImM1NDM0MjBmLTk1N2MtNDYwOS1iZTAzLWJmZWM1NDIyZTM4ZCIsImNsaWVudF9pZCI6ImM1NDM0MjBmLTk1N2MtNDYwOS1iZTAzLWJmZWM1NDIyZTM4ZCIsImVtYWlsIjoibWFyY2Vsby5nb21lc0B6dXAuY29tLmJyIiwiZXhwIjoxNzY1Mzk1Nzg3LCJmYW1pbHlfbmFtZSI6IlJlbmF0byBHb21lcyIsImdpdmVuX25hbWUiOiJNYXJjZWxvIiwiaWF0IjoxNzY1Mzk0NTg3LCJpc3MiOiJodHRwczovL2F1dGguc3RhY2tzcG90LmNvbS96dXAvb2lkYyIsImp0aSI6ImlvSXEzNFJxQ3BzZWI2UTJIRTJtc0RDU1JPb1FsTWpXakY4QXdFVmI2UDBnWUthb3pzbTI4VDhadmpmSzZmSEoiLCJuYW1lIjoiTWFyY2VsbyBSZW5hdG8gR29tZXMiLCJuYmYiOjE3NjUzOTQ1ODcsInByZWZlcnJlZF91c2VybmFtZSI6Im1hcmNlbG8uZ29tZXMiLCJyZWFsbSI6Inp1cCIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIiwiZGVmYXVsdCB1c2VyIHJvbGU6IDBlNWY5NmEwLWU4YzQtNDhhOS05MzVmLTNjNDNlZWZlMTc3YiIsImNvZGVfc2hpZnRfZGV2ZWxvcGVyIiwiYWlfZGV2ZWxvcGVyIiwibWVtYmVyIiwiZGV2ZWxvcGVyIiwiY3JlYXRvciIsIjAxR1JWWE1OVjFQMDI4MU5HV0JYNzFENzUyIiwiZGVmYXVsdCBncm91cCByb2xlOiAwY2QxNTYyYS0wMmQwLTRkMGEtOGNmYy1hNDM4N2Q3ODQxZmEiXX0sInJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iLCJkZWZhdWx0IHVzZXIgcm9sZTogMGU1Zjk2YTAtZThjNC00OGE5LTkzNWYtM2M0M2VlZmUxNzdiIiwiY29kZV9zaGlmdF9kZXZlbG9wZXIiLCJhaV9kZXZlbG9wZXIiLCJtZW1iZXIiLCJkZXZlbG9wZXIiLCJjcmVhdG9yIiwiMDFHUlZYTU5WMVAwMjgxTkdXQlg3MUQ3NTIiLCJkZWZhdWx0IGdyb3VwIHJvbGU6IDBjZDE1NjJhLTAyZDAtNGQwYS04Y2ZjLWE0Mzg3ZDc4NDFmYSJdLCJzY29wZSI6ImF0dHJpYnV0ZXMgcm9sZXMgZW1haWwiLCJzdWIiOiJjNTQzNDIwZi05NTdjLTQ2MDktYmUwMy1iZmVjNTQyMmUzOGQiLCJ0ZW5hbnQiOiJ6dXAiLCJ0ZW5hbnRfaWQiOiIzOTczNGZlMi1mYjEzLTQzMGQtYTJmOC0wMjFjZjI0YjlhZWIiLCJ0b2tlblR5cGUiOiJDTElFTlRfU0VSVklDRV9BQ0NPVU5UIiwidG9rZW5fdHlwZSI6IkNMSUVOVF9QRVJTT05BTCIsInVzZXJfaWQiOiIwZTVmOTZhMC1lOGM0LTQ4YTktOTM1Zi0zYzQzZWVmZTE3N2IiLCJ1c2VybmFtZSI6Im1hcmNlbG8uZ29tZXMifQ.Ty_bAw9xNBgtur-YSzICNxM0PB7UWyvirDCFoVXMu-YNl7Mj70kSX3fpVZSD0-x3iPvruPpdFZ_hzXVsJTgf6wkCc5rUkS8T8KFiXtjcOhclfek93-OdRQJnbeMB-GgeH9wsvZ-OqIDpt-q1AcQ1iPQsvgD01zXyQ6OE86sl0EBM7DFRPGa7rFaD4jqeIiuy9rS4YIMRBoJL5q_WIePIBWCsMk1lVvfGK6INRiAfjdP9ywveKOGgsXmwVuCqOKI3pZun_kFFN0jMsI3PVDosznh6kXb2AY_tTCSgcQYVUZV3OiZJWLrtW4RBEgUo6hBnHMLUQY2MnO1EMKMztNhutILOUA9_km37P1G9W0TObbINo2egUA6B1Z_xMjnl_CHt-0_kPJqH6zuGEZzh0hjlL0g4MzQ22Pl8UkpOKeJ8MtwUkI8SRIsnl-xhZTtK2ASmhQwcCxFXy9RMxrR6tdajS6mxvxRAHDrOmepqgL3_oTIkPE7CFh-VsVHnKJ0xuIoZWjffxeF8NhEFSwrTEmqVvTuVO8nAbJeK8lq5j5KJ0z55p5jw07EIbCTgrj4bXDsXRBDVk9eJYc-YeShaGbjPckQDKbrbl5jE38gMDHmoc1SrLR1Nfjyc1zQXHJbmCLAZJU5_XssLwTiZ4bNKYHHN7HiU-QCnajEpSwqbBKfv6Dg"
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
        """Poll for execution result using direct API calls"""

        # Garantir que temos token de acesso
        if not self.access_token:
            self._get_access_token()

        if not self.access_token:
            raise StackspotApiError("No access token available")

        start_time = time.time()
        attempts = 0

        # URL da API para polling
        api_url = f"https://genai-code-buddy-api.stackspot.com/v1/quick-commands/callback/{execution_id}"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json',
            'User-Agent': 'modern-jazz/1.0.0'
        }

        print(f"🔗 Polling execution: {execution_id}")

        while (time.time() - start_time) < timeout:
            attempts += 1

            try:
                response = requests.get(api_url, headers=headers, timeout=30)

                if response.status_code == 200:
                    result = response.json()

                    # Verificar se a execução foi completada
                    progress = result.get('progress', {})
                    status = progress.get('status')

                    print(f"📊 Attempt {attempts}: {status}")

                    if status == 'COMPLETED':
                        print(f"✅ Execution completed in {attempts} attempts")
                        return result

                    elif status in ['FAILED', 'CANCELLED']:
                        error = result.get('error', 'Unknown error')
                        raise StackspotApiError(f"Execution {status}: {error}")

                    # Executar callback se fornecido
                    if status_callback:
                        status_callback(result)

                elif response.status_code == 404:
                    print(f"⏳ Execution not ready yet (attempt {attempts})")

                else:
                    print(f"⚠️ API returned {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                print(f"🌐 Network error on attempt {attempts}: {e}")

            time.sleep(polling_delay)

        raise RQCExecutionTimeoutError(f"Timeout after {timeout} seconds and {attempts} attempts")

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