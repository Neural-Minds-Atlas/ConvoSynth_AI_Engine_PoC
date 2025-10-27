"""Multi-Agent System for ConvoSynth AI Engine.

This package implements a sophisticated multi-agent system for generating
financial presentations using various LLM providers and specialized agents.

Agent Types:
- Conversation Agent: Gathers requirements from users (Mistral)
- Query Agent: Extracts intent and context (Claude-4)
- Document Selection Agent: Filters relevant documents using metadata RAG (Cohere)
- RAG Engine: Retrieves relevant information (Claude-4)
- Outline Agent: Generates presentation structure (Claude-4/GPT-4)
- Content Agent: Expands outline into full content (Claude-4)
- Image Coordination Agent: Specifies visualizations (GPT-4/5)
- QA Agent: Validates content accuracy (Claude-4)
- Format Agent: Generates HTML presentation (Claude-4)
- Validation Engine: Final completeness check (Claude-4)
"""

from .base import (
    BaseAgent,
    AgentRequest,
    AgentResponse,
    AgentType,
    AgentConfig,
    LLMProvider,
    LLMClientFactory,
)

from .config import AGENT_CONFIGS, get_agent_config, list_agent_configs

from .conversation import ConversationAgent
from .query import QueryAgent
from .document_selection import DocumentSelectionAgent
from .outline import OutlineAgent
from .content import ContentAgent
from .image_coordination import ImageCoordinationAgent
from .qa import QAAgent
from .format import FormatAgent
from .validation import ValidationAgent

from .orchestrator import AgentOrchestrator

__version__ = "1.0.0"

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentRequest",
    "AgentResponse",
    "AgentType",
    "AgentConfig",
    "LLMProvider",
    "LLMClientFactory",
    # Configuration
    "AGENT_CONFIGS",
    "get_agent_config",
    "list_agent_configs",
    # Agents
    "ConversationAgent",
    "QueryAgent",
    "DocumentSelectionAgent",
    "OutlineAgent",
    "ContentAgent",
    "ImageCoordinationAgent",
    "QAAgent",
    "FormatAgent",
    "ValidationAgent",
    # Orchestrator
    "AgentOrchestrator",
]
