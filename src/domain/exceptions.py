class SessionManagerError(Exception):
    """Base exception for session manager errors."""
    pass


class SessionNotFoundError(SessionManagerError):
    """Raised when no session is found."""
    pass


class SessionExpiredError(SessionManagerError):
    """Raised when trying to use an expired session."""
    pass


class StorageError(SessionManagerError):
    """Raised when there's an issue with session storage."""
    pass


class ClaudeClientError(SessionManagerError):
    """Raised when there's an issue with Claude CLI interaction."""
    pass


class ConfigurationError(SessionManagerError):
    """Raised when there's an issue with configuration."""
    pass