#!/bin/bash

# Constants
REGISTRY="ghcr.io"
USERNAME="your-username"  # Replace with your GitHub username
IMAGE_NAME="swotting-prod"
CONTAINER_NAME="my-app"
PORT=8000

# GitHub Token
echo "Enter your GitHub Token:"
read -s GITHUB_TOKEN

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login $REGISTRY -u $USERNAME --password-stdin

# Pull the latest image
docker pull $REGISTRY/$USERNAME/$IMAGE_NAME:latest

# Stop the existing container (if it exists)
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

# Run the new container
docker run --name $CONTAINER_NAME -d -p 80:$PORT $REGISTRY/$USERNAME/$IMAGE_NAME:latest gunicorn swotting.wsgi:application --bind 0.0.0.0:$PORT

echo "Deployment of $IMAGE_NAME completed."
