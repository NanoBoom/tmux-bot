#!/usr/bin/env bash

# Source helper functions
source "$(dirname "${BASH_SOURCE[0]}")/helpers.sh"
# Source variables
source "$(dirname "${BASH_SOURCE[0]}")/variables.sh"

# Get user prompt from the first argument
# Remove surrounding quotes if present (from tmux command-prompt)
USER_PROMPT="$1"

# Get current OS and shell information
CURRENT_OS=$(get_os)
CURRENT_SHELL=$(get_shell)

# Parse system prompt template with variables
PARSED_SYSTEM_PROMPT=$(parse_template "$SYSTEM_PROMPT" "$CURRENT_OS" "$CURRENT_SHELL")

# Check for dependencies
if ! check_dependencies; then
  exit 1
fi

# Get from tmux options
tmux_base_url=$(get_tmux_option "@openai_base_url" "$DEFAULT_BASE_URL")
tmux_api_key=$(get_tmux_option "@openai_api_key" "")
tmux_model=$(get_tmux_option "@openai_model" "$DEFAULT_MODEL")

api_url="$tmux_base_url/chat/completions"

# Create log directory if it doesn't exist
LOG_DIR="/tmp/tmux-bot-logs"
mkdir -p "$LOG_DIR"

# Generate log filename with timestamp
LOG_FILE="$LOG_DIR/curl_command_$(date +%Y%m%d_%H%M%S).log"

# Construct the JSON payload using a HEREDOC
read -r -d '' JSON_PAYLOAD <<EOF
{
  "model": "$tmux_model",
  "stream": false,
  "messages": [
    {
      "role": "system",
      "content": "$PARSED_SYSTEM_PROMPT"
    },
    {
      "role": "user",
      "content": "$USER_PROMPT"
    }
  ],
  "temperature": $TEMPERATURE,
  "max_tokens": $MAX_TOKENS,
  "top_p": $TOP_P,
  "frequency_penalty": $FREQUENCY_PENALTY,
  "presence_penalty": $PRESENCE_PENALTY
}
EOF

# Log the curl command to file
echo "curl -X POST \"$api_url\" \\" >"$LOG_FILE"
echo "  -H \"Content-Type: application/json\" \\" >>"$LOG_FILE"
echo "  -H \"Authorization: Bearer $tmux_api_key\" \\" >>"$LOG_FILE"
echo "  -d \"$JSON_PAYLOAD\"" >>"$LOG_FILE"
echo "" >>"$LOG_FILE"
echo "Full JSON payload:" >>"$LOG_FILE"
echo "$JSON_PAYLOAD" >>"$LOG_FILE"

# Make the API call in background and show spinner animation
curl -X POST "$api_url" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $tmux_api_key" \
  -d "$JSON_PAYLOAD" >"/tmp/tmux-bot-response.json" 2>/dev/null &
CURL_PID=$!

# Show spinner animation while waiting for API response
show_spinner $CURL_PID

# Wait for curl to finish and get the exit status
wait $CURL_PID
CURL_EXIT=$?

# Parse the response if curl succeeded
if [ $CURL_EXIT -eq 0 ]; then
  AI_COMMAND=$(jq -r '.choices[0].message.content' "/tmp/tmux-bot-response.json" 2>/dev/null)
  rm -f "/tmp/tmux-bot-response.json"
else
  tmux display-message "API请求失败，请检查网络连接和API配置"
  exit 1
fi

# Check if a command was returned, handle potential null or empty responses
if [ -z "$AI_COMMAND" ] || [ "$AI_COMMAND" = "null" ]; then
  tmux display-message "AI did not return a valid command for the prompt: $USER_PROMPT"
  exit 1
fi

# Check if command was denied for safety reasons
if [ "$AI_COMMAND" = "DENIED" ]; then
  tmux display-message "Dangerous operation detected. Command generating denied."
  exit 1
fi

# Clear any existing input in the current line first
tmux send-keys C-u

# Send the extracted command to the current tmux pane.
# The -l flag ensures the command is inserted literally, character by character.
tmux send-keys -l -- "$AI_COMMAND"
