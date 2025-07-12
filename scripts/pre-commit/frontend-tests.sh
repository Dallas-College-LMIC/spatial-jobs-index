#!/usr/bin/env bash
# Pre-commit hook to run frontend unit tests
set -e

echo "Running frontend unit tests..."

# Change to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Error: node_modules not found. Please run 'npm install' in the frontend directory."
    exit 1
fi

# Run tests in CI mode (single run, no watch)
# Use --reporter=verbose for better output in pre-commit context
npm run test:run -- --reporter=verbose --passWithNoTests
