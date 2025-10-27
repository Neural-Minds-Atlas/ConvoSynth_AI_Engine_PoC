# ConvoSynth Backend

A production-ready FastAPI backend for the ConvoSynth conversation agent system, featuring dual-mode operation (presentation generation and editing), role-based access control (RBAC), and MongoDB integration.

## Features

- **Dual-Mode Conversation Agent**
  - Generation Mode: Gather requirements for new presentations
  - Editing Mode: Process modification requests for existing presentations

- **Role-Based Access Control (RBAC)**
  - User profiles with permissions
  - Document access filtering
  - Graceful access denial with professional messaging

- **Authentication & Security**
  - JWT-based authentication
  - Password hashing with bcrypt
  - Session management

- **MongoDB Integration**
  - Async MongoDB operations with Motor
  - Conversation history persistence
  - User and document management

- **LLM Integration**
  - Anthropic Claude Sonnet 4
  - LangChain agent framework
  - ReAct agent pattern

## Prerequisites

- Docker Desktop (for local development)
- Python 3.11+ (if running without Docker)
- Anthropic API key ([get one here](https://console.anthropic.com/))

## Quick Start

### 1. Clone and Setup

```bash
cd backend
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file and add your Anthropic API key:

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
JWT_SECRET_KEY=your-secret-key-change-this  # or generate with: openssl rand -hex 32
```

### 3. Start with Docker Compose

```bash
# Start MongoDB and Backend
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

The API will be available at:
- Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- MongoDB: localhost:27017

### 4. Optional: Start Mongo Express (Database UI)

```bash
docker-compose --profile dev up -d mongo-express
```

Access at http://localhost:8081 (username: `admin`, password: `admin123`)

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info

### Conversation

- `POST /api/v1/conversation/generate` - Generate mode conversation
- `POST /api/v1/conversation/edit` - Edit mode conversation
- `GET /api/v1/conversation/session/{session_id}` - Get session info
- `POST /api/v1/conversation/session/reset` - Reset session
- `DELETE /api/v1/conversation/session/{session_id}` - Delete session
- `GET /api/v1/conversation/history` - Get conversation history

### Health

- `GET /health` - Basic health check
- `GET /health/db` - Database health check

## Usage Examples

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@company.com",
    "password": "SecurePassword123",
    "name": "John Doe",
    "role": "senior_analyst",
    "department": "operations",
    "accessScopes": ["operational_data", "internal_metrics"],
    "permissions": {
      "viewFinancialData": false,
      "viewOperationalData": true,
      "viewHRData": false,
      "viewSalesData": false,
      "viewConfidentialData": false
    }
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@company.com",
    "password": "SecurePassword123"
  }'
```

Response:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "bearer",
  "user": {
    "userId": "usr_123456",
    "email": "john.doe@company.com",
    "profile": { ... }
  }
}
```

### 3. Start Conversation (Generation Mode)

```bash
TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/v1/conversation/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "userMessage": "I need to create a presentation about Q3 operational performance",
    "cycleType": "generation"
  }'
```

### 4. Continue Conversation

```bash
curl -X POST http://localhost:8000/api/v1/conversation/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "sessionId": "sess_abc123",
    "userMessage": "The presentation is for department leadership",
    "cycleType": "generation"
  }'
```

## Python SDK Example

```python
import requests

class ConvoSynthClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None

    def register(self, email, password, name, role, department):
        response = requests.post(
            f"{self.base_url}/api/v1/auth/register",
            json={
                "email": email,
                "password": password,
                "name": name,
                "role": role,
                "department": department,
                "accessScopes": ["operational_data"],
                "permissions": {
                    "viewOperationalData": True
                }
            }
        )
        data = response.json()
        self.token = data["accessToken"]
        return data

    def send_message(self, message, session_id=None):
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "userMessage": message,
            "cycleType": "generation"
        }
        if session_id:
            payload["sessionId"] = session_id

        response = requests.post(
            f"{self.base_url}/api/v1/conversation/generate",
            json=payload,
            headers=headers
        )
        return response.json()

# Usage
client = ConvoSynthClient()
client.register("test@example.com", "password123", "Test User", "analyst", "operations")

# Start conversation
result = client.send_message("I need a presentation about Q3 performance")
print(f"Agent: {result['response']}")

# Continue conversation
result = client.send_message(
    "It's for executive stakeholders",
    session_id=result['sessionId']
)
print(f"Agent: {result['response']}")
```

## Development

### Running Without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start MongoDB (separate terminal)
mongod --dbpath ./data/db

# Run the application
python -m app.main
# or
uvicorn app.main:app --reload
```

### Project Structure

```
backend/
├── app/
│   ├── agents/              # Conversation agent implementation
│   ├── api/                 # FastAPI routes
│   ├── db/                  # MongoDB models and repositories
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic layer
│   ├── utils/               # Utilities (logging, security, exceptions)
│   ├── config.py            # Configuration
│   └── main.py              # FastAPI application
├── tests/                   # Test suite
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile               # Docker image definition
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DB_NAME` | Database name | `convosynth` |
| `JWT_SECRET_KEY` | Secret key for JWT | Required |
| `API_PORT` | API server port | `8000` |
| `DEBUG` | Enable debug mode | `true` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_conversation_agent.py
```

## Troubleshooting

### MongoDB Connection Issues

```bash
# Check if MongoDB is running
docker-compose ps

# View MongoDB logs
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb
```

### Backend Errors

```bash
# View backend logs
docker-compose logs -f backend

# Rebuild backend container
docker-compose build backend
docker-compose up -d backend
```

### Authentication Issues

- Ensure JWT_SECRET_KEY is set in `.env`
- Check token expiration (default: 24 hours)
- Verify user is active in database

## Production Deployment

### Environment Setup

1. Set `ENVIRONMENT=production` in `.env`
2. Use a strong `JWT_SECRET_KEY`
3. Set `DEBUG=false`
4. Use MongoDB Atlas or managed MongoDB service
5. Configure CORS_ORIGINS for your frontend domains

### Docker Production Build

```bash
docker build -t convosynth-backend:latest .
docker run -p 8000:8000 --env-file .env convosynth-backend:latest
```

### Recommended Services

- **Hosting**: Render, Railway, AWS ECS, Google Cloud Run
- **MongoDB**: MongoDB Atlas, AWS DocumentDB
- **Monitoring**: Sentry, DataDog, New Relic

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review the logs: `docker-compose logs backend`

---

Built with FastAPI, LangChain, and Anthropic Claude
