#!/usr/bin/env bash
# Pre-commit hook to run frontend linting
set -e

echo "Running frontend ESLint..."

# Change to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Error: node_modules not found. Please run 'npm install' in the frontend directory."
    exit 1
fi

# Run ESLint
npm run lint
