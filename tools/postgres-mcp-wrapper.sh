#!/usr/bin/env bash
# Wrapper script to run postgres-mcp with environment variables from backend/.env

# Source the backend environment variables
if [[ -f "$(dirname "$0")/../backend/.env" ]]; then
  set -a
  source "$(dirname "$0")/../backend/.env"
  set +a
fi

# Construct DATABASE_URI
export DATABASE_URI="postgresql://${USERNAME}:${PASS}@${URL}:5432/${DB}"

# Run postgres-mcp with the environment variable
exec uvx postgres-mcp "$@"
