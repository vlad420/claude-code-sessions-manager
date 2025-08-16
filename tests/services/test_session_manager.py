import unittest
import unittest.mock
from datetime import datetime, timedelta

from src.config.settings import Settings
from src.domain.exceptions import SessionNotFoundError, ClaudeClientError
from src.domain.models import SessionStatus
from src.services.session_manager import SessionManager
from tests.utils.test_helpers import BaseTestCase, TestDataFactory, MockHelper


class TestSessionManager(BaseTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings: Settings
        self.mock_storage: unittest.mock.Mock
        self.mock_claude_client: unittest.mock.Mock
        self.session_manager: SessionManager

    def setUp(self) -> None:
        super().setUp()
        self.settings = TestDataFactory.create_test_settings()
        self.mock_storage = MockHelper.mock_storage()
        self.mock_claude_client = MockHelper.mock_claude_client()
        self.session_manager = SessionManager(
            storage=self.mock_storage,
            claude_client=self.mock_claude_client,
            settings=self.settings
        )

    def test_activate_session_success(self):
        with unittest.mock.patch(
            'src.services.session_manager.datetime'
        ) as mock_datetime:
            mock_datetime.now.return_value = self.now
            
            session = self.session_manager.activate_session()
            
            # Verify Claude client was tested and called
            self.mock_claude_client.test_connection.assert_called_once()
            self.mock_claude_client.send_message.assert_called_once_with(
                "Hello, Claude!"
            )
            
            # Verify session creation
            self.assertEqual(session.created_at, self.now)
            expected_expires = self.now + timedelta(
                hours=self.settings.session_duration_hours
            )
            self.assertEqual(session.expires_at, expected_expires)
            self.assertEqual(session.status, SessionStatus.ACTIVE)
            
            # Verify session was saved
            self.mock_storage.save.assert_called_once_with(session)

    def test_activate_session_fails_when_claude_not_available(self):
        self.mock_claude_client.test_connection.return_value = False
        
        with self.assertRaises(ClaudeClientError) as context:
            self.session_manager.activate_session()
        
        self.assertIn("Claude CLI is not available", str(context.exception))
        self.mock_claude_client.send_message.assert_not_called()
        self.mock_storage.save.assert_not_called()

    def test_activate_session_fails_when_claude_message_fails(self):
        self.mock_claude_client.send_message.side_effect = ClaudeClientError(
            "Connection failed"
        )
        
        with self.assertRaises(ClaudeClientError) as context:
            self.session_manager.activate_session()
        
        self.assertIn("Nu s-a putut activa sesiunea", str(context.exception))
        self.mock_storage.save.assert_not_called()

    def test_get_current_session_returns_session_when_exists(self):
        expected_session = TestDataFactory.create_active_session()
        self.mock_storage.load.return_value = expected_session
        
        session = self.session_manager.get_current_session()
        
        self.assertEqual(session, expected_session)
        self.mock_storage.load.assert_called_once()

    def test_get_current_session_returns_none_when_no_session(self):
        self.mock_storage.load.return_value = None
        
        session = self.session_manager.get_current_session()
        
        self.assertIsNone(session)

    def test_get_session_info_returns_updated_session(self):
        stored_session = TestDataFactory.create_active_session(
            created_hours_ago=2, 
            expires_hours_from_now=3
        )
        self.mock_storage.load.return_value = stored_session
        
        with MockHelper.mock_datetime_now(self.now):
            session = self.session_manager.get_session_info()
            
            # Verify session data is preserved
            self.assertEqual(session.created_at, stored_session.created_at)
            self.assertEqual(session.expires_at, stored_session.expires_at)
            
            # Verify updated session was saved
            self.mock_storage.save.assert_called_once()
            saved_session = self.mock_storage.save.call_args[0][0]
            self.assertEqual(saved_session.created_at, stored_session.created_at)
            self.assertEqual(saved_session.expires_at, stored_session.expires_at)

    def test_get_session_info_raises_when_no_session(self):
        self.mock_storage.load.return_value = None
        
        with self.assertRaises(SessionNotFoundError) as context:
            self.session_manager.get_session_info()
        
        self.assertIn("Nu există o sesiune activă", str(context.exception))

    def test_is_session_active_returns_true_for_active_session(self):
        active_session = TestDataFactory.create_active_session()
        self.mock_storage.load.return_value = active_session
        
        with MockHelper.mock_datetime_now(self.now):
            result = self.session_manager.is_session_active()
            
            self.assertTrue(result)

    def test_is_session_active_returns_false_for_expired_session(self):
        expired_session = TestDataFactory.create_expired_session()
        self.mock_storage.load.return_value = expired_session
        
        with MockHelper.mock_datetime_now(self.now):
            result = self.session_manager.is_session_active()
            
            self.assertFalse(result)

    def test_is_session_active_returns_false_when_no_session(self):
        self.mock_storage.load.return_value = None
        
        result = self.session_manager.is_session_active()
        
        self.assertFalse(result)

    def test_delete_session_calls_storage_delete(self):
        self.session_manager.delete_session()
        
        self.mock_storage.delete.assert_called_once()

    def test_session_manager_with_custom_settings(self):
        custom_settings = TestDataFactory.create_test_settings(
            session_duration_hours=10,
            claude_timeout_seconds=30
        )
        session_manager = SessionManager(
            storage=self.mock_storage,
            claude_client=self.mock_claude_client,
            settings=custom_settings
        )
        
        with unittest.mock.patch(
            'src.services.session_manager.datetime'
        ) as mock_datetime:
            mock_datetime.now.return_value = self.now
            
            session = session_manager.activate_session()
            
            # Verify custom duration is used
            expected_expires = self.now + timedelta(hours=10)
            self.assertEqual(session.expires_at, expected_expires)


class TestSessionManagerIntegration(unittest.TestCase):
    """
    Integration tests for SessionManager with real dependencies 
    but controlled environment.
    """

    def test_activate_and_get_session_flow(self):
        """Test the complete flow of activating and retrieving a session."""
        settings = TestDataFactory.create_test_settings()
        mock_storage = MockHelper.mock_storage()
        mock_claude_client = MockHelper.mock_claude_client()
        
        session_manager = SessionManager(
            storage=mock_storage,
            claude_client=mock_claude_client,
            settings=settings
        )
        
        # Activate session
        with unittest.mock.patch(
            'src.services.session_manager.datetime'
        ) as mock_datetime:
            test_time = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = test_time
            
            activated_session = session_manager.activate_session()
            
            # Mock storage to return the activated session
            mock_storage.load.return_value = activated_session
            
            # Get session info
            retrieved_session = session_manager.get_session_info()
            
            # Verify consistency
            self.assertEqual(activated_session.created_at, retrieved_session.created_at)
            self.assertEqual(activated_session.expires_at, retrieved_session.expires_at)


if __name__ == '__main__':
    unittest.main()