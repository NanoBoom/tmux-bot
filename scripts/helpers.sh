#!/usr/bin/env bash

# Include guard
[ -n "$_TMUX_BOT_HELPERS_LOADED" ] && return
_TMUX_BOT_HELPERS_LOADED=1

# Helper functions for tmux-bot plugin

# Get the current script directory
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Source variables
source "$(dirname "${BASH_SOURCE[0]}")/variables.sh"

get_tmux_option() {
  local option=$1
  local default_value=$2
  local option_value=$(tmux show-option -gqv "$option")
  if [ -z "$option_value" ]; then
    echo "$default_value"
  else
    echo "$option_value"
  fi
}

set_tmux_option() {
  local option=$1
  local value=$2
  tmux set-option -gq "$option" "$value"
}

# Check for required dependencies
check_dependencies() {
  local missing_deps=()

  if ! command -v jq &>/dev/null; then
    missing_deps+=("jq")
  fi

  if ! command -v curl &>/dev/null; then
    missing_deps+=("curl")
  fi

  if [ ${#missing_deps[@]} -gt 0 ]; then
    tmux display-message "Error: Missing required dependencies: ${missing_deps[*]}"
    return 1
  fi

  return 0
}

# Display error message
display_error() {
  local message="$1"
  tmux display-message "Error: $message"
}

# Display info message
display_info() {
  local message="$1"
  tmux display-message "Info: $message"
}

# Get current operating system
get_os() {
  case "$(uname -s)" in
  Darwin)
    echo "macOS"
    ;;
  Linux)
    echo "Linux"
    ;;
  CYGWIN* | MINGW* | MSYS*)
    echo "Windows"
    ;;
  *)
    echo "Unknown"
    ;;
  esac
}

# Get current shell environment
get_shell() {
  if [ -n "$BASH_VERSION" ]; then
    echo "bash"
  elif [ -n "$ZSH_VERSION" ]; then
    echo "zsh"
  else
    echo "$(basename "$SHELL")"
  fi
}

# Parse template string with variables
parse_template() {
  local template="$1"
  local os="$2"
  local shell="$3"
  local user_prompt="$4"

  # Replace template variables (use // for global replace)
  template="${template//\{OS\}/$os}"
  template="${template//\{SHELL\}/$shell}"
  template="${template//\{USER_PROMPT\}/$user_prompt}"

  echo "$template"
}

# Show spinner animation in tmux status bar.
# Using 'tmux display-message' is the recommended way to show progress for
# scripts running from 'command-prompt' as it does not interfere with the user's pane.
show_spinner() {
  local pid=$1
  local delay=0.2
  # Array of spinner characters
  local spinstr=("⣾" "⣽" "⣻" "⢿" "⡿" "⣟" "⣯" "⣷")

  local index=0
  local length=${#spinstr[@]}

  while ps -p "$pid" >/dev/null 2>&1; do
    local char="${spinstr[$index]}"
    tmux display-message -F "#[fg=blue] $char #[fg=default]Thinking of the perfect command..."
    index=$(((index + 1) % length))
    sleep $delay
  done

  tmux display-message -d 10 "" # Clear the message
}

# Check if a key binding is already set
# Returns 0 if key is available, 1 if already bound
# Usage: key_binding_not_set "v" && tmux bind-key v command
key_binding_not_set() {
    local key="$1"

    # 检查 prefix 表中是否已有该键的绑定
    # 使用 awk 精确匹配第 4 列（键位置），避免误匹配 command 内容
    if tmux list-keys -T prefix 2>/dev/null | awk -v key="$key" 'BEGIN {found=0} $4 == key {found=1; exit} END {exit !found}'; then
        return 1  # Key is already bound
    else
        return 0  # Key is available
    fi
}

# Check if tmux version meets minimum requirement
# Usage: tmux_version_ok "1.9" || die "Requires tmux 1.9+"
tmux_version_ok() {
    local required_version="$1"
    local current_version

    # 提取版本号（去除字母后缀，如 "3.2a" -> "3.2"）
    current_version=$(tmux -V 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)

    if [ -z "$current_version" ]; then
        return 1  # tmux not found or version unparseable
    fi

    # 使用 awk 比较版本号（浮点数比较）
    awk -v cur="$current_version" -v req="$required_version" \
        'BEGIN { exit (cur < req) }'
}
