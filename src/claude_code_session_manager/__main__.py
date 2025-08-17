"""Entry point for the claude-code-session-manager CLI."""

try:
    from claude_code_session_manager.main import main
except ImportError:
    from src.claude_code_session_manager.main import main

if __name__ == "__main__":
    main()

