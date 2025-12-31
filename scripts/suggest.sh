#!/usr/bin/env bash

# Source helper functions FIRST
source "$(dirname "${BASH_SOURCE[0]}")/helpers.sh"
source "$(dirname "${BASH_SOURCE[0]}")/variables.sh"

# Check dependencies IMMEDIATELY (before any other operations)
if ! check_dependencies; then
  exit 1
fi

# Get user prompt
USER_PROMPT="$1"
if [ -z "$USER_PROMPT" ]; then
    tmux display-message "Error: No prompt provided"
    exit 1
fi

# Get system information
CURRENT_OS=$(get_os)
CURRENT_SHELL=$(get_shell)
PARSED_SYSTEM_PROMPT=$(parse_template "$SYSTEM_PROMPT" "$CURRENT_OS" "$CURRENT_SHELL" "")

# === Configuration Validation Function ===
validate_config() {
    local api_key="$1"
    local base_url="$2"

    # 检查 API key 是否配置（必填）
    if [ -z "$api_key" ]; then
        tmux display-message -d 5000 -F "#[fg=red]Error: API key not configured. Set @openai_api_key in .tmux.conf or export OPENAI_API_KEY"
        return 1
    fi

    # 检查 URL 格式（警告级别）
    if ! echo "$base_url" | grep -qE '^https?://'; then
        tmux display-message -d 3000 -F "#[fg=yellow]Warning: Base URL should start with http:// or https://"
    fi

    return 0
}

# Get from tmux options
tmux_base_url=$(get_tmux_option "@openai_base_url" "$DEFAULT_BASE_URL")
tmux_api_key=$(get_tmux_option "@openai_api_key" "")
tmux_model=$(get_tmux_option "@openai_model" "$DEFAULT_MODEL")

# Validate configuration before proceeding
validate_config "$tmux_api_key" "$tmux_base_url" || exit 1

api_url="$tmux_base_url/chat/completions"

# Create log directory if it doesn't exist
LOG_DIR="/tmp/tmux-bot-logs"
mkdir -p "$LOG_DIR"

# Generate log filename with timestamp
LOG_FILE="$LOG_DIR/curl_command_$(date +%Y%m%d_%H%M%S).log"

# Create unique temporary file for API response
TEMP_RESPONSE=$(mktemp "${TMPDIR:-/tmp}/tmux-bot-response.XXXXXX")

# Define cleanup function (safe even if CURL_PID is undefined)
cleanup() {
    [ -n "${CURL_PID:-}" ] && kill "$CURL_PID" 2>/dev/null
    rm -f "$TEMP_RESPONSE"
}

# Set trap for all exit scenarios
trap cleanup EXIT INT TERM

# Escape JSON strings for proper formatting
ESCAPED_SYSTEM_PROMPT=$(printf '%s' "$PARSED_SYSTEM_PROMPT" | jq -Rs .)
ESCAPED_USER_PROMPT=$(printf '%s' "$USER_PROMPT" | jq -Rs .)

# Construct the JSON payload using a HEREDOC
read -r -d '' JSON_PAYLOAD <<EOF
{
  "model": "$tmux_model",
  "stream": false,
  "messages": [
    {
      "role": "system",
      "content": $ESCAPED_SYSTEM_PROMPT
    },
    {
      "role": "user",
      "content": $ESCAPED_USER_PROMPT
    }
  ],
  "temperature": $TEMPERATURE,
  "max_tokens": $MAX_TOKENS,
  "top_p": $TOP_P,
  "frequency_penalty": $FREQUENCY_PENALTY,
  "presence_penalty": $PRESENCE_PENALTY
}
EOF

# Log the curl command to file (with API key redacted)
{
    echo "curl -X POST \"$api_url\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -H \"Authorization: Bearer ***REDACTED***\" \\"
    echo "  -d \"$JSON_PAYLOAD\""
    echo ""
    echo "Full JSON payload:"
    echo "$JSON_PAYLOAD"
} >"$LOG_FILE"

# Make the API call in background and show spinner animation
curl -X POST "$api_url" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $tmux_api_key" \
  -d "$JSON_PAYLOAD" >"$TEMP_RESPONSE" 2>/dev/null &
CURL_PID=$!

# Show spinner animation while waiting for API response
show_spinner $CURL_PID

# Wait for curl to finish and get the exit status
wait $CURL_PID
CURL_EXIT=$?

# Parse the response if curl succeeded
if [ $CURL_EXIT -eq 0 ]; then
  AI_COMMAND=$(jq -r '.choices[0].message.content' "$TEMP_RESPONSE" 2>/dev/null)
  JQ_EXIT=$?

  # Check jq parsing result
  if [ $JQ_EXIT -ne 0 ]; then
      tmux display-message -d 3000 -F "#[fg=red]Error: Failed to parse API response (invalid JSON)"
      exit 1
  fi

  # Check if jq returned null or empty
  if [ -z "$AI_COMMAND" ] || [ "$AI_COMMAND" = "null" ]; then
      tmux display-message "AI did not return a valid command for the prompt: $USER_PROMPT"
      exit 1
  fi
else
  tmux display-message "API request failed, please check network connection and API configuration"
  exit 1
fi

# Check if command was denied for safety reasons
if [ "$AI_COMMAND" = "DENIED" ]; then
  tmux display-message -F "#[fg=red] Dangerous operation detected. Command generating denied."
  exit 0
fi

# Check if command contains "Ambiguous" and display the full message
if echo "$AI_COMMAND" | grep -q "Ambiguous"; then
  tmux display-message -F "#[fg=yellow] $AI_COMMAND"
  exit 0
fi

# Clear any existing input in the current line first
tmux send-keys C-u

# Send the extracted command to the current tmux pane.
# The -l flag ensures the command is inserted literally, character by character.
tmux send-keys -l -- "$AI_COMMAND"
