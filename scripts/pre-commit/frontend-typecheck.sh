#!/usr/bin/env bash
# Pre-commit hook to run frontend TypeScript type checking
set -e

echo "Running frontend TypeScript type check..."

# Change to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Error: node_modules not found. Please run 'npm install' in the frontend directory."
    exit 1
fi

# Run TypeScript type checking
npm run type-check
