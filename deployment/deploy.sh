#!/bin/bash

# Constants
REGISTRY="ghcr.io"
USERNAME="swottinglabs"  # Already correct!
IMAGE_NAME="swotting-prod"

# GitHub Token
echo "Enter your GitHub Token:"
read -s GITHUB_TOKEN

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login $REGISTRY -u $USERNAME --password-stdin

# Stop existing containers and remove volumes
docker-compose -f docker-compose.yml down --volumes

# Pull the latest images
docker-compose -f docker-compose.yml pull

# Start all services in detached mode
docker-compose -f docker-compose.yml up -d

echo "Deployment completed. Services running:"
docker-compose -f docker-compose.yml ps

# Show logs (comment out if not needed)
docker-compose -f docker-compose.yml logs -f
