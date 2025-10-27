#!/usr/bin/env python3
"""
ConvoSynth Claude Initialization Script

This script provides Claude with comprehensive context about the ConvoSynth project
and sets up the development environment for optimal AI-assisted development.

Usage:
    python scripts/claude_init.py

This script should be run at the beginning of any Claude session to provide
full project context and enable efficient development assistance.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

def print_header():
    """Print the initialization header"""
    print("=" * 80)
    print("🚀 CONVOSYNTH - CLAUDE INITIALIZATION SCRIPT")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Project Root: {Path.cwd()}")
    print("=" * 80)

def project_overview():
    """Provide comprehensive project overview"""
    overview = """
## PROJECT CONTEXT FOR CLAUDE

### ConvoSynth Overview
ConvoSynth is a multi-agent RAG system that transforms financial documents into 
professional presentations in <15 seconds. The system uses 9 specialized AI agents
working in orchestrated harmony to deliver high-quality financial analysis.

### Current Development Phase
- **Phase**: Initial Development & Architecture Setup
- **Timeline**: 30-day sprint (Days 1-30)
- **Team**: 2 developers (Shanawaz, Pratham)
- **Status**: Foundation setup and planning

### Key Architecture Components
1. **Multi-Agent System**: 9 specialized agents with distinct roles
2. **RAG Pipeline**: Advanced document processing and retrieval
3. **Orchestration Layer**: LangChain/LangGraph workflow management
4. **Storage**: Redis (sessions) + Qdrant (vectors)
5. **API Layer**: FastAPI with async processing

### Performance Requirements
- End-to-end latency: <15 seconds (p95)
- Output: 8-10 professional slides
- Accuracy: >90% factual correctness
- Scalability: Handle 100+ concurrent requests

### Technology Stack
- **Backend**: Python 3.11+, FastAPI, LangChain
- **LLMs**: Claude-4, GPT-4.1, Gemini 1.5/2.5
- **Storage**: Redis, Qdrant vector DB
- **Monitoring**: LangSmith tracing
- **Deployment**: Docker, Kubernetes
"""
    return overview

def agent_architecture():
    """Detail the agent architecture"""
    agents = """
### AGENT ARCHITECTURE DETAILS

#### 1. Conversation Agent 
- **Role**: User interaction and requirements extraction
- **Input**: User queries, conversation history
- **Output**: Structured requirements, handoff signals
- **SLA**: <2 seconds response time
- **Key Features**: Natural conversation, context retention

#### 2. Query Agent 
- **Role**: Document intake and intent parsing
- **Input**: Documents, user requirements
- **Output**: Parsed intents, document structure
- **SLA**: <2 seconds response time
- **Key Features**: Multi-format parsing, intent classification

#### 3. RAG Engine 
- **Role**: Knowledge retrieval and semantic search
- **Input**: Queries, document corpus
- **Output**: Relevant context, ranked results
- **SLA**: <3 seconds response time
- **Key Features**: Advanced retrieval, reranking

#### 4. Outline Agent 
- **Role**: Slide structure generation
- **Input**: Requirements, content themes
- **Output**: 8-10 slide outline with spatial hints
- **SLA**: <2 seconds response time
- **Key Features**: Template-aware, constraint enforcement

#### 5. Content Agent 
- **Role**: Financial analysis and content creation
- **Input**: Data, outline, context
- **Output**: Slide content with analysis
- **SLA**: <4 seconds response time
- **Key Features**: Financial expertise, numeric validation

#### 6. Image Coordination Agent 
- **Role**: Visual content generation coordination
- **Input**: Content requirements, data
- **Output**: Chart specifications, image requests
- **SLA**: <3 seconds response time
- **Key Features**: Multimodal understanding, tool coordination

#### 7. QA Agent 
- **Role**: Content validation and accuracy checking
- **Input**: Generated content, source documents
- **Output**: Validation results, correction suggestions
- **SLA**: <2 seconds response time
- **Key Features**: Fact-checking, consistency validation

#### 8. Format Agent 
- **Role**: HTML presentation formatting
- **Input**: Content, images, styling requirements
- **Output**: Professional HTML slides
- **SLA**: <3 seconds response time
- **Key Features**: Responsive design, component reuse

#### 9. Validation Engine
- **Role**: Final completeness verification
- **Input**: Complete presentation
- **Output**: Final validation, auto-repairs
- **SLA**: <2 seconds response time
- **Key Features**: Completeness checks, auto-fix capabilities
"""
    return agents

def development_context():
    """Provide development context and guidelines"""
    context = """
### DEVELOPMENT CONTEXT & GUIDELINES

#### Current Priority Tasks
1. **Foundation Setup**: Project structure, environment, base classes
2. **RAG System**: Document ingestion, embedding, vector storage
3. **Agent Development**: Implement agents following base architecture
4. **Integration**: Orchestration workflow and testing
5. **Optimization**: Performance tuning and production readiness

#### Code Architecture Principles
- **Modular Design**: Each agent is self-contained with clear interfaces
- **Async-First**: All I/O operations use async/await patterns
- **Contract-Driven**: Strict input/output schemas using Pydantic
- **Observable**: Comprehensive tracing and monitoring
- **Testable**: Unit, integration, and E2E test coverage

#### File Organization Standards
- One agent per module in `/src/agents/{agent_name}/`
- Shared utilities in `/src/utils/`
- Configuration in `/config/`
- Tests mirror source structure in `/tests/`

#### Performance Considerations
- **Caching**: Multi-level caching (Redis, in-memory)
- **Parallelization**: Concurrent agent execution where possible
- **Connection Pooling**: Reuse HTTP connections to LLM APIs
- **Resource Management**: Proper cleanup and resource limits

#### Error Handling Strategy
- **Graceful Degradation**: System continues with reduced functionality
- **Retry Logic**: Exponential backoff for transient failures
- **Circuit Breakers**: Prevent cascade failures
- **Comprehensive Logging**: Structured logs with correlation IDs
"""
    return context

def current_status():
    """Show current project status"""
    status = """
### CURRENT PROJECT STATUS

#### Completed ✅
- [x] Project planning and architecture design
- [x] Task breakdown and developer assignment
- [x] Folder structure definition
- [x] Technology stack decisions

#### In Progress 🔄
- [ ] Repository setup and initial structure
- [ ] Environment configuration
- [ ] Base agent classes and interfaces
- [ ] Docker compose setup

#### Next Steps 📋
1. **Immediate (Today)**:
   - Set up project repository with folder structure
   - Create base agent classes and schemas
   - Configure development environment
   - Set up Docker compose for local services

2. **This Week**:
   - Implement RAG ingestion pipeline
   - Set up Qdrant vector database
   - Create first agent (Conversation Agent)
   - Establish testing framework

3. **Next Week**:
   - Complete core agents implementation
   - Build orchestration workflow
   - Integration testing
   - Performance benchmarking

#### Blockers & Risks ⚠️
- **API Access**: Ensure all LLM provider APIs are accessible
- **Resource Limits**: Monitor API rate limits and costs
- **Performance**: Early performance testing to validate <15s target
- **Integration Complexity**: Agent coordination complexity
"""
    return status

def helpful_commands():
    """Provide helpful development commands"""
    commands = """
### HELPFUL DEVELOPMENT COMMANDS

#### Project Setup
```bash
# Initialize project structure
python scripts/setup_project.py

# Install dependencies
pip install -e .

# Start local services
docker-compose up -d

# Run development server
make dev
```

#### Development Workflow
```bash
# Run tests
make test

# Format code
make format

# Type checking
make type-check

# Run specific agent tests
pytest tests/unit/agents/conversation/

# Load testing
make load-test
```

#### Debugging & Monitoring
```bash
# View logs
docker-compose logs -f api

# Check system health
curl http://localhost:8000/health

# Monitor agent performance
python scripts/performance_monitor.py
```

#### Common Development Tasks
```bash
# Add new agent
python scripts/create_agent.py --name new_agent --llm claude-4

# Run RAG evaluation
python scripts/evaluate_rag.py --dataset financial_docs

# Generate API documentation
make docs

# Deploy to staging
make deploy-staging
```
"""
    return commands

def print_initialization_complete():
    """Print completion message"""
    print("\n" + "=" * 80)
    print("✅ CLAUDE INITIALIZATION COMPLETE")
    print("=" * 80)
    print("""
Claude now has full context of the ConvoSynth project including:
- Project architecture and agent design
- Development guidelines and standards  
- Current status and next steps
- Helpful commands and workflows

You can now ask Claude to help with:
- Implementing specific agents or components
- Code review and optimization
- Architecture decisions and trade-offs
- Debugging and troubleshooting
- Testing strategies and implementation
- Performance optimization
- Documentation and planning

Example prompts:
- "Help me implement the Conversation Agent"
- "Review this RAG pipeline code"
- "Optimize the agent orchestration workflow"
- "Create tests for the Query Agent"
- "Help debug the vector search performance"
""")
    print("=" * 80)

def main():
    """Main initialization function"""
    print_header()

    print("\n📋 PROJECT OVERVIEW")
    print(project_overview())

    print("\n🤖 AGENT ARCHITECTURE")
    print(agent_architecture())

    print("\n💻 DEVELOPMENT CONTEXT")
    print(development_context())

    print("\n📊 CURRENT STATUS")
    print(current_status())

    print("\n⚡ HELPFUL COMMANDS")
    print(helpful_commands())

    print_initialization_complete()

if __name__ == "__main__":
    main()
