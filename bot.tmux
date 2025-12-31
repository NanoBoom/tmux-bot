#!/usr/bin/env bash

# Get the directory where the plugin is located
PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source helpers for key_binding_not_set and get_tmux_option functions
source "$PLUGIN_DIR/scripts/helpers.sh"

set_keybind() {
  local default_key="v"
  local custom_key
  custom_key=$(get_tmux_option "@tmux_bot_key" "$default_key")

  # 检查键绑定冲突
  if key_binding_not_set "$custom_key"; then
    tmux bind-key "$custom_key" command-prompt -p "Ask AI assistant:" \
      "run-shell \"$PLUGIN_DIR/scripts/suggest.sh '%1'\""
  else
    tmux display-message -d 3000 "Warning: Key '$custom_key' already bound, tmux-bot not activated. Set @tmux_bot_key to use different key."
  fi
}

# Cleanup old log files
cleanup_old_logs() {
  local log_dir="/tmp/tmux-bot-logs"
  [ -d "$log_dir" ] || return 0
  # Delete log files older than 7 days (silent failure)
  find "$log_dir" -name "*.log" -mtime +7 -delete 2>/dev/null || true
}

main() {
  # 检查 tmux 版本（command-prompt -p 需要 1.9+）
  if ! tmux_version_ok "1.9"; then
    local current_version
    current_version=$(tmux -V 2>/dev/null)
    tmux display-message -d 5000 "Error: tmux-bot requires tmux 1.9 or higher. Current version: $current_version"
    return 1
  fi

  cleanup_old_logs
  set_keybind
}

main
