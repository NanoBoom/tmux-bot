#!/bin/bash

# Source the helpers script
source scripts/helpers.sh

# Test the spinner function in tmux environment
echo "Testing tmux spinner function..."

# Start a background process
sleep 10 &
bg_pid=$!

# Show spinner while the process runs
show_spinner $bg_pid

echo "Tmux spinner test completed!"

