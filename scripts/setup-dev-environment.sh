#!/bin/bash
# Development Environment Setup Script for 3D Print Management System

set -e

echo "🏗️  Setting up 3D Print Management System development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files from examples if they don't exist
if [ ! -f backend/.env ]; then
    echo "📄 Creating backend/.env from example..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your configuration"
fi

if [ ! -f frontend/.env.local ]; then
    echo "📄 Creating frontend/.env.local from example..."
    cp frontend/.env.local.example frontend/.env.local
    echo "⚠️  Please edit frontend/.env.local with your configuration"
fi

# Create storage directories
echo "📁 Creating storage directories..."
mkdir -p storage/{Uploaded,Pending,ReadyToPrint,Printing,Completed,PaidPickedUp,Archived}

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose build

# Start database first
echo "🗄️  Starting database..."
docker-compose up -d db

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 5

# Run database migrations
echo "🔄 Running database migrations..."
docker-compose run --rm backend flask db upgrade

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

echo "✅ Development environment setup complete!"
echo ""
echo "🌐 Services available at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:5000"
echo "   Database: localhost:5432"
echo ""
echo "📝 Next steps:"
echo "   1. Edit backend/.env with your email server settings"
echo "   2. Edit frontend/.env.local if needed"
echo "   3. Install SlicerOpener protocol handler on staff workstations"
echo "   4. Configure shared network storage paths"
echo ""
echo "🛠️  Development commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Rebuild: docker-compose build"
echo "   Database shell: docker-compose exec db psql -U printdb printdb"