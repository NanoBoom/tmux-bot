#!/usr/bin/env bash
# Fix multiple aichat instances issue
# This script applies the fix automatically

set -euo pipefail

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  tmux-bot Multi-Instance Fix Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if tmux is running
if ! tmux info &>/dev/null; then
  echo "Error: tmux is not running. Start tmux first."
  exit 1
fi

# Step 1: Check current configuration
echo "[1/4] Checking current configuration..."
current_format=$(tmux show -gv @popup-id-format 2>/dev/null || echo "default")
echo "  Current @popup-id-format: $current_format"

current_binding=$(tmux list-keys -T root | grep 'M-t' | head -1 || echo "none")
echo "  Current Alt+t binding: $current_binding"

popup_sessions=$(tmux -L popup list-sessions 2>/dev/null | wc -l || echo "0")
echo "  Popup sessions count: $popup_sessions"
echo ""

# Step 2: Apply fix
echo "[2/4] Applying fix..."
tmux set -gF @popup-id-format "{popup_name}"
echo "  ✓ Set @popup-id-format to {popup_name}"

# Get plugin directory
plugin_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
chat_script="$plugin_dir/scripts/chat.sh"

tmux bind -n M-t run "#{@popup-toggle} -w85% -h85% --name=aichat '${chat_script}'"
echo "  ✓ Updated Alt+t keybinding with --name=aichat"
echo ""

# Step 3: Clean up old sessions
echo "[3/4] Cleaning up old popup sessions..."
if [ "$popup_sessions" -gt 0 ]; then
  echo "  Found $popup_sessions old sessions."
  read -p "  Delete all old popup sessions? [y/N] " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    tmux -L popup kill-server 2>/dev/null || true
    echo "  ✓ Deleted all old sessions"
  else
    echo "  Skipped cleanup (you can manually run: tmux -L popup kill-server)"
  fi
else
  echo "  No old sessions found"
fi
echo ""

# Step 4: Verify fix
echo "[4/4] Verifying fix..."
new_format=$(tmux show -gv @popup-id-format)
new_binding=$(tmux list-keys -T root | grep 'M-t')

if [[ "$new_format" == "{popup_name}" ]]; then
  echo "  ✓ @popup-id-format is correct"
else
  echo "  ✗ @popup-id-format verification failed: $new_format"
fi

if echo "$new_binding" | grep -q -- "--name=aichat"; then
  echo "  ✓ Keybinding includes --name=aichat"
else
  echo "  ✗ Keybinding verification failed"
fi
echo ""

# Instructions
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Fix Applied Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Test by pressing Alt+t in different directories"
echo "  2. Verify only one session exists:"
echo "     tmux -L popup list-sessions"
echo ""
echo "To make this permanent, add to ~/.tmux.conf:"
echo "  set -gF @popup-id-format \"{popup_name}\""
echo ""
echo "See FIX_MULTI_INSTANCE.md for detailed documentation."
