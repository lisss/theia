#!/bin/bash
# Build script for Theia Docker images with optimized caching

set -e

echo "Building Theia Docker images with layer caching..."
echo ""

# Build images in dependency order
echo "Building backend image..."
docker-compose build backend

echo "Building agent image..."
docker-compose build agent

echo "Building frontend image..."
docker-compose build frontend

echo ""
echo "All images built successfully!"
echo "Start services with: docker-compose up -d"

