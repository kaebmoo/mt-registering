#!/bin/bash

# Deployment script for Meeting Registration System

echo "🚀 Starting deployment of Meeting Registration System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing."
    echo "Press Enter to continue after editing .env file..."
    read
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start containers
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting containers..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check if database is initialized
echo "🔍 Checking database..."
docker-compose exec -T postgres psql -U postgres -d meeting_registration -c "SELECT COUNT(*) FROM employees;" &> /dev/null

if [ $? -ne 0 ]; then
    echo "📊 Initializing database schema..."
    docker-compose exec -T postgres psql -U postgres -d meeting_registration < database_schema.sql
fi

# Check for employee.csv
if [ -f employee.csv ]; then
    echo "📥 Importing employee data..."
    docker-compose exec -T web python import_data.py --employees employee.csv
else
    echo "⚠️  employee.csv not found. Please import manually later."
fi

# Check for schedule.json
if [ -f schedule.json ]; then
    echo "📅 Importing meeting schedule..."
    docker-compose exec -T web python import_data.py --meeting schedule.json
else
    echo "⚠️  schedule.json not found. Please create meeting via admin panel."
fi

# Show status
echo ""
echo "✅ Deployment completed!"
echo ""
echo "📍 Access points:"
echo "   - Registration: http://localhost:5000"
echo "   - Admin Panel: http://localhost:5000/admin"
echo ""
echo "📊 Services status:"
docker-compose ps

echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
