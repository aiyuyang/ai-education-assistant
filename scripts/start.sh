#!/bin/bash

# AI Education Assistant Backend Startup Script

echo "🚀 Starting AI Education Assistant Backend..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from env.example..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration before running again."
    exit 1
fi

# Start services with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services started successfully!"
    echo ""
    echo "📋 Service Status:"
    docker-compose ps
    echo ""
    echo "🌐 API Documentation:"
    echo "   - Swagger UI: http://localhost:8000/docs"
    echo "   - ReDoc: http://localhost:8000/redoc"
    echo ""
    echo "📊 Service URLs:"
    echo "   - API Server: http://localhost:8000"
    echo "   - MySQL: localhost:3306"
    echo "   - Redis: localhost:6379"
    echo ""
    echo "📝 To view logs: docker-compose logs -f app"
    echo "🛑 To stop services: docker-compose down"
else
    echo "❌ Failed to start services. Check logs with: docker-compose logs"
    exit 1
fi

