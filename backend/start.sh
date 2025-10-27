#!/bin/bash

# ConvoSynth Backend Startup Script

set -e

echo "======================================"
echo "  ConvoSynth Backend Startup"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: You need to add your Anthropic API key to .env"
    echo "   Edit .env and add: ANTHROPIC_API_KEY=your_key_here"
    echo ""
    read -p "Press Enter after adding your API key..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "   Please start Docker Desktop and try again"
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if API key is set
if grep -q "your_anthropic_api_key_here" .env; then
    echo "⚠️  WARNING: Anthropic API key not set in .env"
    echo "   The backend will fail to start without a valid API key"
    echo ""
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Aborted. Please add your API key to .env first."
        exit 1
    fi
fi

echo "Starting services with Docker Compose..."
echo ""

# Start services
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
echo "   This may take 30-60 seconds on first run..."
echo ""

# Wait for backend to be ready
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend is ready!"
        break
    fi
    attempt=$((attempt + 1))
    sleep 2
    echo -n "."
done

echo ""
echo ""

if [ $attempt -eq $max_attempts ]; then
    echo "⚠️  Backend did not start within expected time"
    echo "   Check logs: docker-compose logs backend"
    echo ""
    exit 1
fi

# Check database
if curl -sf http://localhost:8000/health/db | grep -q "healthy"; then
    echo "✓ MongoDB is connected"
else
    echo "⚠️  MongoDB connection failed"
    echo "   Check logs: docker-compose logs mongodb"
fi

echo ""
echo "======================================"
echo "  ✅ ConvoSynth Backend is Running!"
echo "======================================"
echo ""
echo "Access points:"
echo "  • Backend API:     http://localhost:8000"
echo "  • API Docs:        http://localhost:8000/docs"
echo "  • Health Check:    http://localhost:8000/health"
echo "  • MongoDB:         localhost:27017"
echo ""
echo "Quick commands:"
echo "  • View logs:       docker-compose logs -f backend"
echo "  • Stop services:   docker-compose down"
echo "  • Test API:        python example_client.py"
echo ""
echo "Next steps:"
echo "  1. Visit http://localhost:8000/docs to see API documentation"
echo "  2. Run: python example_client.py to test the system"
echo "  3. Read QUICKSTART.md for more information"
echo ""
echo "======================================"
