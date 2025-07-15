#!/usr/bin/env bash

# Claude Code PostToolUse hook for auto-formatting after file edits
# This hook runs after Edit, MultiEdit, or Write tools are used

set -e

# Read JSON from stdin
JSON_INPUT=$(cat)

# Parse tool name and file path from JSON using jq
TOOL_NAME=$(echo "$JSON_INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$JSON_INPUT" | jq -r '.tool_input.file_path // .tool_response.filePath // empty')

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
    # JavaScript/TypeScript file - format with eslint
    if [[ "$FILE_PATH" == *frontend/* ]]; then
        # Find the frontend directory
        FRONTEND_DIR=$(echo "$FILE_PATH" | sed 's|/frontend/.*|/frontend|')
        if [ -d "$FRONTEND_DIR" ]; then
            cd "$FRONTEND_DIR" && npx eslint "$FILE_PATH" --fix 2>/dev/null || true
        fi
    fi
elif [[ "$FILE_PATH" == *.json ]]; then
    # JSON file - format with jq if available
    if command -v jq &> /dev/null; then
        jq . "$FILE_PATH" > "$FILE_PATH.tmp" && mv "$FILE_PATH.tmp" "$FILE_PATH" 2>/dev/null || true
    fi
fi

# Always exit successfully to not block Claude Code
exit 0
