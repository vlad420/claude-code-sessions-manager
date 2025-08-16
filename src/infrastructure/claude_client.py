import json
import subprocess
from typing import Any

from ..config.settings import Settings
from ..domain.exceptions import ClaudeClientError


class ClaudeClient:
    """Client for interacting with Claude CLI."""

    def __init__(self, settings: Settings):
        self.settings: Settings = settings

    def send_message(self, message: str) -> dict[str, Any]:
        """Send a message to Claude CLI and return the response."""
        cmd = [
            "claude",
            "-p", message,
            "--max-turns", str(self.settings.max_turns),
            "--output-format", self.settings.output_format,
        ]

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                timeout=self.settings.claude_timeout_seconds,
            )
            
            if not result.stdout.strip():
                raise ClaudeClientError("Empty response from Claude CLI")

            return self._parse_response(result.stdout.strip())

        except subprocess.TimeoutExpired as e:
            raise ClaudeClientError(f"Claude CLI timeout after {self.settings.claude_timeout_seconds}s: {e}")
        except subprocess.CalledProcessError as e:
            raise ClaudeClientError(f"Claude CLI error: {e}")
        except Exception as e:
            raise ClaudeClientError(f"Unexpected error calling Claude CLI: {e}")

    def _parse_response(self, raw_output: str) -> dict[str, Any]:
        """Parse the raw output from Claude CLI."""
        try:
            response = json.loads(raw_output)
            self._verify_response(response)
            return response
        except json.JSONDecodeError as e:
            raise ClaudeClientError(f"Invalid JSON response from Claude CLI: {e}")

    def _verify_response(self, response: dict[str, Any]) -> None:
        """Verify that the Claude response is valid."""
        if not isinstance(response, dict):
            raise ClaudeClientError("Response is not a valid JSON object")
        
        if response.get("is_error", False):
            error_message = response.get("result", "Unknown error")
            raise ClaudeClientError(f"Claude returned error: {error_message}")

    def test_connection(self) -> bool:
        """Test if Claude CLI is available and working without consuming usage."""
        try:
            result = subprocess.run(
                ["claude", "--help"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            return False


def create_claude_client(settings: Settings) -> ClaudeClient:
    """Factory function to create Claude client."""
    return ClaudeClient(settings)