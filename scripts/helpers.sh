#!/usr/bin/env bash

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

  # Replace template variables
  template="${template/(OS)/$os}"
  template="${template/(SHELL)/$shell}"
  template="${template/(USER_PROMPT)/$user_prompt}"

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
    tmux display-message " $char Thinking of the perfect command..."
    index=$(((index + 1) % length))
    sleep $delay
  done

  tmux display-message -d 10 "" # Clear the message
}
