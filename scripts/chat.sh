#!/usr/bin/env bash
set -euo pipefail

# Check aichat availability
if ! command -v aichat &>/dev/null; then
  echo "Error: aichat is not installed."
  echo "Install: https://github.com/sigoden/aichat#installation"
  exit 1
fi

# Display welcome message
cat <<'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  tmux-bot AI Chat Assistant
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF

# Start aichat with session persistence
# Users can configure role, model, etc. in aichat's own config
exec aichat --session tmux-bot
