from datetime import datetime, timedelta

from ..config.settings import Settings
from ..domain.exceptions import SessionNotFoundError, SessionExpiredError, ClaudeClientError
from ..domain.models import Session
from ..infrastructure.claude_client import ClaudeClient
from ..infrastructure.storage import SessionStorage


class SessionManager:
    """Service for managing Claude sessions."""

    def __init__(self, storage: SessionStorage, claude_client: ClaudeClient, settings: Settings):
        self.storage: SessionStorage = storage
        self.claude_client: ClaudeClient = claude_client
        self.settings: Settings = settings

    def activate_session(self) -> Session:
        """Activate a new session by testing Claude connection and creating session."""
        if not self.claude_client.test_connection():
            raise ClaudeClientError("Claude CLI is not available or not working")

        try:
            _ = self.claude_client.send_message("Hello, Claude!")
        except ClaudeClientError as e:
            raise ClaudeClientError(f"Nu s-a putut activa sesiunea: {e}")

        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=self.settings.session_duration_hours)
        
        session = Session.create_active(created_at=created_at, expires_at=expires_at)
        self.storage.save(session)
        
        return session

    def get_current_session(self) -> Session | None:
        """Get the current session, if any."""
        return self.storage.load()

    def get_session_info(self) -> Session:
        """Get session info, raising exception if no session exists."""
        session = self.get_current_session()
        if not session:
            raise SessionNotFoundError("Nu există o sesiune activă.")
        
        # Update session with current status and save
        updated_session = Session.from_data(
            created_at=session.created_at,
            expires_at=session.expires_at
        )
        self.storage.save(updated_session)
        
        return updated_session

    def is_session_active(self) -> bool:
        """Check if there's an active session."""
        session = self.get_current_session()
        return session is not None and session.is_active

    def delete_session(self) -> None:
        """Delete the current session."""
        self.storage.delete()

    def refresh_session(self) -> Session:
        """Refresh an existing session by extending its expiration time."""
        current_session = self.get_current_session()
        if not current_session:
            raise SessionNotFoundError("Nu există o sesiune de reîmprospătat.")

        if current_session.is_expired:
            raise SessionExpiredError("Sesiunea a expirat și nu poate fi reîmprospătată.")

        new_expires_at = datetime.now() + timedelta(hours=self.settings.session_duration_hours)
        refreshed_session = Session.create_active(
            created_at=current_session.created_at,
            expires_at=new_expires_at
        )
        
        self.storage.save(refreshed_session)
        return refreshed_session