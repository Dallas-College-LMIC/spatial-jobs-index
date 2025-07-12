#!/usr/bin/env bash

# Claude Code PreToolUse hook for Bash command validation
# This hook runs before Bash commands are executed

set -e

# Get the command from Claude Code environment
COMMAND="${CLAUDE_TOOL_PARAMS_command}"

# Output JSON to control execution
output_json() {
    local continue="$1"
    local message="$2"
    echo "{\"continue\": $continue, \"decision_feedback\": \"$message\"}"
}

# Check for potentially dangerous commands
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf /*"
    "chmod -R 777"
    ":(){ :|:& };:"  # Fork bomb
    "> /dev/sda"
    "dd if=/dev/zero"
    "mkfs."
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if [[ "$COMMAND" == *"$pattern"* ]]; then
        output_json "false" "⚠️ Blocked dangerous command pattern: $pattern"
        exit 0
    fi
done

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
