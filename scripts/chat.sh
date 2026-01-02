#!/usr/bin/env bash
set -euo pipefail

# Check aichat availability
if ! command -v aichat &>/dev/null; then
    echo "Error: aichat is not installed."
    echo "Install: https://github.com/sigoden/aichat#installation"
    exit 1
fi

# Check if custom role exists
AICHAT_ROLE="${AICHAT_ROLE:-tmux-bot-assistant}"
role_file="$HOME/.config/aichat/roles/${AICHAT_ROLE}.md"

if [ -f "$role_file" ]; then
    # Role exists - use it
    exec aichat --session tmux-bot -r "$AICHAT_ROLE"
else
    # Role doesn't exist - start without role (use default behavior)
    exec aichat --session tmux-bot
fi
