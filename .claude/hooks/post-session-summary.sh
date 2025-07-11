#!/usr/bin/env bash

# Claude Code Stop hook - runs at the end of each session
# Provides a summary of what was done

set -e

# Track files changed in this session (if git is available)
if command -v git &> /dev/null && [ -d .git ]; then
    # Get uncommitted changes
    CHANGED_FILES=$(git status --porcelain 2>/dev/null | wc -l)
    
    if [ "$CHANGED_FILES" -gt 0 ]; then
        echo "📊 Session Summary:"
        echo "- Modified files: $CHANGED_FILES"
        
        # Show file categories
        PYTHON_FILES=$(git status --porcelain 2>/dev/null | grep -c "\.py" || true)
        TS_FILES=$(git status --porcelain 2>/dev/null | grep -cE "\.(ts|tsx|js|jsx)" || true)
        
        if [ "$PYTHON_FILES" -gt 0 ]; then
            echo "  - Python files: $PYTHON_FILES"
        fi
        
        if [ "$TS_FILES" -gt 0 ]; then
            echo "  - TypeScript/JavaScript files: $TS_FILES"
        fi
        
        echo ""
        echo "💡 Remember to:"
        echo "  - Review changes: git diff"
        echo "  - Run tests before committing"
        echo "  - Commit with descriptive message"
    fi
fi

# Check if any TODOs were added
if command -v grep &> /dev/null; then
    NEW_TODOS=$(git diff 2>/dev/null | grep -c "^+.*TODO" || true)
    if [ "$NEW_TODOS" -gt 0 ]; then
        echo "📝 Added $NEW_TODOS new TODO comments"
    fi
fi

exit 0