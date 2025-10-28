# ConvoSynth Backend - Quick Start (5 Minutes)

Get your backend running in 5 minutes! 🚀

## Prerequisites

- ✅ Docker Desktop installed and running
- ✅ Anthropic API key ([get free key here](https://console.anthropic.com/))

## Step 1: Configure API Key (30 seconds)

Open `backend/.env` file and add your Anthropic API key:

```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

> **Note**: The file already exists with a pre-generated JWT secret key. You only need to add your Anthropic API key!

## Step 2: Start Everything (2 minutes)

```bash
cd backend
docker-compose up -d
```

Wait for services to start (~1-2 minutes on first run).

## Step 3: Verify It's Working (30 seconds)

Open your browser:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

You should see the Swagger UI with all API endpoints!

## Step 4: Test the Conversation Agent (2 minutes)

### Option A: Use the Example Client (Easiest)

```bash
python example_client.py
```

This will:
1. Register a test user
2. Start a conversation
3. Test the conversation agent
4. Show you the full flow

### Option B: Use curl

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "name": "Test User",
    "role": "analyst",
    "department": "operations",
    "accessScopes": ["operational_data"],
    "permissions": {"viewOperationalData": true}
  }'

# 2. Copy the accessToken from response and use it:
TOKEN="paste_your_token_here"

# 3. Start conversation
curl -X POST http://localhost:8000/api/v1/conversation/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "userMessage": "I need a presentation about Q3 performance",
    "cycleType": "generation"
  }'
```

### Option C: Use the API Docs UI

1. Go to http://localhost:8000/docs
2. Click on **POST /api/v1/auth/register**
3. Click **Try it out**
4. Use the example request body
5. Click **Execute**
6. Copy the `accessToken`
7. Click **Authorize** button (top right)
8. Paste token: `Bearer your_token_here`
9. Try **POST /api/v1/conversation/generate**

## That's It! 🎉

Your backend is now running with:
- ✅ MongoDB database
- ✅ User authentication
- ✅ Conversation agent with Claude
- ✅ RBAC system
- ✅ Full API documentation

## What's Running?

| Service | URL | Purpose |
|---------|-----|---------|
| Backend API | http://localhost:8000 | Main API |
| API Docs | http://localhost:8000/docs | Interactive documentation |
| MongoDB | localhost:27017 | Database |

## Quick Commands

```bash
# View logs
docker-compose logs -f backend

# Stop everything
docker-compose down

# Restart backend
docker-compose restart backend

# Check status
docker-compose ps
```

## Next Steps

1. **Read the README.md** for detailed information
2. **Check SETUP_GUIDE.md** for troubleshooting
3. **Integrate with your frontend** using the API endpoints
4. **Customize** user roles, permissions, and documents

## Common Issues

### "Anthropic API key invalid"
- Make sure you added your real API key to `.env`
- No extra spaces before/after the key
- Restart: `docker-compose restart backend`

### "Port 8000 already in use"
- Change `API_PORT=8001` in `.env`
- Restart: `docker-compose down && docker-compose up -d`

### "MongoDB connection failed"
- Wait a bit longer (MongoDB takes ~30s to start first time)
- Check: `docker-compose logs mongodb`
- Restart: `docker-compose restart mongodb`

## Getting Help

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Database Health**: http://localhost:8000/health/db
- **Logs**: `docker-compose logs -f backend`

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│         Your Frontend Application           │
└──────────────┬──────────────────────────────┘
               │ HTTP/REST API
               ▼
┌─────────────────────────────────────────────┐
│      FastAPI Backend (Port 8000)            │
│  ┌──────────────────────────────────────┐   │
│  │  Conversation Agent (Claude Sonnet)  │   │
│  └──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────┐   │
│  │  RBAC Service (Access Control)       │   │
│  └──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────┐   │
│  │  Authentication (JWT)                │   │
│  └──────────────────────────────────────┘   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      MongoDB (Port 27017)                   │
│  - Users & Profiles                         │
│  - Conversations & History                  │
│  - Documents & Access Control               │
└─────────────────────────────────────────────┘
```

## API Endpoints Summary

### Authentication
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get profile

### Conversation Agent
- `POST /api/v1/conversation/generate` - Generation mode
- `POST /api/v1/conversation/edit` - Editing mode
- `GET /api/v1/conversation/session/{id}` - Get session
- `GET /api/v1/conversation/history` - Get history

### Health
- `GET /health` - Service health
- `GET /health/db` - Database health

---

**You're all set!** Start building your frontend integration! 🚀

For detailed information, see:
- `README.md` - Full documentation
- `SETUP_GUIDE.md` - Detailed setup instructions
- `example_client.py` - Python integration example
