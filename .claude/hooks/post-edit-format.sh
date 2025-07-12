#!/usr/bin/env bash

# Claude Code PostToolUse hook for auto-formatting after file edits
# This hook runs after Edit, MultiEdit, or Write tools are used

set -e

# Get the tool name and file path from Claude Code environment
TOOL_NAME="${CLAUDE_TOOL_NAME}"
FILE_PATH="${CLAUDE_TOOL_RESULT_file_path}"

# Exit if no file path (some tools might not have it)
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Only process files that exist
if [ ! -f "$FILE_PATH" ]; then
    exit 0
fi

# Determine file type and apply appropriate formatting
if [[ "$FILE_PATH" == *.py ]]; then
    # Python file - format with ruff
    if command -v ruff &> /dev/null; then
        ruff format "$FILE_PATH" --quiet 2>/dev/null || true
    elif command -v nix &> /dev/null; then
        nix develop -c ruff format "$FILE_PATH" --quiet 2>/dev/null || true
    fi
elif [[ "$FILE_PATH" == *.js || "$FILE_PATH" == *.jsx || "$FILE_PATH" == *.ts || "$FILE_PATH" == *.tsx ]]; then
    # JavaScript/TypeScript file - format with prettier
    if [[ "$FILE_PATH" == frontend/* ]]; then
        cd frontend && npx prettier --write "${FILE_PATH#frontend/}" --loglevel silent 2>/dev/null || true
    fi
elif [[ "$FILE_PATH" == *.json ]]; then
    # JSON file - format with jq if available
    if command -v jq &> /dev/null; then
        jq . "$FILE_PATH" > "$FILE_PATH.tmp" && mv "$FILE_PATH.tmp" "$FILE_PATH" 2>/dev/null || true
    fi
fi

# Always exit successfully to not block Claude Code
exit 0
