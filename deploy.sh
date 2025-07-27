#!/bin/bash

echo "🚀 Stock AI Production Deployment"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create a .env file with production credentials"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "🔧 Building and starting production services..."

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Build and start services
if docker-compose -f docker-compose.prod.yml up -d --build; then
    echo "⏳ Waiting for services to start..."
    sleep 15
    
    # Check service status
    echo "🔍 Checking service status..."
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    echo "🎉 Stock AI Production Deployment Complete!"
    echo ""
    echo "📱 Services Available:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📋 Useful Commands:"
    echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
    echo "   Restart services: docker-compose -f docker-compose.prod.yml restart"
    echo ""
    echo "🔍 Health Checks:"
    echo "   Backend Health: curl http://localhost:8000/health"
    echo "   Database: docker exec stock_ai_postgres_prod pg_isready -U stock_ai_user -d stock_ai"
    echo "   Redis: docker exec stock_ai_redis_prod redis-cli ping"
else
    echo ""
    echo "❌ Production deployment failed!"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "1. Check logs: docker-compose -f docker-compose.prod.yml logs"
    echo "2. Verify .env file has all required variables"
    echo "3. Ensure ports 3000 and 8000 are available"
    echo "4. Check Docker has enough resources"
    exit 1
fi 