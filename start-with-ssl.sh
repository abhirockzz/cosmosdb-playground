#!/bin/bash

# Start Cosmos DB Playground with HTTPS/SSL enabled
# This script uses docker-compose with the SSL override file

set -e

echo "Starting Cosmos DB Playground with HTTPS enabled..."
echo ""

# Check if docker-compose.ssl.yml exists
if [ ! -f "docker-compose.ssl.yml" ]; then
    echo "Error: docker-compose.ssl.yml not found!"
    echo "Make sure you're running this script from the project root directory."
    exit 1
fi

# Check if SSL certificates have been configured
if grep -q "your-domain-name" docker-compose.ssl.yml; then
    echo "Warning: SSL certificates not yet configured!"
    echo "Please update docker-compose.ssl.yml with your actual domain name:"
    echo "  sed -i \"s|your-domain-name|\$DOMAIN_NAME|g\" docker-compose.ssl.yml"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Stop any running containers
echo "Stopping existing containers..."
docker-compose down

# Start with SSL configuration
echo "Starting services with HTTPS enabled..."
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d

# Wait a moment for containers to start
sleep 2

# Show status
echo ""
echo "Services started! Status:"
docker-compose ps

echo ""
echo "✅ HTTPS is now enabled!"
echo "Access your playground at: https://your-domain-name"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f nginx"
