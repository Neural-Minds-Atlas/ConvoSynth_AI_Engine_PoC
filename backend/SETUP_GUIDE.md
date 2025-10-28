# ConvoSynth Backend - Setup Guide

This guide will walk you through setting up the ConvoSynth backend from scratch.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Docker Desktop installed and running
- [ ] Python 3.11+ installed (for local development)
- [ ] Anthropic API key (sign up at https://console.anthropic.com/)
- [ ] Git installed
- [ ] A code editor (VS Code recommended)

## Step 1: Environment Setup

### 1.1 Create Environment File

```bash
cd backend
cp .env.example .env
```

### 1.2 Configure Your API Key

Open `.env` file and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### 1.3 Generate JWT Secret

Generate a secure JWT secret key:

```bash
# On Mac/Linux
openssl rand -hex 32

# On Windows (PowerShell)
[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
```

Add it to `.env`:

```env
JWT_SECRET_KEY=your-generated-secret-key-here
```

## Step 2: Start the Backend

### Option A: Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

Services started:
- MongoDB: `localhost:27017`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### Option B: Local Development (Without Docker)

#### 2.1 Install MongoDB

**Mac:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Windows:**
Download from https://www.mongodb.com/try/download/community

**Linux:**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
```

#### 2.2 Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2.3 Start the Backend

```bash
python -m app.main
# or
uvicorn app.main:app --reload
```

## Step 3: Verify Installation

### 3.1 Check Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "ConvoSynth Backend",
  "version": "1.0.0",
  "environment": "development"
}
```

### 3.2 Check Database

```bash
curl http://localhost:8000/health/db
```

Expected response:
```json
{
  "status": "healthy",
  "database": "MongoDB",
  "connected": true
}
```

### 3.3 Open API Documentation

Visit http://localhost:8000/docs in your browser.

You should see the interactive Swagger UI with all API endpoints.

## Step 4: Create Your First User

### 4.1 Using curl

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "name": "Test User",
    "role": "analyst",
    "department": "operations",
    "accessScopes": ["operational_data"],
    "permissions": {
      "viewOperationalData": true
    }
  }'
```

### 4.2 Using Python

```bash
python example_client.py
```

### 4.3 Using API Docs

1. Go to http://localhost:8000/docs
2. Click on "POST /api/v1/auth/register"
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"

## Step 5: Test Conversation Agent

### 5.1 Get Access Token

Login to get your token:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

Save the `accessToken` from the response.

### 5.2 Start Conversation

```bash
TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/v1/conversation/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "userMessage": "I need a presentation about Q3 performance",
    "cycleType": "generation"
  }'
```

## Step 6: Optional - Database UI

### Start Mongo Express

```bash
docker-compose --profile dev up -d mongo-express
```

Access at: http://localhost:8081
- Username: `admin`
- Password: `admin123`

## Common Issues & Solutions

### Issue: MongoDB connection failed

**Solution:**
```bash
# Check if MongoDB is running
docker-compose ps

# Restart MongoDB
docker-compose restart mongodb

# Check logs
docker-compose logs mongodb
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Find process using port 8000
# Mac/Linux:
lsof -i :8000

# Windows:
netstat -ano | findstr :8000

# Kill the process or change port in .env:
API_PORT=8001
```

### Issue: Anthropic API key invalid

**Solution:**
1. Verify your API key at https://console.anthropic.com/
2. Ensure no extra spaces in `.env` file
3. Restart the backend after updating `.env`

### Issue: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Or rebuild Docker image
docker-compose build --no-cache backend
docker-compose up -d
```

## Next Steps

Now that your backend is running:

1. **Test the API** using the example client or Postman
2. **Read the API documentation** at `/docs`
3. **Integrate with your frontend** using the provided endpoints
4. **Add sample documents** for RBAC testing
5. **Customize user roles** and permissions

## Development Workflow

### Making Changes

1. Edit code in `app/` directory
2. If using Docker with volumes, changes auto-reload
3. If running locally with `--reload`, changes auto-reload
4. Test your changes
5. Commit to git

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

### Viewing Logs

```bash
# Docker logs
docker-compose logs -f backend

# Local logs
# Logs are output to console when running locally
```

## Production Deployment

For production deployment, see the main README.md file for:
- Environment configuration
- Security best practices
- Cloud deployment options
- Monitoring setup

## Getting Help

- Check the main README.md for detailed documentation
- Review API docs at `/docs`
- Check logs for error messages
- Open an issue on GitHub

## Summary

You now have:
- ✅ MongoDB running
- ✅ Backend API running
- ✅ User authentication working
- ✅ Conversation agent ready
- ✅ API documentation available

Your backend is ready for integration! 🎉
