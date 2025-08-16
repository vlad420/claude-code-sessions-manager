import unittest
import unittest.mock
from datetime import datetime, timedelta

from src.claude_code_session_manager.domain.models import Session, SessionStatus


class TestSession(unittest.TestCase):
    now: datetime
    past_time: datetime
    future_time: datetime

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.now = datetime(2024, 1, 1, 12, 0, 0)
        self.past_time = self.now - timedelta(hours=1)
        self.future_time = self.now + timedelta(hours=1)

    def setUp(self) -> None:
        self.now = datetime(2024, 1, 1, 12, 0, 0)
        self.past_time = self.now - timedelta(hours=1)
        self.future_time = self.now + timedelta(hours=1)

    def test_create_active_creates_active_session(self):
        session = Session.create_active(
            created_at=self.past_time, expires_at=self.future_time
        )

        self.assertEqual(session.created_at, self.past_time)
        self.assertEqual(session.expires_at, self.future_time)
        self.assertEqual(session.status, SessionStatus.ACTIVE)

    def test_from_data_creates_active_session_when_not_expired(self):
        with unittest.mock.patch(
            "src.claude_code_session_manager.domain.models.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = self.now

            session = Session.from_data(
                created_at=self.past_time, expires_at=self.future_time
            )

            self.assertEqual(session.status, SessionStatus.ACTIVE)

    def test_from_data_creates_expired_session_when_expired(self):
        with unittest.mock.patch(
            "src.claude_code_session_manager.domain.models.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = self.now

            session = Session.from_data(
                created_at=self.past_time,
                expires_at=self.past_time,  # Already expired
            )

            self.assertEqual(session.status, SessionStatus.EXPIRED)

    def test_is_active_returns_true_for_active_non_expired_session(self):
        with unittest.mock.patch(
            "src.claude_code_session_manager.domain.models.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = self.now

            session = Session(
                created_at=self.past_time,
                expires_at=self.future_time,
                status=SessionStatus.ACTIVE,
            )

            self.assertTrue(session.is_active)

    def test_is_active_returns_false_for_expired_session(self):
        with unittest.mock.patch(
            "src.claude_code_session_manager.domain.models.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = self.now

            session = Session(
                created_at=self.past_time,
                expires_at=self.past_time,  # Already expired
                status=SessionStatus.ACTIVE,
            )

            self.assertFalse(session.is_active)

    def test_is_active_returns_false_for_expired_status(self):
        with unittest.mock.patch(
            "src.claude_code_session_manager.domain.models.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = self.now

            session = Session(
                created_at=self.past_time,
                expires_at=self.future_time,
                status=SessionStatus.EXPIRED,
            )

            self.assertFalse(session.is_active)

    def test_is_expired_returns_true_when_session_not_active(self):
        with unittest.mock.patch(
            "src.claude_code_session_manager.domain.models.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = self.now

            session = Session(
                created_at=self.past_time,
                expires_at=self.past_time,  # Already expired
                status=SessionStatus.ACTIVE,
            )

            self.assertTrue(session.is_expired)

    def test_is_expired_returns_false_when_session_active(self):
        with unittest.mock.patch(
            "src.claude_code_session_manager.domain.models.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value = self.now

            session = Session(
                created_at=self.past_time,
                expires_at=self.future_time,
                status=SessionStatus.ACTIVE,
            )

            self.assertFalse(session.is_expired)

    def test_session_is_immutable(self):
        session = Session.create_active(
            created_at=self.past_time, expires_at=self.future_time
        )

        with self.assertRaises(AttributeError):
            session.created_at = self.now  # type: ignore


class TestSessionStatus(unittest.TestCase):
    def test_session_status_values(self):
        self.assertEqual(SessionStatus.ACTIVE.value, "active")
        self.assertEqual(SessionStatus.EXPIRED.value, "expired")

    def test_session_status_enum_membership(self):
        self.assertIn(SessionStatus.ACTIVE, SessionStatus)
        self.assertIn(SessionStatus.EXPIRED, SessionStatus)


if __name__ == "__main__":
    unittest.main()
