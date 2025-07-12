#!/usr/bin/env bash
# Build script for local testing with root base path

export BASE_PATH="/"
npm run build
echo "Built with base path: /"
echo "You can now serve the dist/ directory with any static file server"
