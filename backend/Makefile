# ConvoSynth Backend Makefile

.PHONY: help install dev up down logs test clean build

help:
	@echo "ConvoSynth Backend - Available Commands:"
	@echo ""
	@echo "  make install    - Install Python dependencies"
	@echo "  make dev        - Run backend locally with auto-reload"
	@echo "  make up         - Start all services with Docker Compose"
	@echo "  make down       - Stop all services"
	@echo "  make logs       - View backend logs"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean up generated files"
	@echo "  make build      - Build Docker images"
	@echo "  make shell      - Open Python shell in backend container"
	@echo "  make mongo      - Open MongoDB shell"
	@echo ""

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

dev:
	@echo "Starting backend in development mode..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "✓ Services started"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "MongoDB: localhost:27017"

down:
	@echo "Stopping all services..."
	docker-compose down
	@echo "✓ Services stopped"

logs:
	docker-compose logs -f backend

test:
	@echo "Running tests..."
	pytest -v
	@echo "✓ Tests complete"

test-cov:
	@echo "Running tests with coverage..."
	pytest --cov=app --cov-report=html tests/
	@echo "✓ Coverage report generated in htmlcov/"

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf .coverage
	@echo "✓ Cleanup complete"

build:
	@echo "Building Docker images..."
	docker-compose build
	@echo "✓ Build complete"

shell:
	docker-compose exec backend python

mongo:
	docker-compose exec mongodb mongosh convosynth

mongo-ui:
	@echo "Starting Mongo Express..."
	docker-compose --profile dev up -d mongo-express
	@echo "✓ Mongo Express: http://localhost:8081"
	@echo "  Username: admin"
	@echo "  Password: admin123"

restart:
	@echo "Restarting backend..."
	docker-compose restart backend
	@echo "✓ Backend restarted"

status:
	@echo "Service status:"
	docker-compose ps
