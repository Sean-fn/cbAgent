#!/bin/bash

# Check if an argument is provided
if [ -z "$1" ]; then
    echo "Error: No argument provided."
    echo "Usage: $0 <argument>"
    exit 1
fi

# Run the command with the first argument
# The "$1" is quoted to handle arguments with spaces correctly
# codex exec --json "$1" --sandbox read-only | jq -r .msg.message
codex exec --json "$1" --sandbox read-only --skip-git-repo-check | jq -r '.item | select(.type == "agent_message") | .text'