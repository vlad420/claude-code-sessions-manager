import argparse
from src.config.settings import get_settings
from src.domain.exceptions import SessionManagerError, SessionNotFoundError
from src.infrastructure.claude_client import create_claude_client
from src.infrastructure.storage import create_file_storage
from src.services.session_manager import SessionManager
from src.utils.formatters import format_session_info, format_success_message, format_error_message


def main() -> None:
    """Main entry point for the session manager CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Initialize dependencies
        settings = get_settings()
        storage = create_file_storage(settings.get_session_file_path())
        claude_client = create_claude_client(settings)
        session_manager = SessionManager(storage, claude_client, settings)
        
        # Route to appropriate command
        command: str = args.command
        if command == 'start-now':
            force: bool = getattr(args, 'force', False)
            handle_start_now(session_manager, force)
        elif command == 'status':
            handle_status(session_manager)
        else:
            parser.print_help()
            
    except SessionManagerError as e:
        print(format_error_message(str(e)))
    except Exception as e:
        print(format_error_message(f"Eroare neașteptată: {e}"))


def create_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Manager pentru sesiuni Claude Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comenzi disponibile')
    
    # start-now command
    start_parser = subparsers.add_parser('start-now', help='Pornește o sesiune nouă')
    _ = start_parser.add_argument(
        '-f', '--force', 
        action='store_true',
        help='Forțează crearea unei sesiuni noi indiferent de starea curentă'
    )
    
    # status command
    _ = subparsers.add_parser('status', help='Afișează statusul sesiunii curente')
    
    return parser


def handle_start_now(session_manager: SessionManager, force: bool = False) -> None:
    """Handle the start-now command."""
    if not force and session_manager.is_session_active():
        session = session_manager.get_session_info()
        print("Există deja o sesiune activă:")
        print(format_session_info(session))
        print("\nFolosește -f/--force pentru a forța o sesiune nouă.")
        return
    
    try:
        _ = session_manager.activate_session()
        print(format_success_message("Sesiune activată cu succes!"))
    except SessionManagerError as e:
        raise e


def handle_status(session_manager: SessionManager) -> None:
    """Handle the status command."""
    try:
        session = session_manager.get_session_info()
        print(format_session_info(session))
    except SessionNotFoundError:
        print("Nu există o sesiune activă. Folosește 'start-now' pentru a porni o sesiune nouă.")


if __name__ == "__main__":
    main()
