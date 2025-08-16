import tempfile
import unittest.mock
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from src.claude_code_session_manager.config.settings import Settings
from src.claude_code_session_manager.domain.models import Session, SessionStatus
from src.claude_code_session_manager.infrastructure.claude_client import ClaudeClient
from src.claude_code_session_manager.infrastructure.storage import FileSessionStorage


class TestDataFactory:
    """Factory for creating test data objects."""

    @staticmethod
    def create_datetime(offset_hours: int = 0) -> datetime:
        """Create a datetime with optional hour offset from a fixed base time."""
        base_time = datetime(2024, 1, 1, 12, 0, 0)
        return base_time + timedelta(hours=offset_hours)

    @staticmethod
    def create_active_session(
        created_hours_ago: int = 1, expires_hours_from_now: int = 4
    ) -> Session:
        """Create an active session with specified timing."""
        created_at = TestDataFactory.create_datetime(-created_hours_ago)
        expires_at = TestDataFactory.create_datetime(expires_hours_from_now)
        return Session.create_active(created_at=created_at, expires_at=expires_at)

    @staticmethod
    def create_expired_session(
        created_hours_ago: int = 6, expired_hours_ago: int = 1
    ) -> Session:
        """Create an expired session with specified timing."""
        created_at = TestDataFactory.create_datetime(-created_hours_ago)
        expires_at = TestDataFactory.create_datetime(-expired_hours_ago)
        return Session(
            created_at=created_at, expires_at=expires_at, status=SessionStatus.EXPIRED
        )

    @staticmethod
    def create_test_settings(**overrides: int | str) -> Settings:
        """Create test settings with optional overrides."""
        defaults = {
            "session_duration_hours": 5,
            "session_file_path": "test_session.json",
            "claude_timeout_seconds": 10,
            "max_turns": 1,
            "output_format": "json",
        }
        defaults.update(overrides)
        return Settings(
            session_duration_hours=int(defaults["session_duration_hours"]),
            session_file_path=str(defaults["session_file_path"]),
            claude_timeout_seconds=int(defaults["claude_timeout_seconds"]),
            max_turns=int(defaults["max_turns"]),
            output_format=str(defaults["output_format"]),
        )

    @staticmethod
    def create_claude_response(
        content: str = "Hello!", is_error: bool = False
    ) -> dict[str, str | bool | int | dict[str, int]]:
        """Create a mock Claude CLI response."""
        return {"result": content, "is_error": is_error, "usage": {"tokens": 10}}


class MockHelper:
    """Helper for creating common mocks."""

    @staticmethod
    def mock_claude_client(
        response_data: dict[str, str | bool | int | dict[str, int]] | None = None,
    ) -> unittest.mock.Mock:
        """Create a mocked Claude client."""
        mock_client = unittest.mock.Mock(spec=ClaudeClient)
        mock_client.test_connection.return_value = True

        if response_data is None:
            response_data = TestDataFactory.create_claude_response()

        mock_client.send_message.return_value = response_data
        return mock_client

    @staticmethod
    def mock_storage(session: Session | None = None) -> unittest.mock.Mock:
        """Create a mocked storage."""
        mock_storage = unittest.mock.Mock(spec=FileSessionStorage)
        mock_storage.load.return_value = session
        mock_storage.exists.return_value = session is not None
        return mock_storage

    @staticmethod
    def mock_datetime_now(fixed_time: datetime | None = None):
        """Create a context manager that mocks datetime.now()."""
        if fixed_time is None:
            fixed_time = TestDataFactory.create_datetime()

        mock_datetime = unittest.mock.Mock()
        mock_datetime.now.return_value = fixed_time
        return unittest.mock.patch(
            "src.claude_code_session_manager.domain.models.datetime", mock_datetime
        )


class TempFileHelper:
    """Helper for working with temporary files in tests."""

    @staticmethod
    def create_temp_dir() -> tempfile.TemporaryDirectory[str]:
        """Create a temporary directory for test files."""
        return tempfile.TemporaryDirectory()

    @staticmethod
    def create_temp_file_path(suffix: str = ".json") -> Path:
        """Create a temporary file path without creating the file."""
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        temp_file.close()
        path = Path(temp_file.name)
        path.unlink()  # Remove the file, keep only the path
        return path


class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and utilities."""

    def __init__(self, *args: str, **kwargs: str) -> None:
        super().__init__(*args, **kwargs)
        self.test_data: TestDataFactory
        self.mock_helper: MockHelper
        self.temp_helper: TempFileHelper
        self.now: datetime
        self.past_time: datetime
        self.future_time: datetime

    def setUp(self) -> None:
        """Set up common test fixtures."""
        self.test_data = TestDataFactory()
        self.mock_helper = MockHelper()
        self.temp_helper = TempFileHelper()

        # Common test times
        self.now = TestDataFactory.create_datetime()
        self.past_time = TestDataFactory.create_datetime(-1)
        self.future_time = TestDataFactory.create_datetime(1)

    def assert_session_equal(self, session1: Session, session2: Session):
        """Assert that two sessions are equal."""
        self.assertEqual(session1.created_at, session2.created_at)
        self.assertEqual(session1.expires_at, session2.expires_at)
        self.assertEqual(session1.status, session2.status)

