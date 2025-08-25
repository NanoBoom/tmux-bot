#!/usr/bin/env bash

# Get the directory where the plugin is located
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source helper functions
source "$CURRENT_DIR/scripts/variables.sh"
source "$CURRENT_DIR/scripts/helpers.sh"

set_keybind() {
  tmux bind-key v command-prompt -p "Ask AI assistant:" "run-shell \"$CURRENT_DIR/suggest.sh '%1'\" "

  # tmux command-prompt -p "copycat search:" "run-shell \"$CURRENT_DIR/copycat_mode_start.sh '%1'\""
}

main() {
  set_keybind
}

main
