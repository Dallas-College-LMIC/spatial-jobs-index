#!/usr/bin/env bash
# Pre-commit hook to run backend unit tests
set -e

echo "Running backend unit tests..."

# Always use uv to ensure dependencies are available
cd backend && uv run pytest tests/unit/ -x --tb=short -q
