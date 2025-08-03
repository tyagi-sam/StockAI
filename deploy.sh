#!/bin/bash

# Stock AI Production Deployment Script

set -e  # Exit on any error

echo "🚀 Starting Stock AI Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install it and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found!"
    print_status "Creating .env file from template..."
    cp env.example .env
    print_error "Please edit .env file with your production credentials before continuing."
    print_status "Required variables for production:"
    echo "   - POSTGRES_USER (default: stock_ai_user)"
    echo "   - POSTGRES_PASSWORD (strong password)"
    echo "   - REDIS_PASSWORD (strong password)"
    echo "   - JWT_SECRET (32+ characters)"
    echo "   - FERNET_KEY (base64 encoded)"
    echo "   - GOOGLE_CLIENT_ID"
    echo "   - GOOGLE_CLIENT_SECRET"
    echo "   - ZERODHA_API_KEY"
    echo "   - ZERODHA_API_SECRET"
    echo "   - OPENAI_API_KEY (optional)"
    echo "   - SMTP settings for email"
    echo "   - FRONTEND_URL (your domain)"
    echo "   - BACKEND_CORS_ORIGINS (your domain)"
    echo ""
    print_status "After editing .env, run this script again."
    exit 1
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=(
    "JWT_SECRET"
    "FERNET_KEY"
    "GOOGLE_CLIENT_ID"
    "GOOGLE_CLIENT_SECRET"
    "ZERODHA_API_KEY"
    "ZERODHA_API_SECRET"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        print_error "Required environment variable $var is not set in .env file"
        exit 1
    fi
done

# Check JWT_SECRET length
if [ ${#JWT_SECRET} -lt 32 ]; then
    print_error "JWT_SECRET must be at least 32 characters long"
    exit 1
fi

print_status "Environment variables validated successfully"

# Security checks
print_status "Running security checks..."

# Check for weak passwords
if [ -n "$POSTGRES_PASSWORD" ] && [ ${#POSTGRES_PASSWORD} -lt 8 ]; then
    print_warning "POSTGRES_PASSWORD is less than 8 characters. Consider using a stronger password."
fi

if [ -n "$REDIS_PASSWORD" ] && [ ${#REDIS_PASSWORD} -lt 8 ]; then
    print_warning "REDIS_PASSWORD is less than 8 characters. Consider using a stronger password."
fi

# Check if production environment is set
if [ "$ENVIRONMENT" != "production" ]; then
    print_warning "ENVIRONMENT is not set to 'production'. Setting it now..."
    sed -i 's/ENVIRONMENT=.*/ENVIRONMENT=production/' .env
fi

print_status "Security checks completed"

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Clean up old images (optional)
read -p "Do you want to clean up old Docker images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleaning up old images..."
    docker system prune -f
fi

# Build and start production services
print_status "Building and starting production services..."
if docker-compose -f docker-compose.prod.yml up -d --build; then
    print_status "Waiting for services to start..."
    sleep 15

    # Check service health
    print_status "Checking service health..."
    
    # Check if services are running
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        print_status "Services are running!"
    else
        print_error "Some services failed to start"
        docker-compose -f docker-compose.prod.yml logs
        exit 1
    fi

    # Wait for backend to be ready
    print_status "Waiting for backend to be ready..."
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_status "Backend is ready!"
            break
        else
            attempt=$((attempt + 1))
            print_status "Backend not ready, waiting... (attempt $attempt/$max_attempts)"
            sleep 5
        fi
    done

    if [ $attempt -eq $max_attempts ]; then
        print_error "Backend failed to start within expected time"
        docker-compose -f docker-compose.prod.yml logs backend
        exit 1
    fi

    # Wait for frontend to be ready
    print_status "Waiting for frontend to be ready..."
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost/health > /dev/null 2>&1; then
            print_status "Frontend is ready!"
            break
        else
            attempt=$((attempt + 1))
            print_status "Frontend not ready, waiting... (attempt $attempt/$max_attempts)"
            sleep 5
        fi
    done

    if [ $attempt -eq $max_attempts ]; then
        print_error "Frontend failed to start within expected time"
        docker-compose -f docker-compose.prod.yml logs frontend
        exit 1
    fi

    print_status ""
    print_status "🎉 Stock AI Production Deployment Successful!"
    print_status ""
    print_status "📱 Frontend: http://localhost (or your domain)"
    print_status "🔧 Backend API: http://localhost:8000"
    print_status "📚 API Documentation: http://localhost:8000/docs"
    print_status ""
    print_status "📋 Useful commands:"
    echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
    echo "   Restart services: docker-compose -f docker-compose.prod.yml restart"
    echo "   Update deployment: ./deploy.sh"
    print_status ""
    print_status "🔍 Health checks:"
    echo "   Frontend: curl http://localhost/health"
    echo "   Backend: curl http://localhost:8000/health"
    print_status ""
    print_status "🔒 Security reminders:"
    echo "   - Change default passwords"
    echo "   - Set up SSL/TLS certificates"
    echo "   - Configure firewall rules"
    echo "   - Set up monitoring and logging"
    echo "   - Regular backups of postgres_data volume"

else
    print_error ""
    print_error "❌ Failed to deploy Stock AI!"
    print_error ""
    print_error "🔍 Common issues and solutions:"
    echo "1. Port conflicts: Make sure ports 80 and 8000 are available"
    echo "2. Build errors: Check Docker build logs above"
    echo "3. Environment variables: Ensure all required vars are set in .env"
    echo "4. Docker resources: Ensure Docker has enough memory/CPU"
    print_error ""
    print_error "📋 Useful commands:"
    echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
    echo "   Clean build: docker-compose -f docker-compose.prod.yml down && ./deploy.sh"
    exit 1
fi 