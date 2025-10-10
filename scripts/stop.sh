#!/bin/bash

# AI Education Assistant Backend Stop Script

echo "🛑 Stopping AI Education Assistant Backend..."

# Stop services with Docker Compose
echo "🐳 Stopping services..."
docker-compose down

# Check if services are stopped
if docker-compose ps | grep -q "Up"; then
    echo "⚠️  Some services are still running. Force stopping..."
    docker-compose down --remove-orphans
else
    echo "✅ All services stopped successfully!"
fi

echo ""
echo "📋 Service Status:"
docker-compose ps

