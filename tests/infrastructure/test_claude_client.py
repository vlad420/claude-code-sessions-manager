import json
import subprocess
import unittest
import unittest.mock

from src.claude_code_session_manager.config.settings import Settings
from src.claude_code_session_manager.domain.exceptions import ClaudeClientError
from src.claude_code_session_manager.infrastructure.claude_client import (
    ClaudeClient,
    create_claude_client,
)
from tests.utils.test_helpers import BaseTestCase, TestDataFactory


class TestClaudeClient(BaseTestCase):
    settings: Settings
    client: ClaudeClient

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = TestDataFactory.create_test_settings()
        self.client = ClaudeClient(self.settings)

    def setUp(self) -> None:
        super().setUp()
        self.settings = TestDataFactory.create_test_settings()
        self.client = ClaudeClient(self.settings)

    @unittest.mock.patch("subprocess.run")
    def test_send_message_success(self, mock_run):
        response_data = TestDataFactory.create_claude_response("Hello back!")
        mock_run.return_value.stdout = json.dumps(response_data)

        result = self.client.send_message("Hello Claude!")

        # Verify subprocess was called with correct arguments
        expected_cmd = [
            "claude",
            "-p",
            "Hello Claude!",
            "--max-turns",
            str(self.settings.max_turns),
            "--output-format",
            self.settings.output_format,
        ]
        mock_run.assert_called_once_with(
            expected_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            timeout=self.settings.claude_timeout_seconds,
        )

        self.assertEqual(result, response_data)

    @unittest.mock.patch("subprocess.run")
    def test_send_message_with_custom_settings(self, mock_run):
        custom_settings = TestDataFactory.create_test_settings(
            max_turns=3, output_format="text", claude_timeout_seconds=30
        )
        client = ClaudeClient(custom_settings)

        response_data = TestDataFactory.create_claude_response()
        mock_run.return_value.stdout = json.dumps(response_data)

        client.send_message("Test message")

        # Verify custom settings are used
        expected_cmd = [
            "claude",
            "-p",
            "Test message",
            "--max-turns",
            "3",
            "--output-format",
            "text",
        ]
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        self.assertEqual(call_args[0][0], expected_cmd)
        self.assertEqual(call_args[1]["timeout"], 30)

    @unittest.mock.patch("subprocess.run")
    def test_send_message_handles_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("claude", 10)

        with self.assertRaises(ClaudeClientError) as context:
            self.client.send_message("Hello")

        self.assertIn("Claude CLI timeout after 10s", str(context.exception))

    @unittest.mock.patch("subprocess.run")
    def test_send_message_handles_process_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "claude", "Error output"
        )

        with self.assertRaises(ClaudeClientError) as context:
            self.client.send_message("Hello")

        self.assertIn("Claude CLI error", str(context.exception))

    @unittest.mock.patch("subprocess.run")
    def test_send_message_handles_empty_response(self, mock_run):
        mock_run.return_value.stdout = ""

        with self.assertRaises(ClaudeClientError) as context:
            self.client.send_message("Hello")

        self.assertIn("Empty response from Claude CLI", str(context.exception))

    @unittest.mock.patch("subprocess.run")
    def test_send_message_handles_whitespace_only_response(self, mock_run):
        mock_run.return_value.stdout = "   \n\t  "

        with self.assertRaises(ClaudeClientError) as context:
            self.client.send_message("Hello")

        self.assertIn("Empty response from Claude CLI", str(context.exception))

    @unittest.mock.patch("subprocess.run")
    def test_send_message_handles_generic_exception(self, mock_run):
        mock_run.side_effect = RuntimeError("Unexpected error")

        with self.assertRaises(ClaudeClientError) as context:
            self.client.send_message("Hello")

        self.assertIn("Unexpected error calling Claude CLI", str(context.exception))

    @unittest.mock.patch("subprocess.run")
    def test_parse_response_valid_json(self, mock_run):
        response_data = TestDataFactory.create_claude_response()
        mock_run.return_value.stdout = json.dumps(response_data)

        result = self.client.send_message("Hello")

        self.assertEqual(result, response_data)

    @unittest.mock.patch("subprocess.run")
    def test_parse_response_invalid_json(self, mock_run):
        mock_run.return_value.stdout = "not valid json"

        with self.assertRaises(ClaudeClientError) as context:
            self.client.send_message("Hello")

        self.assertIn("Invalid JSON response from Claude CLI", str(context.exception))

    @unittest.mock.patch("subprocess.run")
    def test_verify_response_handles_error_response(self, mock_run):
        error_response = TestDataFactory.create_claude_response(
            content="Something went wrong", is_error=True
        )
        mock_run.return_value.stdout = json.dumps(error_response)

        with self.assertRaises(ClaudeClientError) as context:
            self.client.send_message("Hello")

        self.assertIn(
            "Claude returned error: Something went wrong", str(context.exception)
        )

    @unittest.mock.patch("subprocess.run")
    def test_verify_response_handles_error_without_result(self, mock_run):
        error_response = {"is_error": True}
        mock_run.return_value.stdout = json.dumps(error_response)

        with self.assertRaises(ClaudeClientError) as context:
            self.client.send_message("Hello")

        self.assertIn("Claude returned error: Unknown error", str(context.exception))

    @unittest.mock.patch("subprocess.run")
    def test_test_connection_success(self, mock_run):
        mock_run.return_value.returncode = 0

        result = self.client.test_connection()

        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["claude", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )

    @unittest.mock.patch("subprocess.run")
    def test_test_connection_failure_return_code(self, mock_run):
        mock_run.return_value.returncode = 1

        result = self.client.test_connection()

        self.assertFalse(result)

    @unittest.mock.patch("subprocess.run")
    def test_test_connection_handles_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired("claude", 5)

        result = self.client.test_connection()

        self.assertFalse(result)

    @unittest.mock.patch("subprocess.run")
    def test_test_connection_handles_file_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError("claude not found")

        result = self.client.test_connection()

        self.assertFalse(result)

    @unittest.mock.patch("subprocess.run")
    def test_test_connection_handles_process_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "claude")

        result = self.client.test_connection()

        self.assertFalse(result)

    def test_claude_client_stores_settings(self):
        """Test that ClaudeClient properly stores settings."""
        self.assertEqual(self.client.settings, self.settings)

    @unittest.mock.patch("subprocess.run")
    def test_send_message_strips_response(self, mock_run):
        """Test that response is properly stripped of whitespace."""
        response_data = TestDataFactory.create_claude_response()
        mock_run.return_value.stdout = f"  {json.dumps(response_data)}  \n"

        result = self.client.send_message("Hello")

        self.assertEqual(result, response_data)


class TestClaudeClientFactory(unittest.TestCase):
    """Test the factory function for creating ClaudeClient."""

    def test_create_claude_client_returns_claude_client_instance(self):
        settings = TestDataFactory.create_test_settings()

        client = create_claude_client(settings)

        self.assertIsInstance(client, ClaudeClient)
        self.assertEqual(client.settings, settings)


class TestClaudeClientIntegration(BaseTestCase):
    """Integration tests for ClaudeClient behavior patterns."""

    settings: Settings
    client: ClaudeClient

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = TestDataFactory.create_test_settings()
        self.client = ClaudeClient(self.settings)

    def setUp(self) -> None:
        super().setUp()
        self.settings = TestDataFactory.create_test_settings()
        self.client = ClaudeClient(self.settings)

    @unittest.mock.patch("subprocess.run")
    def test_multiple_messages_use_consistent_settings(self, mock_run):
        """Test that multiple message calls use the same settings."""
        response_data = TestDataFactory.create_claude_response()
        mock_run.return_value.stdout = json.dumps(response_data)

        self.client.send_message("First message")
        self.client.send_message("Second message")

        # Verify both calls used the same settings
        self.assertEqual(mock_run.call_count, 2)
        for call in mock_run.call_args_list:
            cmd = call[0][0]
            self.assertIn("--max-turns", cmd)
            self.assertIn(str(self.settings.max_turns), cmd)
            self.assertIn("--output-format", cmd)
            self.assertIn(self.settings.output_format, cmd)

    @unittest.mock.patch("subprocess.run")
    def test_connection_test_does_not_affect_message_sending(self, mock_run):
        """Test that connection test doesn't interfere with message sending."""
        # First call for test_connection
        mock_run.return_value.returncode = 0
        connection_result = self.client.test_connection()

        # Second call for send_message
        response_data = TestDataFactory.create_claude_response()
        mock_run.return_value.stdout = json.dumps(response_data)
        message_result = self.client.send_message("Hello")

        self.assertTrue(connection_result)
        self.assertEqual(message_result, response_data)
        self.assertEqual(mock_run.call_count, 2)


if __name__ == "__main__":
    unittest.main()

