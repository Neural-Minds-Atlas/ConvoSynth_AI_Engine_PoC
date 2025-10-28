# Agent System Quick Start Guide

## Installation & Setup

### 1. Install Dependencies

All required dependencies are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `anthropic` - Claude API
- `openai` - GPT-4 API
- `cohere` - Cohere API
- `langchain` - Agent framework
- `fastapi` - API server
- `structlog` - Structured logging

### 2. Configure Environment Variables

Create or update `.env` file:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Optional
COHERE_API_KEY=...
MISTRAL_API_KEY=...

# Application settings
DEBUG=True
LOG_LEVEL=INFO
```

### 3. Initialize RAG System (if using documents)

```python
from src.rag_anything.client import RAGAnythingClient

rag_client = RAGAnythingClient()
await rag_client.initialize()
```

## Basic Usage

### Example 1: Simple Presentation Generation

```python
import asyncio
from src.agents import AgentOrchestrator

async def create_presentation():
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()

    # Generate presentation
    result = await orchestrator.run_full_workflow(
        user_request="Create a Q3 2024 financial presentation",
        documents=None,  # No documents
        preferences={
            "theme": "professional",
            "num_slides": 8
        }
    )

    # Save HTML
    if result["success"]:
        with open("presentation.html", "w") as f:
            f.write(result["presentation"]["html"])
        print("✓ Presentation created successfully!")
    else:
        print(f"✗ Error: {result['error']}")

# Run
asyncio.run(create_presentation())
```

### Example 2: With Document Upload

```python
import asyncio
from pathlib import Path
from src.agents import AgentOrchestrator
from src.rag_anything.client import RAGAnythingClient

async def create_presentation_with_docs():
    # Initialize RAG client
    rag_client = RAGAnythingClient()
    await rag_client.initialize()

    # Process documents
    documents = [
        Path("data/q3_report.pdf"),
        Path("data/financial_data.xlsx")
    ]

    for doc in documents:
        await rag_client.process_document(doc)

    # Initialize orchestrator with RAG
    orchestrator = AgentOrchestrator(rag_client=rag_client)
    await orchestrator.initialize()

    # Generate presentation
    result = await orchestrator.run_full_workflow(
        user_request="Create executive summary of Q3 results",
        documents=[str(d) for d in documents],
        preferences={
            "theme": "corporate",
            "num_slides": 10,
            "audience": "executives"
        }
    )

    # Save and report
    if result["success"]:
        with open("presentation.html", "w") as f:
            f.write(result["presentation"]["html"])

        print("✓ Presentation created!")
        print(f"  Slides: {len(result['presentation']['outline']['outline'])}")
        print(f"  Sources: {len(result['metadata']['rag_sources'])}")
        print(f"  QA Score: {result['metadata']['qa_results'].get('accuracy_score', 'N/A')}")
        print(f"  Validation: {'✓' if result['metadata']['validation_results'].get('validation_passed') else '✗'}")
    else:
        print(f"✗ Error: {result['error']}")

asyncio.run(create_presentation_with_docs())
```

### Example 3: Conversational Workflow

```python
import asyncio
from src.agents import AgentOrchestrator

async def conversation_example():
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()

    session_id = "user_123"

    # First message
    response1 = await orchestrator.run_conversation_workflow(
        user_message="I need to create a presentation",
        session_id=session_id
    )
    print(f"Agent: {response1['response']}")
    print(f"Complete: {response1['is_complete']}\n")

    # Second message
    response2 = await orchestrator.run_conversation_workflow(
        user_message="It's about Q3 financial results for executives",
        session_id=session_id
    )
    print(f"Agent: {response2['response']}")
    print(f"Complete: {response2['is_complete']}\n")

    # Continue until complete...
    if response2['is_complete']:
        # Extract gathered information
        info = response2['extracted_information']

        # Run full workflow
        result = await orchestrator.run_full_workflow(
            user_request=info['presentation_requirements']['topic'],
            preferences=info['presentation_requirements']
        )

        print("✓ Conversation complete, presentation generated!")

asyncio.run(conversation_example())
```

### Example 4: Using Individual Agents

```python
import asyncio
from src.agents import QueryAgent, AgentRequest

async def test_query_agent():
    # Initialize agent
    agent = QueryAgent()

    # Create request
    request = AgentRequest(
        user_input="Create a 10-slide deck about Q3 revenue growth",
        context={}
    )

    # Execute
    response = await agent.execute(request)

    if response.success:
        print("✓ Query Analysis:")
        print(f"  Intent: {response.output['query_context']['intent']}")
        print(f"  Entities: {response.output['entities']}")
        print(f"  Search Strategy: {response.output['search_strategy']}")
    else:
        print(f"✗ Error: {response.errors}")

asyncio.run(test_query_agent())
```

## API Integration

### FastAPI Endpoint Example

```python
from fastapi import FastAPI, UploadFile, File
from src.agents import AgentOrchestrator
from src.rag_anything.client import RAGAnythingClient

app = FastAPI()

# Initialize on startup
@app.on_event("startup")
async def startup():
    app.state.rag_client = RAGAnythingClient()
    await app.state.rag_client.initialize()

    app.state.orchestrator = AgentOrchestrator(app.state.rag_client)
    await app.state.orchestrator.initialize()

# Presentation generation endpoint
@app.post("/api/v1/generate-presentation")
async def generate_presentation(
    request: str,
    theme: str = "professional",
    num_slides: int = 10
):
    result = await app.state.orchestrator.run_full_workflow(
        user_request=request,
        preferences={
            "theme": theme,
            "num_slides": num_slides
        }
    )

    return {
        "success": result["success"],
        "html": result["presentation"]["html"] if result["success"] else None,
        "metadata": result.get("metadata", {})
    }

# Document upload endpoint
@app.post("/api/v1/upload-document")
async def upload_document(file: UploadFile = File(...)):
    # Save file
    file_path = f"data/uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Process with RAG
    await app.state.rag_client.process_document(Path(file_path))

    return {"message": "Document processed", "filename": file.filename}
```

## Configuration

### Customize Agent Behavior

```python
from src.agents import AgentType, get_agent_config

# Get agent configuration
config = get_agent_config(AgentType.OUTLINE)

print(f"Model: {config.model_name}")
print(f"Temperature: {config.temperature}")
print(f"Max Tokens: {config.max_tokens}")
print(f"Response Target: {config.response_time_target}s")
```

### Override Agent Config

```python
from src.agents.base import AgentConfig, LLMProvider
from src.agents import OutlineAgent

# Custom config
custom_config = AgentConfig(
    agent_type=AgentType.OUTLINE,
    llm_provider=LLMProvider.OPENAI,
    model_name="gpt-4-turbo",
    temperature=0.3,
    max_tokens=4096
)

# Create agent with custom config
agent = OutlineAgent()
agent.config = custom_config
```

## Monitoring & Logging

### View Agent Logs

```python
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
)

logger = structlog.get_logger()

# Logs will show:
# {"event": "agent_execution_started", "agent": "query_agent", "timestamp": "..."}
# {"event": "query_analysis_complete", "intent": "create_presentation", ...}
```

### Track Performance

```python
result = await orchestrator.run_full_workflow(...)

# Check execution times
for agent_name, output in result["all_outputs"].items():
    if isinstance(output, dict) and "execution_time" in output:
        print(f"{agent_name}: {output['execution_time']:.2f}s")
```

## Troubleshooting

### Common Issues

**1. API Key Not Set**
```
ValueError: ANTHROPIC_API_KEY environment variable not set
```
Solution: Add API keys to `.env` file

**2. RAG Client Not Initialized**
```
Exception: RAG client not initialized
```
Solution: Call `await rag_client.initialize()` before use

**3. Import Errors**
```
ModuleNotFoundError: No module named 'anthropic'
```
Solution: `pip install -r requirements.txt`

**4. JSON Parsing Errors**
```
ValueError: Failed to parse JSON response
```
Solution: Agent retry logic should handle this; check temperature settings

### Enable Debug Mode

```python
import os
os.environ["DEBUG"] = "True"

# More verbose logging
import structlog
structlog.configure(
    processors=[
        structlog.dev.ConsoleRenderer()  # Human-readable
    ]
)
```

## Next Steps

1. Read [AGENT_ARCHITECTURE.md](./AGENT_ARCHITECTURE.md) for detailed agent information
2. Explore [examples/](../examples/) directory for more use cases
3. Check [tests/](../tests/) for test examples
4. Review API documentation at `/docs` when running the FastAPI server

## Support

For issues or questions:
- Check existing documentation
- Review error logs
- Test individual agents
- Verify environment variables
- Check API rate limits
