from src.config.settings import get_settings
from src.domain.exceptions import SessionManagerError, SessionNotFoundError
from src.infrastructure.claude_client import create_claude_client
from src.infrastructure.storage import create_file_storage
from src.services.session_manager import SessionManager
from src.utils.formatters import format_session_info, format_success_message, format_error_message


def main() -> None:
    """Main entry point for the session manager."""
    try:
        # Initialize dependencies
        settings = get_settings()
        storage = create_file_storage(settings.get_session_file_path())
        claude_client = create_claude_client(settings)
        session_manager = SessionManager(storage, claude_client, settings)
        
        # Activate session
        activate_session(session_manager)
        
        # Check session
        check_session(session_manager)
        
    except SessionManagerError as e:
        print(format_error_message(str(e)))
    except Exception as e:
        print(format_error_message(f"Eroare neașteptată: {e}"))


def activate_session(session_manager: SessionManager) -> None:
    """Activate a new session."""
    try:
        _ = session_manager.activate_session()
        print(format_success_message("Sesiune activată cu succes!"))
    except SessionManagerError as e:
        raise e


def check_session(session_manager: SessionManager) -> None:
    """Check and display current session info."""
    try:
        session = session_manager.get_session_info()
        print(format_session_info(session))
    except SessionNotFoundError as e:
        print(str(e))


if __name__ == "__main__":
    main()
