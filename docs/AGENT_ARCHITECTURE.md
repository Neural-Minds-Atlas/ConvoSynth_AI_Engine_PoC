# ConvoSynth AI Engine - Agent Architecture

## Overview

The ConvoSynth AI Engine implements a sophisticated multi-agent system for generating professional financial presentations. Each agent is specialized for a specific task and uses the most appropriate LLM for its function.

## Agent Functionality Scheme

| Agent | Primary Function | LLM Selection | Response Time Target | Accuracy Target | Rationale | LangChain Implementation |
|-------|------------------|---------------|---------------------|-----------------|-----------|-------------------------|
| **Conversation Agent** | Talks with the user to gather missing information required for presentation generation | Mistral/Open Source | N/A | N/A | Superior conversational abilities | CONVERSATIONAL_REACT_DESCRIPTION |
| **Query Agent** | Extract context, intent, entities, and search strategy from user requirements | Claude-4 | <2 seconds | 98% intent accuracy | Superior information retrieval skills | OPENAI_FUNCTIONS/OPENAI_MULTI_FUNCTIONS |
| **RAG Engine** | Knowledge retrieval and context extraction from uploaded documents | Claude-4 | <3 seconds | 95% data accuracy | Best semantic/relevant search capabilities | Custom Implementation |
| **Outline Agent** | Generate an 8-10 slide structured outline with titles and key bullet points | GPT-4.1/Claude-4 | <2 seconds | 100% template compliance | Excellent structural reasoning | Zero-shot ReAct Agent or Plan-and-Execute Agent |
| **Content Agent** | Expand the outline into full-fledged content for each slide | Claude-4 | <4 seconds | 95% financial accuracy | Superior analytical and content writing capabilities | ZERO_SHOT_REACT_DESCRIPTION |
| **Image Coordination Agent** | Generate image specifications and visualizations for each slide | GPT-4.1/5 | <2 seconds | 90% visual relevance | Best prompt engineering for visuals | Tool Calling Agent |
| **QA Agent** | Validate generated content against uploaded documents using RAG engine | Claude-4 | <1 second | 99% error detection | Best quality assurance and reasoning abilities | ReAct Agent with Self-Ask Pattern |
| **Format Agent** | Professional HTML generation from content, images, and user preferences | Claude-4 | <2 seconds | 100% formatting compliance | Superior code generation abilities | Zero-shot Agent with Structured Output |
| **Validation Engine** | Final presentation completeness check and validation of user preferences | Claude-4 | <1 second | 100% completeness | Excellent systematic validation | Plan-and-Execute Agent |

## Architecture Diagram

```
User Request
    ↓
[Conversation Agent] ← (Optional: Gather missing info)
    ↓
[Query Agent] ← Extract intent, entities, search strategy
    ↓
[RAG Engine] ← Retrieve relevant context from documents
    ↓
[Outline Agent] ← Generate 8-10 slide structure
    ↓
[Content Agent] ← Expand outline into full content
    ↓
[Image Coordination Agent] ← Generate visualization specs
    ↓
[QA Agent] ← Validate against source documents
    ↓
[Format Agent] ← Generate professional HTML
    ↓
[Validation Engine] ← Final completeness check
    ↓
HTML Presentation
```

## Directory Structure

```
src/agents/
├── __init__.py                 # Main package initialization
├── config.py                   # Agent configurations
├── orchestrator.py             # Workflow orchestration
├── base/                       # Base classes and utilities
│   ├── __init__.py
│   ├── agent.py               # BaseAgent class
│   ├── models.py              # Data models (AgentRequest, AgentResponse, etc.)
│   └── llm_client.py          # LLM client factory (Claude, GPT, Cohere)
├── conversation/              # Conversation Agent
│   ├── __init__.py
│   ├── agent.py
│   └── prompts.py
├── query/                     # Query Agent
│   ├── __init__.py
│   └── agent.py
├── rag_engine/                # RAG Engine Agent
│   ├── __init__.py
│   └── agent.py
├── outline/                   # Outline Agent
│   ├── __init__.py
│   └── agent.py
├── content/                   # Content Agent
│   ├── __init__.py
│   └── agent.py
├── image_coordination/        # Image Coordination Agent
│   ├── __init__.py
│   └── agent.py
├── qa/                        # QA Agent
│   ├── __init__.py
│   └── agent.py
├── format/                    # Format Agent
│   ├── __init__.py
│   └── agent.py
└── validation/                # Validation Engine
    ├── __init__.py
    └── agent.py
```

## Agent Details

### 1. Conversation Agent

**Purpose**: Gather missing information through natural conversation

**LLM**: Mistral/Open Source
**Pattern**: CONVERSATIONAL_REACT_DESCRIPTION

**Key Features**:
- Natural language interaction
- Progressive information gathering
- Session management
- Context tracking

**Output**:
```json
{
  "response": "conversational message",
  "extracted_information": {...},
  "is_complete": false,
  "next_action": "continue_conversation"
}
```

### 2. Query Agent

**Purpose**: Extract intent, entities, and search strategy

**LLM**: Claude-4 (claude-sonnet-4-20250514)
**Pattern**: OPENAI_FUNCTIONS
**Targets**: <2s response, 98% intent accuracy

**Key Features**:
- Intent classification
- Entity extraction (companies, metrics, time periods)
- Search strategy determination
- Presentation metadata extraction

**Output**:
```json
{
  "query_context": {
    "primary_focus": "Q3 Financial Results",
    "intent": "create_presentation",
    "scope": "quarterly"
  },
  "entities": {
    "companies": ["Acme Corp"],
    "metrics": ["revenue", "profit"],
    "time_periods": ["Q3 2024"]
  },
  "search_strategy": {
    "vector_weight": 0.7,
    "graph_weight": 0.3
  }
}
```

### 3. RAG Engine

**Purpose**: Retrieve and synthesize relevant information

**LLM**: Claude-4
**Targets**: <3s response, 95% data accuracy

**Key Features**:
- Hybrid search (vector + knowledge graph)
- Document reranking
- Context synthesis
- Entity relationship extraction
- Source attribution

**Output**:
```json
{
  "retrieved_context": "relevant text...",
  "sources": ["doc1.pdf", "doc2.pdf"],
  "key_findings": ["finding1", "finding2"],
  "entities": {...},
  "relevance_scores": {...}
}
```

### 4. Outline Agent

**Purpose**: Generate 8-10 slide structured outline

**LLM**: Claude-4 or GPT-4.1
**Pattern**: Zero-shot ReAct / Plan-and-Execute
**Targets**: <2s response, 100% template compliance

**Key Features**:
- Logical slide progression
- 3-5 bullet points per slide
- Visual suggestions
- Narrative flow design

**Output**:
```json
{
  "outline": [
    {
      "slide_number": 1,
      "title": "Executive Summary",
      "bullet_points": ["point1", "point2"],
      "visual_suggestion": "chart"
    }
  ],
  "narrative_flow": "Problem-Solution-Impact",
  "total_slides": 10
}
```

### 5. Content Agent

**Purpose**: Expand outline into full slide content

**LLM**: Claude-4
**Pattern**: ZERO_SHOT_REACT_DESCRIPTION
**Targets**: <4s response, 95% financial accuracy

**Key Features**:
- Data-driven content expansion
- Metric integration
- Professional tone
- Factual accuracy

**Output**:
```json
{
  "slides": [
    {
      "slide_number": 1,
      "title": "Executive Summary",
      "content": {
        "main_points": ["detailed point with data"],
        "supporting_data": {"revenue": "$100M"},
        "narrative": "connecting text"
      }
    }
  ]
}
```

### 6. Image Coordination Agent

**Purpose**: Generate visualization specifications

**LLM**: GPT-4/5
**Pattern**: Tool Calling Agent
**Targets**: <2s response, 90% visual relevance

**Key Features**:
- Chart type selection
- Data mapping
- Design specifications
- Accessibility considerations

**Output**:
```json
{
  "visualizations": [
    {
      "slide_number": 1,
      "visual_type": "bar_chart",
      "data_to_visualize": {...},
      "chart_config": {...}
    }
  ]
}
```

### 7. QA Agent

**Purpose**: Validate content against source documents

**LLM**: Claude-4
**Pattern**: ReAct with Self-Ask
**Targets**: <1s response, 99% error detection

**Key Features**:
- Factual verification
- Source cross-referencing
- Hallucination detection
- Consistency checking

**Output**:
```json
{
  "validation_passed": true,
  "accuracy_score": 0.97,
  "errors_found": [],
  "warnings": [],
  "recommendations": []
}
```

### 8. Format Agent

**Purpose**: Generate professional HTML presentation

**LLM**: Claude-4
**Pattern**: Zero-shot with Structured Output
**Targets**: <2s response, 100% formatting compliance

**Key Features**:
- Responsive HTML/CSS
- Professional styling
- Accessibility standards
- Print-friendly design

**Output**:
```json
{
  "html": "<!DOCTYPE html>...",
  "format": "html",
  "is_valid": true
}
```

### 9. Validation Engine

**Purpose**: Final completeness and quality check

**LLM**: Claude-4
**Pattern**: Plan-and-Execute
**Targets**: <1s response, 100% completeness

**Key Features**:
- Comprehensive checklist
- User preference verification
- Completeness scoring
- Final recommendations

**Output**:
```json
{
  "validation_passed": true,
  "completeness_score": 1.0,
  "checklist": {...},
  "ready_for_delivery": true
}
```

## Usage

### Initialize Orchestrator

```python
from src.agents import AgentOrchestrator
from src.rag_anything.client import RAGAnythingClient

# Initialize RAG client
rag_client = RAGAnythingClient()
await rag_client.initialize()

# Create orchestrator
orchestrator = AgentOrchestrator(rag_client=rag_client)
await orchestrator.initialize()
```

### Run Full Workflow

```python
result = await orchestrator.run_full_workflow(
    user_request="Create a Q3 financial presentation for executives",
    documents=["q3_report.pdf", "financial_data.xlsx"],
    preferences={
        "theme": "professional",
        "num_slides": 10,
        "color_scheme": "blue"
    }
)

# Access presentation
html_presentation = result["presentation"]["html"]
metadata = result["metadata"]
```

### Run Conversation Workflow

```python
response = await orchestrator.run_conversation_workflow(
    user_message="I need help creating a presentation",
    session_id="user123"
)

print(response["response"])
if response["is_complete"]:
    # Proceed to full workflow
    pass
```

## Environment Variables

Required API keys in `.env`:

```bash
# Anthropic (Claude)
ANTHROPIC_API_KEY=your_key_here

# OpenAI (GPT-4)
OPENAI_API_KEY=your_key_here

# Cohere (optional)
COHERE_API_KEY=your_key_here

# Mistral (optional)
MISTRAL_API_KEY=your_key_here
```

## Performance Targets

All agents are configured with specific performance and accuracy targets:

- **Query Agent**: <2s, 98% intent accuracy
- **RAG Engine**: <3s, 95% data accuracy
- **Outline Agent**: <2s, 100% template compliance
- **Content Agent**: <4s, 95% financial accuracy
- **Image Agent**: <2s, 90% visual relevance
- **QA Agent**: <1s, 99% error detection
- **Format Agent**: <2s, 100% formatting compliance
- **Validation Engine**: <1s, 100% completeness

## Extensibility

### Adding New Agents

1. Create agent directory: `src/agents/new_agent/`
2. Implement agent class inheriting from `BaseAgent`
3. Add configuration to `config.py`
4. Register in orchestrator
5. Update workflow as needed

### Supporting New LLM Providers

1. Implement client in `base/llm_client.py`
2. Add provider to `LLMProvider` enum
3. Update `LLMClientFactory`
4. Configure in agent config

## Testing

```python
# Test individual agent
from src.agents import QueryAgent, AgentRequest

agent = QueryAgent()
request = AgentRequest(
    user_input="Create Q3 presentation",
    context={}
)

response = await agent.execute(request)
assert response.success
print(response.output)
```

## Monitoring

All agents emit structured logs:

```python
{
  "agent": "query_agent",
  "action": "query_analysis_complete",
  "intent": "create_presentation",
  "entity_count": 5,
  "execution_time": 1.2
}
```

## Error Handling

- All agents implement retry logic with exponential backoff
- Fallback responses for critical failures
- Detailed error logging
- Graceful degradation

## Best Practices

1. **Always initialize RAG client** before orchestrator
2. **Use session IDs** for conversation workflows
3. **Provide documents** for better context
4. **Set user preferences** for customized output
5. **Monitor performance metrics** against targets
6. **Validate outputs** before delivery
