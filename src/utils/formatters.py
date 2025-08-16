from datetime import datetime, timedelta

from ..domain.models import Session, SessionStatus


def format_date(date: datetime) -> str:
    """Format a datetime object to a readable string."""
    return date.strftime("%d-%m-%Y %H:%M:%S")


def format_duration(duration: timedelta) -> str:
    """Format a timedelta object to a readable string."""
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours} ore, {minutes} minute"


def format_session_info(session: Session) -> str:
    """Format session information for display."""
    lines = [
        "Sesiune:",
        f"Started: {format_date(session.created_at)}",
        f"Expiră: {format_date(session.expires_at)}",
        f"Status: {session.status}",
    ]
    
    if session.status == SessionStatus.ACTIVE:
        duration = session.expires_at - datetime.now()
        if duration.total_seconds() > 0:
            lines.append(f"Timp rămas: {format_duration(duration)}")
    
    return "\n".join(lines)


def format_success_message(message: str) -> str:
    """Format a success message."""
    return f"✓ {message}"


def format_error_message(message: str) -> str:
    """Format an error message."""
    return f"✗ {message}"