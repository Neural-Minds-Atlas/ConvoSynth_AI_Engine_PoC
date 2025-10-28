# Agents API Guide

## Overview

The Agents API provides endpoints for interacting with the ConvoSynth multi-agent system. The main endpoint is the **Conversation Agent** which gathers presentation requirements through natural conversation.

Base URL: `http://localhost:8000/api/v1/agents`

## Endpoints

### 1. Conversation Endpoint

**POST** `/conversation`

Interact with the Conversation Agent to gather presentation requirements.

**Request:**
```json
{
  "message": "I need to create a presentation about Q3 results",
  "session_id": "user_123",  // Optional, auto-generated if not provided
  "documents": ["q3_report.pdf"]  // Optional
}
```

**Response:**
```json
{
  "response": "Great! What's the main focus of your Q3 presentation?",
  "session_id": "user_123",
  "is_complete": false,
  "extracted_information": {
    "presentation_requirements": {
      "topic": "Q3 results",
      "target_audience": null,
      "num_slides": null,
      "key_themes": [],
      "tone": null
    },
    "data_requirements": {
      "documents": ["q3_report.pdf"],
      "metrics": [],
      "time_periods": ["Q3"]
    },
    "visual_preferences": {},
    "missing_information": ["target_audience", "num_slides"],
    "confidence_score": 0.3
  },
  "conversation_state": "gathering",
  "confidence_score": 0.3,
  "next_action": "continue_conversation"
}
```

### 2. Get Session Info

**GET** `/conversation/session/{session_id}`

Get information about a conversation session.

**Response:**
```json
{
  "session_id": "user_123",
  "exists": true,
  "message_count": 6,
  "is_complete": false,
  "extracted_info": {...}
}
```

### 3. Reset Session

**POST** `/conversation/reset`

Reset a conversation session.

**Request:**
```json
{
  "session_id": "user_123"
}
```

**Response:**
```json
{
  "message": "Conversation reset successfully",
  "session_id": "user_123"
}
```

### 4. List Sessions

**GET** `/conversation/sessions`

List all active conversation sessions.

**Response:**
```json
{
  "total_sessions": 2,
  "sessions": [
    {
      "session_id": "user_123",
      "message_count": 6,
      "is_complete": false,
      "confidence_score": 0.65,
      "state": "gathering"
    }
  ]
}
```

### 5. Delete Session

**DELETE** `/conversation/session/{session_id}`

Delete a conversation session.

**Response:**
```json
{
  "message": "Session deleted successfully",
  "session_id": "user_123"
}
```

### 6. Generate Presentation

**POST** `/generate-presentation`

Generate a complete presentation using the full agent workflow.

**Request:**
```json
{
  "user_request": "Create a Q3 financial presentation for executives",
  "documents": ["q3_report.pdf"],
  "preferences": {
    "theme": "professional",
    "num_slides": 10,
    "color_scheme": "blue"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Presentation generated successfully",
  "presentation": {
    "html": "<!DOCTYPE html>...",
    "outline": {...},
    "content": {...},
    "visualizations": [...]
  },
  "metadata": {
    "query_analysis": {...},
    "rag_sources": [...],
    "qa_results": {...},
    "validation_results": {...}
  }
}
```

### 7. Agents Info

**GET** `/agents/info`

Get information about available agents and configurations.

**Response:**
```json
{
  "available_agents": [
    "conversation",
    "query",
    "rag_engine",
    "outline",
    "content",
    "image_coordination",
    "qa",
    "format",
    "validation"
  ],
  "agent_configs": {...},
  "workflows": {...}
}
```

## Usage Examples

### Example 1: Basic Conversation

```bash
# Start conversation
curl -X POST http://localhost:8000/api/v1/agents/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need help creating a presentation"
  }'

# Continue conversation (use session_id from response)
curl -X POST http://localhost:8000/api/v1/agents/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Its about Q3 financial results for executives",
    "session_id": "conv_abc123def456"
  }'
```

### Example 2: Using Python requests

```python
import requests

# Start conversation
response = requests.post(
    "http://localhost:8000/api/v1/agents/conversation",
    json={
        "message": "I need to create a presentation",
        "documents": ["report.pdf"]
    }
)

data = response.json()
session_id = data["session_id"]
print(f"Agent: {data['response']}")

# Continue conversation
response = requests.post(
    "http://localhost:8000/api/v1/agents/conversation",
    json={
        "message": "It's about Q3 results for executives",
        "session_id": session_id
    }
)

print(f"Agent: {response.json()['response']}")
```

### Example 3: Full Workflow

```python
import requests

# Generate presentation directly
response = requests.post(
    "http://localhost:8000/api/v1/agents/generate-presentation",
    json={
        "user_request": "Create a Q3 financial presentation",
        "documents": ["q3_report.pdf"],
        "preferences": {
            "theme": "professional",
            "num_slides": 10
        }
    }
)

result = response.json()
if result["success"]:
    html = result["presentation"]["html"]
    # Save HTML
    with open("presentation.html", "w") as f:
        f.write(html)
```

## Conversation Flow

1. **Start Conversation**: Send initial message
2. **Agent Asks Questions**: Agent will ask clarifying questions
3. **Provide Information**: Answer agent's questions
4. **Monitor Progress**: Check `confidence_score` and `is_complete`
5. **Completion**: When `is_complete` is `true`, information gathering is done
6. **Generate Presentation**: Use extracted information for generation

## Session Management

- **Session IDs**: Auto-generated if not provided
- **Session Storage**: In-memory (use Redis in production)
- **Session Lifetime**: Until server restart or manual deletion
- **Multiple Sessions**: Each user can have their own session

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `404 Not Found`: Session not found
- `422 Validation Error`: Invalid request data
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message",
  "errors": ["error details"]
}
```

## Rate Limiting

Default rate limits (configurable in `.env`):
- 60 requests per minute
- 1000 requests per hour

## Authentication

Optional API key authentication (set `API_KEY` in `.env`):

```bash
curl -X POST http://localhost:8000/api/v1/agents/conversation \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## Testing

### Run Test Script

```bash
python examples/test_conversation_api.py
```

### Interactive Mode

```bash
python examples/test_conversation_api.py
# Choose option 1 for interactive conversation
```

### Use API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI

## Best Practices

1. **Maintain Session ID**: Store and reuse session_id for conversation continuity
2. **Check Completeness**: Monitor `is_complete` and `confidence_score`
3. **Handle Errors**: Implement retry logic for failed requests
4. **Clean Up**: Delete sessions when done to free memory
5. **Document Upload**: Provide document paths when available for better context

## Future Agents

The `/api/v1/agents` route is designed for easy extension. Future agents can be added by:

1. Creating agent endpoint in `src/api/routes/agents.py`
2. Following the same request/response pattern
3. Using the AgentOrchestrator for multi-agent workflows

Example for future Query Agent endpoint:
```python
@router.post("/query-analysis", tags=["agents"])
async def query_analysis_endpoint(request: QueryRequest):
    agent = QueryAgent()
    response = await agent.execute(...)
    return response
```

## Support

- API Documentation: http://localhost:8000/docs
- Architecture Docs: `docs/AGENT_ARCHITECTURE.md`
- Quick Start: `docs/AGENT_QUICKSTART.md`
