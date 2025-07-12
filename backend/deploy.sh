#!/bin/bash

# Deployment script for spatial-index-api
# This script pulls the latest Docker image and restarts the application

set -e

echo "Starting deployment..."

# Navigate to the directory containing docker-compose.yml
cd ~/projects/spatial-jobs-index-api || { echo "Error: Could not find deployment directory"; exit 1; }

echo "Pulling latest Docker image..."
docker compose pull

echo "Restarting services..."
docker compose up -d

# Wait a moment for the service to start
sleep 10

# Health check
echo "Performing health check..."
if curl -f -s http://localhost:8000/docs > /dev/null; then
    echo "✅ Deployment successful - API is responding"
else
    echo "❌ Health check failed - API may not be running properly"
    docker compose logs --tail=20
    exit 1
fi

echo "🚀 Deployment completed successfully!"
