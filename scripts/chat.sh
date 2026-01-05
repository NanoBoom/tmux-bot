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

# Start aichat with user arguments
exec aichat "$@"
