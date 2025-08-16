import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import override

from ..domain.exceptions import StorageError
from ..domain.models import Session


class SessionStorage(ABC):
    """Abstract interface for session storage."""

    @abstractmethod
    def save(self, session: Session) -> None:
        """Save a session."""
        pass

    @abstractmethod
    def load(self) -> Session | None:
        """Load a session. Returns None if no session exists."""
        pass

    @abstractmethod
    def exists(self) -> bool:
        """Check if a session exists."""
        pass

    @abstractmethod
    def delete(self) -> None:
        """Delete the stored session."""
        pass


class FileSessionStorage(SessionStorage):
    """File-based session storage implementation."""

    def __init__(self, file_path: Path):
        self.file_path: Path = file_path

    @override
    def save(self, session: Session) -> None:
        """Save session to JSON file."""
        try:
            session_data = {
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
                "status": session.status.value,
            }
            
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(session_data, file, ensure_ascii=False, indent=4)
                
        except (OSError, IOError) as e:
            raise StorageError(f"Failed to save session: {e}")

    @override
    def load(self) -> Session | None:
        """Load session from JSON file."""
        if not self.exists():
            return None

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                session_data = json.load(file)

            created_at = datetime.fromisoformat(session_data["created_at"])
            expires_at = datetime.fromisoformat(session_data["expires_at"])

            return Session.from_data(created_at=created_at, expires_at=expires_at)

        except (OSError, IOError, json.JSONDecodeError, KeyError, ValueError) as e:
            raise StorageError(f"Failed to load session: {e}")

    @override
    def exists(self) -> bool:
        """Check if session file exists."""
        return self.file_path.exists()

    @override
    def delete(self) -> None:
        """Delete the session file."""
        try:
            if self.exists():
                self.file_path.unlink()
        except OSError as e:
            raise StorageError(f"Failed to delete session: {e}")


def create_file_storage(file_path: Path) -> FileSessionStorage:
    """Factory function to create file storage."""
    return FileSessionStorage(file_path)