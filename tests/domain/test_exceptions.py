import unittest

from src.domain.exceptions import (
    SessionManagerError,
    SessionNotFoundError,
    SessionExpiredError,
    StorageError,
    ClaudeClientError,
    ConfigurationError,
)


class TestExceptions(unittest.TestCase):

    def test_session_manager_error_is_base_exception(self):
        exception = SessionManagerError("test message")
        self.assertIsInstance(exception, Exception)
        self.assertEqual(str(exception), "test message")

    def test_session_not_found_error_inherits_from_session_manager_error(self):
        exception = SessionNotFoundError("session not found")
        self.assertIsInstance(exception, SessionManagerError)
        self.assertIsInstance(exception, Exception)
        self.assertEqual(str(exception), "session not found")

    def test_session_expired_error_inherits_from_session_manager_error(self):
        exception = SessionExpiredError("session expired")
        self.assertIsInstance(exception, SessionManagerError)
        self.assertIsInstance(exception, Exception)
        self.assertEqual(str(exception), "session expired")

    def test_storage_error_inherits_from_session_manager_error(self):
        exception = StorageError("storage error")
        self.assertIsInstance(exception, SessionManagerError)
        self.assertIsInstance(exception, Exception)
        self.assertEqual(str(exception), "storage error")

    def test_claude_client_error_inherits_from_session_manager_error(self):
        exception = ClaudeClientError("claude error")
        self.assertIsInstance(exception, SessionManagerError)
        self.assertIsInstance(exception, Exception)
        self.assertEqual(str(exception), "claude error")

    def test_configuration_error_inherits_from_session_manager_error(self):
        exception = ConfigurationError("config error")
        self.assertIsInstance(exception, SessionManagerError)
        self.assertIsInstance(exception, Exception)
        self.assertEqual(str(exception), "config error")

    def test_exceptions_can_be_raised_and_caught(self):
        with self.assertRaises(SessionNotFoundError) as context:
            raise SessionNotFoundError("test session not found")
        
        self.assertEqual(str(context.exception), "test session not found")

    def test_specific_exceptions_can_be_caught_as_base_exception(self):
        with self.assertRaises(SessionManagerError):
            raise SessionNotFoundError("specific error")

        with self.assertRaises(SessionManagerError):
            raise StorageError("storage error")

        with self.assertRaises(SessionManagerError):
            raise ClaudeClientError("client error")


if __name__ == '__main__':
    unittest.main()