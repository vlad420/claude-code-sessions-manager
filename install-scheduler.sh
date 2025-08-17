#!/bin/bash

# Install Claude Sessions Scheduler LaunchAgent

set -e

PLIST_NAME="com.claude-sessions.scheduler.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_SOURCE="$(pwd)/$PLIST_NAME"
PLIST_TARGET="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

echo "🔧 Installing Claude Sessions Scheduler LaunchAgent..."

# Check if pipx-installed claude-sessions exists
if ! command -v claude-sessions &> /dev/null; then
    echo "❌ Error: claude-sessions command not found!"
    echo "   Make sure the application is installed via pipx:"
    echo "   pipx install ."
    exit 1
fi

# Check if source plist exists
if [ ! -f "$PLIST_SOURCE" ]; then
    echo "❌ Error: $PLIST_NAME not found in current directory!"
    echo "   Make sure you're running this script from the project root."
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Copy plist file
echo "📂 Copying plist to $LAUNCH_AGENTS_DIR..."
cp "$PLIST_SOURCE" "$PLIST_TARGET"

# Set proper permissions
chmod 644 "$PLIST_TARGET"

# Unload if already loaded (ignore errors)
launchctl unload "$PLIST_TARGET" 2>/dev/null || true

# Load the LaunchAgent
echo "🚀 Loading LaunchAgent..."
launchctl load "$PLIST_TARGET"

# Check if it's loaded
if launchctl list | grep -q "com.claude-sessions.scheduler"; then
    echo "✅ LaunchAgent installed and loaded successfully!"
    echo ""
    echo "📋 The scheduler will:"
    echo "   • Run every 5 minutes"
    echo "   • Check for expired Claude sessions"
    echo "   • Automatically start new sessions when needed"
    echo "   • Log output to ~/.local/share/claude-sessions/"
    echo ""
    echo "📖 Useful commands:"
    echo "   Check status: launchctl list | grep claude-sessions"
    echo "   View logs:    tail -f ~/.local/share/claude-sessions/scheduler.out"
    echo "   View errors:  tail -f ~/.local/share/claude-sessions/scheduler.err"
    echo "   Uninstall:    ./uninstall-scheduler.sh"
else
    echo "❌ Failed to load LaunchAgent. Check the configuration."
    exit 1
fi

echo ""
echo "🎉 Installation complete!"