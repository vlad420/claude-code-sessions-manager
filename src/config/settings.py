import os
from dataclasses import dataclass
from pathlib import Path

from ..domain.exceptions import ConfigurationError


@dataclass(frozen=True)
class Settings:
    session_duration_hours: int = 5
    session_file_path: str = "session.json"
    claude_timeout_seconds: int = 10
    max_turns: int = 1
    output_format: str = "json"

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables with defaults."""
        try:
            return cls(
                session_duration_hours=int(os.getenv("SESSION_DURATION_HOURS", "5")),
                session_file_path=os.getenv("SESSION_FILE_PATH", "session.json"),
                claude_timeout_seconds=int(os.getenv("CLAUDE_TIMEOUT_SECONDS", "10")),
                max_turns=int(os.getenv("CLAUDE_MAX_TURNS", "1")),
                output_format=os.getenv("CLAUDE_OUTPUT_FORMAT", "json"),
            )
        except (ValueError, TypeError) as e:
            raise ConfigurationError(f"Invalid configuration value: {e}")

    @classmethod
    def default(cls) -> "Settings":
        """Create default settings."""
        return cls()

    def get_session_file_path(self) -> Path:
        """Get the session file path as a Path object."""
        return Path(self.session_file_path)

    def validate(self) -> None:
        """Validate the configuration settings."""
        if self.session_duration_hours <= 0:
            raise ConfigurationError("Session duration must be positive")
        
        if self.claude_timeout_seconds <= 0:
            raise ConfigurationError("Claude timeout must be positive")
        
        if self.max_turns <= 0:
            raise ConfigurationError("Max turns must be positive")
        
        if self.output_format not in ["json", "text"]:
            raise ConfigurationError("Output format must be 'json' or 'text'")


def get_settings() -> Settings:
    """Get application settings, trying environment variables first."""
    settings = Settings.from_env()
    settings.validate()
    return settings