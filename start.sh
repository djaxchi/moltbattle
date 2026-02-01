#!/bin/bash

echo "🔥 Starting Agent Fight Club..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Copy env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
fi

# Build and start containers
echo "🏗️  Building containers..."
docker compose build

echo "🚀 Starting services..."
docker compose up -d

echo ""
echo "✅ Agent Fight Club is running!"
echo ""
echo "📍 Frontend UI: http://localhost:3000"
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 Health Check: http://localhost:8000/health"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop: docker compose down"
echo ""
