# ConvoSynth Multi-Agent System

A sophisticated multi-agent system for automated financial presentation generation using specialized AI agents.

## Features

- **9 Specialized Agents** - Each optimized for specific tasks
- **Multi-LLM Support** - Claude-4, GPT-4, Cohere, Mistral
- **RAG Integration** - Context-aware content generation
- **Quality Assurance** - Automated validation and accuracy checking
- **Professional Output** - HTML presentations with responsive design

## Quick Start

```python
from src.agents import AgentOrchestrator

# Initialize
orchestrator = AgentOrchestrator()
await orchestrator.initialize()

# Generate presentation
result = await orchestrator.run_full_workflow(
    user_request="Create Q3 financial presentation",
    preferences={"theme": "professional", "num_slides": 10}
)

# Save output
with open("presentation.html", "w") as f:
    f.write(result["presentation"]["html"])
```

## Agent Pipeline

```
User Request → Query Agent → RAG Engine → Outline Agent →
Content Agent → Image Agent → QA Agent → Format Agent →
Validation Engine → HTML Presentation
```

## Agents Overview

| Agent | LLM | Purpose | Response Time |
|-------|-----|---------|---------------|
| Conversation | Mistral | Gather requirements | N/A |
| Query | Claude-4 | Extract intent | <2s |
| RAG Engine | Claude-4 | Retrieve context | <3s |
| Outline | Claude-4/GPT-4 | Generate structure | <2s |
| Content | Claude-4 | Expand content | <4s |
| Image | GPT-4/5 | Visualizations | <2s |
| QA | Claude-4 | Validate accuracy | <1s |
| Format | Claude-4 | Generate HTML | <2s |
| Validation | Claude-4 | Final check | <1s |

## Installation

```bash
pip install -r requirements.txt
```

Required API keys in `.env`:
```bash
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
```

## Documentation

- [Full Architecture](../../docs/AGENT_ARCHITECTURE.md)
- [Quick Start Guide](../../docs/AGENT_QUICKSTART.md)

## Configuration

Agent configurations in `src/agents/config.py`:

```python
from src.agents import get_agent_config, AgentType

config = get_agent_config(AgentType.QUERY)
print(config.model_name)  # claude-sonnet-4-20250514
print(config.temperature)  # 0.3
```

## Usage Examples

### Basic Generation

```python
result = await orchestrator.run_full_workflow(
    user_request="Q3 Results Presentation"
)
```

### With Documents

```python
result = await orchestrator.run_full_workflow(
    user_request="Q3 Results Presentation",
    documents=["report.pdf", "data.xlsx"]
)
```

### Conversational

```python
response = await orchestrator.run_conversation_workflow(
    user_message="I need a presentation",
    session_id="user123"
)
```

## Testing

```bash
# Test individual agent
python -c "
import asyncio
from src.agents import QueryAgent, AgentRequest

async def test():
    agent = QueryAgent()
    request = AgentRequest(user_input='Create presentation')
    response = await agent.execute(request)
    print(response.output)

asyncio.run(test())
"
```

## Performance Targets

- Query Agent: <2s, 98% accuracy
- RAG Engine: <3s, 95% accuracy
- Outline Agent: <2s, 100% template compliance
- Content Agent: <4s, 95% financial accuracy
- QA Agent: <1s, 99% error detection

## Architecture

```
src/agents/
├── base/              # Base classes, LLM clients
├── conversation/      # Conversation agent
├── query/             # Query analysis agent
├── rag_engine/        # RAG integration
├── outline/           # Outline generation
├── content/           # Content expansion
├── image_coordination/# Visualization specs
├── qa/                # Quality assurance
├── format/            # HTML generation
├── validation/        # Final validation
├── config.py          # Agent configurations
├── orchestrator.py    # Workflow orchestration
└── __init__.py        # Package exports
```

## Contributing

1. Follow existing agent patterns
2. Inherit from `BaseAgent`
3. Implement `_execute()` method
4. Add configuration to `config.py`
5. Register in orchestrator
6. Add tests

## License

Part of ConvoSynth AI Engine
