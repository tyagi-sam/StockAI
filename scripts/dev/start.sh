#!/bin/bash

# Stock AI Startup Script

# Always run from the repo root so relative paths resolve
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🚀 Starting Stock AI Application..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. Please edit it with your credentials before continuing."
    echo "   Required variables:"
    echo "   - ZERODHA_API_KEY"
    echo "   - ZERODHA_API_SECRET" 
    echo "   - OPENAI_API_KEY (optional)"
    echo "   - FERNET_KEY"
    echo ""
    echo "   After editing .env, run this script again."
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install it and try again."
    exit 1
fi

echo "🔧 Building and starting services..."
if docker-compose up -d --build; then
    echo "⏳ Waiting for services to start..."
    sleep 10

    # Check if services are running
    echo "🔍 Checking service status..."
    docker-compose ps

    echo ""
    echo "🎉 Stock AI is starting up!"
    echo ""
    echo "📱 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop services: docker-compose down"
    echo "   Restart services: docker-compose restart"
    echo ""
    echo "🔍 To check if everything is working:"
    echo "   python test_setup.py"
else
    echo ""
    echo "❌ Failed to start Stock AI services!"
    echo ""
    echo "🔍 Common issues and solutions:"
    echo "1. Frontend build errors: Check TypeScript compilation errors above"
    echo "2. Backend build errors: Check if all dependencies are available"
    echo "3. Port conflicts: Make sure ports 3000 and 8000 are available"
    echo "4. Docker issues: Make sure Docker is running and has enough resources"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop services: docker-compose down"
    echo "   Restart services: docker-compose restart"
    echo "   Clean build: docker-compose down && docker-compose up -d --build --force-recreate"
    echo ""
    echo "🔧 For local development without Docker:"
    echo "   Install dependencies: ./install_deps.sh"
    echo "   Test setup: python test_setup.py"
    exit 1
fi 