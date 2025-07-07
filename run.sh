#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
# This ensures that the script will stop if any step fails.
set -e

# --- Build Docker Images ---
# This command builds (or rebuilds) the Docker images for all services
# defined in the docker compose.yml file. It uses the Dockerfile
# in each service's respective directory.
echo "Building all service images..."
docker compose build

# --- Launch Services ---
# This command creates and starts all the services in detached mode (-d),
# meaning they will run in the background. The services will be
# interconnected on a dedicated Docker network.
echo "Launching all services in detached mode..."
docker compose up -d

echo "✅ System is up and running!"
echo "Access the React UI at http://localhost:3000"
echo "API documentation available at http://localhost:8000/docs"