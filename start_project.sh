#!/bin/bash

echo "Stopping and removing Docker containers and volumes..."
docker-compose down --volumes

echo "Building Docker images..."
docker-compose build

echo "Starting Docker containers in detached mode..."
docker-compose up -d

echo "Project startup script finished."
printf '\a'
