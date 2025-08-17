import dataclasses
import os
import unittest
import unittest.mock
from pathlib import Path

from src.claude_code_session_manager.config.settings import Settings, get_settings, get_default_session_file_path
from src.claude_code_session_manager.domain.exceptions import ConfigurationError
from tests.utils.test_helpers import BaseTestCase


class TestSettings(BaseTestCase):
    def test_default_settings_values(self):
        settings = Settings.default()

        self.assertEqual(settings.session_duration_hours, 5)
        self.assertEqual(settings.session_file_path, get_default_session_file_path())
        self.assertEqual(settings.claude_timeout_seconds, 10)
        self.assertEqual(settings.max_turns, 1)
        self.assertEqual(settings.output_format, "json")

    def test_settings_is_immutable(self):
        settings = Settings.default()

        with self.assertRaises((AttributeError, dataclasses.FrozenInstanceError)):
            settings.session_duration_hours = 10  # type: ignore

    def test_custom_settings_values(self):
        settings = Settings(
            session_duration_hours=8,
            session_file_path="custom.json",
            claude_timeout_seconds=30,
            max_turns=3,
            output_format="text",
        )

        self.assertEqual(settings.session_duration_hours, 8)
        self.assertEqual(settings.session_file_path, "custom.json")
        self.assertEqual(settings.claude_timeout_seconds, 30)
        self.assertEqual(settings.max_turns, 3)
        self.assertEqual(settings.output_format, "text")

    def test_get_session_file_path_returns_path_object(self):
        settings = Settings(session_file_path="test/path.json")

        path = settings.get_session_file_path()

        self.assertIsInstance(path, Path)
        self.assertEqual(str(path), "test/path.json")

    def test_validate_success_with_valid_settings(self):
        settings = Settings(
            session_duration_hours=5,
            claude_timeout_seconds=10,
            max_turns=1,
            output_format="json",
        )

        # Should not raise any exception
        settings.validate()

    def test_validate_raises_error_for_negative_session_duration(self):
        settings = Settings(session_duration_hours=-1)

        with self.assertRaises(ConfigurationError) as context:
            settings.validate()

        self.assertIn("Session duration must be positive", str(context.exception))

    def test_validate_raises_error_for_zero_session_duration(self):
        settings = Settings(session_duration_hours=0)

        with self.assertRaises(ConfigurationError) as context:
            settings.validate()

        self.assertIn("Session duration must be positive", str(context.exception))

    def test_validate_raises_error_for_negative_timeout(self):
        settings = Settings(claude_timeout_seconds=-5)

        with self.assertRaises(ConfigurationError) as context:
            settings.validate()

        self.assertIn("Claude timeout must be positive", str(context.exception))

    def test_validate_raises_error_for_zero_timeout(self):
        settings = Settings(claude_timeout_seconds=0)

        with self.assertRaises(ConfigurationError) as context:
            settings.validate()

        self.assertIn("Claude timeout must be positive", str(context.exception))

    def test_validate_raises_error_for_negative_max_turns(self):
        settings = Settings(max_turns=-1)

        with self.assertRaises(ConfigurationError) as context:
            settings.validate()

        self.assertIn("Max turns must be positive", str(context.exception))

    def test_validate_raises_error_for_zero_max_turns(self):
        settings = Settings(max_turns=0)

        with self.assertRaises(ConfigurationError) as context:
            settings.validate()

        self.assertIn("Max turns must be positive", str(context.exception))

    def test_validate_raises_error_for_invalid_output_format(self):
        settings = Settings(output_format="xml")

        with self.assertRaises(ConfigurationError) as context:
            settings.validate()

        self.assertIn("Output format must be 'json' or 'text'", str(context.exception))

    def test_validate_accepts_json_output_format(self):
        settings = Settings(output_format="json")

        # Should not raise
        settings.validate()

    def test_validate_accepts_text_output_format(self):
        settings = Settings(output_format="text")

        # Should not raise
        settings.validate()


class TestSettingsFromEnv(unittest.TestCase):
    original_env: dict[str, str | None]

    def __init__(self, *args: str, **kwargs: str) -> None:
        super().__init__(*args, **kwargs)
        self.original_env = {}

    def setUp(self) -> None:
        # Store original environment values
        env_vars = [
            "SESSION_DURATION_HOURS",
            "SESSION_FILE_PATH",
            "CLAUDE_TIMEOUT_SECONDS",
            "CLAUDE_MAX_TURNS",
            "CLAUDE_OUTPUT_FORMAT",
        ]
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]

    def tearDown(self) -> None:
        # Restore original environment values
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    def test_from_env_uses_defaults_when_no_env_vars(self):
        settings = Settings.from_env()

        self.assertEqual(settings.session_duration_hours, 5)
        self.assertEqual(settings.session_file_path, get_default_session_file_path())
        self.assertEqual(settings.claude_timeout_seconds, 10)
        self.assertEqual(settings.max_turns, 1)
        self.assertEqual(settings.output_format, "json")

    def test_from_env_uses_environment_variables(self):
        os.environ["SESSION_DURATION_HOURS"] = "8"
        os.environ["SESSION_FILE_PATH"] = "custom.json"
        os.environ["CLAUDE_TIMEOUT_SECONDS"] = "30"
        os.environ["CLAUDE_MAX_TURNS"] = "3"
        os.environ["CLAUDE_OUTPUT_FORMAT"] = "text"

        settings = Settings.from_env()

        self.assertEqual(settings.session_duration_hours, 8)
        self.assertEqual(settings.session_file_path, "custom.json")
        self.assertEqual(settings.claude_timeout_seconds, 30)
        self.assertEqual(settings.max_turns, 3)
        self.assertEqual(settings.output_format, "text")

    def test_from_env_partial_environment_variables(self):
        os.environ["SESSION_DURATION_HOURS"] = "10"
        os.environ["CLAUDE_OUTPUT_FORMAT"] = "text"
        # Other values should use defaults

        settings = Settings.from_env()

        self.assertEqual(settings.session_duration_hours, 10)
        self.assertEqual(settings.session_file_path, get_default_session_file_path())  # default
        self.assertEqual(settings.claude_timeout_seconds, 10)  # default
        self.assertEqual(settings.max_turns, 1)  # default
        self.assertEqual(settings.output_format, "text")

    def test_from_env_raises_error_for_invalid_integer(self):
        os.environ["SESSION_DURATION_HOURS"] = "not_an_integer"

        with self.assertRaises(ConfigurationError) as context:
            Settings.from_env()

        self.assertIn("Invalid configuration value", str(context.exception))

    def test_from_env_raises_error_for_invalid_timeout_integer(self):
        os.environ["CLAUDE_TIMEOUT_SECONDS"] = "invalid"

        with self.assertRaises(ConfigurationError) as context:
            Settings.from_env()

        self.assertIn("Invalid configuration value", str(context.exception))

    def test_from_env_raises_error_for_invalid_max_turns_integer(self):
        os.environ["CLAUDE_MAX_TURNS"] = "not_a_number"

        with self.assertRaises(ConfigurationError) as context:
            Settings.from_env()

        self.assertIn("Invalid configuration value", str(context.exception))


class TestGetSettings(unittest.TestCase):
    original_env: dict[str, str | None]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_env = {}

    def setUp(self) -> None:
        # Store original environment values
        self.original_env = {}
        env_vars = [
            "SESSION_DURATION_HOURS",
            "SESSION_FILE_PATH",
            "CLAUDE_TIMEOUT_SECONDS",
            "CLAUDE_MAX_TURNS",
            "CLAUDE_OUTPUT_FORMAT",
        ]
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]

    def tearDown(self) -> None:
        # Restore original environment values
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    def test_get_settings_returns_validated_settings(self):
        settings = get_settings()

        # Should not raise any exception and return valid settings
        self.assertIsInstance(settings, Settings)
        self.assertEqual(settings.session_duration_hours, 5)

    def test_get_settings_with_environment_variables(self):
        os.environ["SESSION_DURATION_HOURS"] = "7"
        os.environ["SESSION_FILE_PATH"] = "env.json"

        settings = get_settings()

        self.assertEqual(settings.session_duration_hours, 7)
        self.assertEqual(settings.session_file_path, "env.json")

    def test_get_settings_raises_configuration_error_for_invalid_values(self):
        os.environ["SESSION_DURATION_HOURS"] = "-1"

        with self.assertRaises(ConfigurationError):
            get_settings()

    def test_get_settings_raises_configuration_error_for_invalid_format(self):
        os.environ["CLAUDE_OUTPUT_FORMAT"] = "invalid_format"

        with self.assertRaises(ConfigurationError):
            get_settings()


class TestSettingsIntegration(unittest.TestCase):
    """Integration tests for Settings functionality."""

    def test_settings_workflow_from_creation_to_validation(self):
        # Create settings from environment
        with unittest.mock.patch.dict(
            os.environ,
            {
                "SESSION_DURATION_HOURS": "6",
                "CLAUDE_TIMEOUT_SECONDS": "15",
                "CLAUDE_OUTPUT_FORMAT": "text",
            },
        ):
            settings = Settings.from_env()

        # Validate the settings
        settings.validate()

        # Use the settings
        file_path = settings.get_session_file_path()

        # Verify everything works together
        self.assertEqual(settings.session_duration_hours, 6)
        self.assertEqual(settings.claude_timeout_seconds, 15)
        self.assertEqual(settings.output_format, "text")
        self.assertIsInstance(file_path, Path)


if __name__ == "__main__":
    unittest.main()

