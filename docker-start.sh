#!/bin/bash

# YorkU Multi-DB API - Docker Quick Start Script
# This script helps you get started with Docker deployment

set -e

echo "========================================"
echo "YorkU Multi-DB API - Docker Quick Start"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker is installed: $(docker --version)"
echo "✓ Docker Compose is installed: $(docker compose version)"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    if [ -f .env.example ]; then
        echo "   Creating .env from .env.example..."
        cp .env.example .env
        echo "✓ .env file created"
        echo "⚠️  Please edit .env file with your database credentials before continuing"
        echo ""
        read -p "Press Enter to continue after editing .env file..."
    else
        echo "❌ .env.example not found. Cannot create .env file."
        exit 1
    fi
else
    echo "✓ .env file exists"
fi

echo ""
echo "Choose deployment mode:"
echo "  1) Production (recommended for deployment)"
echo "  2) Development (with hot-reload)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting in PRODUCTION mode..."
        echo ""

        # Build the image
        echo "Building Docker image..."
        docker compose -f docker-compose.prod.yml build

        echo ""
        echo "Starting container..."
        docker compose -f docker-compose.prod.yml up -d

        echo ""
        echo "Waiting for container to be healthy..."
        sleep 5

        # Check health
        for i in {1..10}; do
            if curl -s http://localhost:8082/health > /dev/null 2>&1; then
                echo "✓ Container is healthy!"
                break
            fi
            echo "  Waiting... ($i/10)"
            sleep 3
        done

        echo ""
        echo "========================================"
        echo "✓ Production deployment complete!"
        echo "========================================"
        echo ""
        echo "API is running at: http://localhost:8082"
        echo "Health check: http://localhost:8082/health"
        echo ""
        echo "Useful commands:"
        echo "  View logs:        docker compose -f docker-compose.prod.yml logs -f"
        echo "  Stop container:   docker compose -f docker-compose.prod.yml down"
        echo "  Restart:          docker compose -f docker-compose.prod.yml restart"
        echo "  Or use:           make logs, make down, make restart"
        echo ""
        ;;
    2)
        echo ""
        echo "🔧 Starting in DEVELOPMENT mode..."
        echo ""

        # Build the image
        echo "Building Docker image..."
        docker compose -f docker-compose.dev.yml build

        echo ""
        echo "Starting container with hot-reload..."
        docker compose -f docker-compose.dev.yml up -d

        echo ""
        echo "Waiting for container to be healthy..."
        sleep 5

        # Check health
        for i in {1..10}; do
            if curl -s http://localhost:8082/health > /dev/null 2>&1; then
                echo "✓ Container is healthy!"
                break
            fi
            echo "  Waiting... ($i/10)"
            sleep 3
        done

        echo ""
        echo "========================================"
        echo "✓ Development deployment complete!"
        echo "========================================"
        echo ""
        echo "API is running at: http://localhost:8082"
        echo "Interactive docs: http://localhost:8082/docs"
        echo "Health check: http://localhost:8082/health"
        echo ""
        echo "Hot-reload is enabled - code changes will auto-reload!"
        echo ""
        echo "Useful commands:"
        echo "  View logs:        docker compose -f docker-compose.dev.yml logs -f"
        echo "  Stop container:   docker compose -f docker-compose.dev.yml down"
        echo "  Restart:          docker compose -f docker-compose.dev.yml restart"
        echo "  Or use:           make dev-logs, make dev-down"
        echo ""
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Test the API
echo "Testing API..."
if curl -s http://localhost:8082/health | grep -q "ok"; then
    echo "✓ API is responding correctly!"
else
    echo "⚠️  API might not be fully ready yet. Check logs with:"
    echo "   docker-compose logs -f"
fi

echo ""
echo "Quick test command:"
echo "  curl http://localhost:8082/health"
echo ""

