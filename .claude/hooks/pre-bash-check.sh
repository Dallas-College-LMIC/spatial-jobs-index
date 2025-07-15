#!/usr/bin/env bash

# Claude Code PreToolUse hook for Bash command validation
# This hook runs before Bash commands are executed

set -e

# Read JSON from stdin
JSON_INPUT=$(cat)

# Parse the command from JSON using jq
COMMAND=$(echo "$JSON_INPUT" | jq -r '.tool_input.command // empty')

# Output JSON to control execution
output_json() {
    local continue="$1"
    local message="$2"
    echo "{\"continue\": $continue, \"decision_feedback\": \"$message\"}"
}

# Exit if no command
if [ -z "$COMMAND" ]; then
    exit 0
fi

# Project-specific command checks are handled below
# (Universal dangerous commands are blocked by global hooks)

# Check for commands that modify git config (per CLAUDE.md instructions)
if [[ "$COMMAND" == *"git config"* ]] && [[ "$COMMAND" != *"--get"* ]] && [[ "$COMMAND" != *"--list"* ]]; then
    output_json "false" "❌ Git config modifications are not allowed per CLAUDE.md"
    exit 0
fi

# Check for npm/yarn global installs that might conflict with Nix
if [[ "$COMMAND" == *"npm install -g"* ]] || [[ "$COMMAND" == *"yarn global add"* ]]; then
    output_json "true" "⚠️ Warning: Global npm/yarn installs may conflict with Nix environment"
    exit 0
fi

# Get current working directory from session if available
PWD=$(echo "$JSON_INPUT" | jq -r '.cwd // empty')

# Check if running tests without being in correct directory
if [[ "$COMMAND" == *"pytest"* ]] && [[ ! "$COMMAND" == *"cd backend"* ]] && [[ "$PWD" != */backend ]]; then
    output_json "true" "💡 Tip: pytest should be run from the backend directory"
    exit 0
fi

if [[ "$COMMAND" == *"npm test"* ]] && [[ ! "$COMMAND" == *"cd frontend"* ]] && [[ "$PWD" != */frontend ]]; then
    output_json "true" "💡 Tip: npm test should be run from the frontend directory"
    exit 0
fi

# Allow command to proceed
exit 0
