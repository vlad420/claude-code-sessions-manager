# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based Claude Pro session manager that automates the creation and tracking of Claude sessions to optimize usage of 5-hour windows. The system manages session lifecycle through automated scheduling and provides status tracking.

## Running the Application

```bash
python main.py start-now    # Start a new session
python main.py status       # Check current session status
python main.py start-now -f # Force start new session (override active session)
```

## Development Commands

### Linting and Type Checking
```bash
ruff check .                # Run linting
ruff format .               # Format code
basedpyright               # Type checking
```

### Testing
```bash
python run_tests.py             # Run all tests
python run_tests.py -v 1        # Run with less verbose output
python run_tests.py -q          # Run with minimal output
python run_tests.py -m test_models  # Run specific test module
```

### Dependencies
```bash
pip install -r requirements.txt  # Install dependencies (rich for formatting)
```

### Installation (Alternative)
```bash
# Install with pipx (recommended)
brew install pipx
pipx ensurepath   # apoi deschide un shell nou
pipx install .
# After installation, use: claude-sessions instead of python main.py
```

## Architecture

The codebase follows a clean architecture pattern with clear separation of concerns:

- **Domain Layer** (`src/domain/`): Core business models and exceptions
- **Infrastructure Layer** (`src/infrastructure/`): External dependencies (Claude CLI client, file storage)
- **Services Layer** (`src/services/`): Business logic (SessionManager)
- **Config Layer** (`src/config/`): Application settings and configuration
- **Utils Layer** (`src/utils/`): Formatting utilities

## Key Components

### SessionManager (`src/services/session_manager.py`)
Central service that orchestrates session activation, status checking, and lifecycle management. Key methods:
- `activate_session()`: Creates new session by testing Claude CLI and storing session data
- `get_session_info()`: Retrieves current session with updated status
- `is_session_active()`: Checks if session is still within 5-hour window

### ClaudeClient (`src/infrastructure/claude_client.py`)
Handles communication with Claude CLI using subprocess calls. Configured for single-turn interactions with JSON output format.

### Session Model (`src/domain/models.py`)
Immutable dataclass representing session state with automatic status calculation based on expiration time.

### FileSessionStorage (`src/infrastructure/storage.py`)
JSON-based persistence for session data. Stores session in `session.json` file by default.

## Configuration

Settings are managed through environment variables with defaults:
- `SESSION_DURATION_HOURS`: Session window duration (default: 5)
- `SESSION_FILE_PATH`: Session storage file path (default: "session.json")
- `CLAUDE_TIMEOUT_SECONDS`: Claude CLI timeout (default: 10)
- `CLAUDE_MAX_TURNS`: Max conversation turns (default: 1)
- `CLAUDE_OUTPUT_FORMAT`: Output format (default: "json")

## Dependencies

- Python standard library + rich (for terminal formatting)
- Requires Claude CLI to be installed and available in PATH
- Uses subprocess to interact with `claude` command

## Session Flow

1. Test Claude CLI availability with `claude --help`
2. Send activation message to Claude CLI
3. Create session with 5-hour expiration
4. Store session data in JSON file
5. Display formatted session information

The system is designed for macOS with plans for LaunchAgent integration for automated scheduling.

## Important Development Notes

- After any refactoring or code changes, verify and fix errors using `ruff` and `basedpyright`, then run `python run_tests.py` to verify tests
- The CLI supports Romanian language for user-facing messages
- Session data is persisted in JSON format for simplicity and readability