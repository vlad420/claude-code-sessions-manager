#!/bin/bash

# Uninstall Claude Sessions Scheduler LaunchAgent

set -e

PLIST_NAME="com.claude-sessions.scheduler.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_TARGET="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

echo "🗑️  Uninstalling Claude Sessions Scheduler LaunchAgent..."

# Check if plist exists
if [ ! -f "$PLIST_TARGET" ]; then
    echo "⚠️  LaunchAgent not found at $PLIST_TARGET"
    echo "   It may have already been uninstalled."
    exit 0
fi

# Unload the LaunchAgent
echo "🛑 Unloading LaunchAgent..."
launchctl unload "$PLIST_TARGET" 2>/dev/null || true

# Wait a moment for unloading
sleep 1

# Remove the plist file
echo "🗂️  Removing plist file..."
rm -f "$PLIST_TARGET"

# Check if it's really gone
if ! launchctl list | grep -q "com.claude-sessions.scheduler"; then
    echo "✅ LaunchAgent uninstalled successfully!"
    echo ""
    echo "📝 Note: Log files are preserved at ~/.local/share/claude-sessions/"
    echo "   Remove them manually if desired:"
    echo "   rm -rf ~/.local/share/claude-sessions/"
else
    echo "❌ LaunchAgent may still be running. Try manually:"
    echo "   launchctl remove com.claude-sessions.scheduler"
    exit 1
fi

echo ""
echo "🎉 Uninstallation complete!"