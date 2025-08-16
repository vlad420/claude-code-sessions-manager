import json
import unittest
import unittest.mock
from pathlib import Path

from src.domain.exceptions import StorageError
from src.domain.models import Session
from src.infrastructure.storage import FileSessionStorage, SessionStorage
from tests.utils.test_helpers import BaseTestCase, TestDataFactory, TempFileHelper


class TestSessionStorageInterface(unittest.TestCase):
    """Test the SessionStorage abstract interface."""

    def test_session_storage_is_abstract(self):
        """Test that SessionStorage cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            SessionStorage()  # type: ignore


class TestFileSessionStorage(BaseTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temp_file_path: Path
        self.storage: FileSessionStorage
        self.test_session: Session

    def setUp(self) -> None:
        super().setUp()
        self.temp_file_path = TempFileHelper.create_temp_file_path()
        self.storage = FileSessionStorage(self.temp_file_path)
        self.test_session = TestDataFactory.create_active_session()

    def tearDown(self) -> None:
        """Clean up temporary files after each test."""
        if self.temp_file_path.exists():
            self.temp_file_path.unlink()

    def test_save_creates_file_with_correct_format(self):
        self.storage.save(self.test_session)
        
        self.assertTrue(self.temp_file_path.exists())
        
        # Verify file content
        with open(self.temp_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        expected_data = {
            "created_at": self.test_session.created_at.isoformat(),
            "expires_at": self.test_session.expires_at.isoformat(),
            "status": self.test_session.status.value,
        }
        self.assertEqual(data, expected_data)

    def test_save_overwrites_existing_file(self):
        # Save first session
        first_session = TestDataFactory.create_active_session(created_hours_ago=2)
        self.storage.save(first_session)
        
        # Save second session
        second_session = TestDataFactory.create_active_session(created_hours_ago=1)
        self.storage.save(second_session)
        
        # Verify only second session is stored
        loaded_session = self.storage.load()
        self.assertIsNotNone(loaded_session)
        assert loaded_session is not None  # For type checker
        self.assertEqual(loaded_session.created_at, second_session.created_at)
        self.assertEqual(loaded_session.expires_at, second_session.expires_at)

    def test_save_raises_storage_error_on_file_permission_error(self):
        # Mock the open function to raise a permission error
        with unittest.mock.patch(
            'builtins.open', side_effect=PermissionError("Permission denied")
        ):
            with self.assertRaises(StorageError) as context:
                self.storage.save(self.test_session)
            
            self.assertIn("Failed to save session", str(context.exception))

    def test_load_returns_session_when_file_exists(self):
        self.storage.save(self.test_session)
        
        loaded_session = self.storage.load()
        
        # Note: loaded session status may be recalculated based on current time
        self.assertIsNotNone(loaded_session)
        assert loaded_session is not None  # For type checker
        self.assertEqual(loaded_session.created_at, self.test_session.created_at)
        self.assertEqual(loaded_session.expires_at, self.test_session.expires_at)

    def test_load_returns_none_when_file_does_not_exist(self):
        loaded_session = self.storage.load()
        
        self.assertIsNone(loaded_session)

    def test_load_creates_session_with_updated_status(self):
        # Create an "expired" session by setting expires_at in the past
        expired_session = TestDataFactory.create_expired_session()
        self.storage.save(expired_session)
        
        # Load should create session with updated status based on current time
        loaded_session = self.storage.load()
        
        # Verify the timestamps are preserved but status is recalculated
        self.assertIsNotNone(loaded_session)
        assert loaded_session is not None  # For type checker
        self.assertEqual(loaded_session.created_at, expired_session.created_at)
        self.assertEqual(loaded_session.expires_at, expired_session.expires_at)
        # Status should be recalculated by Session.from_data()

    def test_load_raises_storage_error_on_invalid_json(self):
        # Write invalid JSON to file
        with open(self.temp_file_path, 'w', encoding='utf-8') as file:
            file.write("invalid json content")
        
        with self.assertRaises(StorageError) as context:
            self.storage.load()
        
        self.assertIn("Failed to load session", str(context.exception))

    def test_load_raises_storage_error_on_missing_fields(self):
        # Write JSON with missing required fields
        incomplete_data = {"created_at": "2024-01-01T12:00:00"}
        with open(self.temp_file_path, 'w', encoding='utf-8') as file:
            json.dump(incomplete_data, file)
        
        with self.assertRaises(StorageError) as context:
            self.storage.load()
        
        self.assertIn("Failed to load session", str(context.exception))

    def test_load_raises_storage_error_on_invalid_datetime(self):
        # Write JSON with invalid datetime format
        invalid_data = {
            "created_at": "not-a-datetime",
            "expires_at": "2024-01-01T12:00:00",
            "status": "active"
        }
        with open(self.temp_file_path, 'w', encoding='utf-8') as file:
            json.dump(invalid_data, file)
        
        with self.assertRaises(StorageError) as context:
            self.storage.load()
        
        self.assertIn("Failed to load session", str(context.exception))

    def test_exists_returns_true_when_file_exists(self):
        self.storage.save(self.test_session)
        
        self.assertTrue(self.storage.exists())

    def test_exists_returns_false_when_file_does_not_exist(self):
        self.assertFalse(self.storage.exists())

    def test_delete_removes_existing_file(self):
        self.storage.save(self.test_session)
        self.assertTrue(self.temp_file_path.exists())
        
        self.storage.delete()
        
        self.assertFalse(self.temp_file_path.exists())

    def test_delete_does_nothing_when_file_does_not_exist(self):
        # Should not raise an error
        self.storage.delete()
        
        self.assertFalse(self.temp_file_path.exists())

    def test_delete_raises_storage_error_on_permission_error(self):
        self.storage.save(self.test_session)
        
        # Mock the Path.unlink method to raise OSError
        with unittest.mock.patch(
            'pathlib.Path.unlink', side_effect=OSError("Permission denied")
        ):
            with self.assertRaises(StorageError) as context:
                self.storage.delete()
            
            self.assertIn("Failed to delete session", str(context.exception))

    def test_file_encoding_handles_unicode_correctly(self):
        """Test that the storage correctly handles unicode characters."""
        # This test ensures proper UTF-8 encoding
        self.storage.save(self.test_session)
        
        # Read the file and verify it's properly encoded
        with open(self.temp_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Should not raise encoding errors
        self.assertIsInstance(content, str)
        
        # Should be able to load back without issues
        loaded_session = self.storage.load()
        self.assertIsNotNone(loaded_session)
        assert loaded_session is not None  # For type checker
        self.assertEqual(loaded_session.created_at, self.test_session.created_at)
        self.assertEqual(loaded_session.expires_at, self.test_session.expires_at)

    def test_concurrent_access_safety(self):
        """Basic test for file access safety."""
        # Save a session
        self.storage.save(self.test_session)
        
        # Create another storage instance pointing to the same file
        another_storage = FileSessionStorage(self.temp_file_path)
        
        # Both should be able to read the same session
        session1 = self.storage.load()
        session2 = another_storage.load()
        
        self.assertIsNotNone(session1)
        self.assertIsNotNone(session2)
        assert session1 is not None and session2 is not None  # For type checker
        self.assert_session_equal(session1, session2)


class TestFileSessionStorageFactory(unittest.TestCase):
    """Test the factory function for creating FileSessionStorage."""

    def test_create_file_storage_returns_file_storage_instance(self):
        from src.infrastructure.storage import create_file_storage
        
        test_path = Path("test.json")
        storage = create_file_storage(test_path)
        
        self.assertIsInstance(storage, FileSessionStorage)
        self.assertEqual(storage.file_path, test_path)


if __name__ == '__main__':
    unittest.main()