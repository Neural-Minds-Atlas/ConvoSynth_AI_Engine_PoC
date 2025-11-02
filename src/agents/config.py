"""Agent configurations based on functionality scheme."""
from typing import Dict
from .base import AgentConfig, AgentType, LLMProvider


# Agent Configuration Dictionary
AGENT_CONFIGS: Dict[AgentType, AgentConfig] = {
    # Conversation Agent - Claude (Anthropic)
    AgentType.CONVERSATION: AgentConfig(
        agent_type=AgentType.CONVERSATION,
        llm_provider=LLMProvider.ANTHROPIC,  # Using Claude for superior conversation
        model_name="claude-sonnet-4-20250514",
        temperature=0.8,  # Higher for more conversational
        max_tokens=2048,
        timeout=30,
        max_retries=3,
        langchain_agent_type="CONVERSATIONAL_REACT_DESCRIPTION",
        response_time_target=None,  # No strict target
        accuracy_target=None,
    ),

    # Query Agent - Claude-4
    AgentType.QUERY: AgentConfig(
        agent_type=AgentType.QUERY,
        llm_provider=LLMProvider.ANTHROPIC,
        model_name="claude-sonnet-4-20250514",
        temperature=0.3,  # Lower for precise intent extraction
        max_tokens=2048,
        timeout=30,
        max_retries=3,
        langchain_agent_type="OPENAI_FUNCTIONS",
        response_time_target=2.0,  # <2 seconds
        accuracy_target=0.98,  # 98% intent accuracy
    ),

    # Document Selection Agent - Cohere
    AgentType.DOCUMENT_SELECTION: AgentConfig(
        agent_type=AgentType.DOCUMENT_SELECTION,
        llm_provider=LLMProvider.COHERE,
        model_name="command-r-plus-08-2024",  # Updated model name
        temperature=0.4,  # Balanced for reasoning
        max_tokens=2048,
        timeout=30,
        max_retries=3,
        langchain_agent_type="ZERO_SHOT_REACT_DESCRIPTION",  # Zero-shot ReAct with MetaData RAG Tool
        response_time_target=3.0,  # <3 seconds
        accuracy_target=0.95,  # 95% relevance
    ),

    # RAG Engine - Claude-4
    AgentType.RAG_ENGINE: AgentConfig(
        agent_type=AgentType.RAG_ENGINE,
        llm_provider=LLMProvider.ANTHROPIC,
        model_name="claude-sonnet-4-20250514",
        temperature=0.4,
        max_tokens=4096,
        timeout=30,
        max_retries=3,
        langchain_agent_type=None,  # Custom implementation
        response_time_target=3.0,  # <3 seconds
        accuracy_target=0.95,  # 95% data accuracy
    ),

    # Outline Agent - GPT-4.1/Claude-4
    AgentType.OUTLINE: AgentConfig(
        agent_type=AgentType.OUTLINE,
        llm_provider=LLMProvider.ANTHROPIC,  # Can switch to OPENAI for GPT-4.1
        model_name="claude-sonnet-4-20250514",
        temperature=0.5,  # Balanced for structure
        max_tokens=8000,  # Increased for complex JSON structure with nested slides
        timeout=30,
        max_retries=3,
        langchain_agent_type="ZERO_SHOT_REACT_DESCRIPTION",  # Or Plan-and-Execute
        response_time_target=2.0,  # <2 seconds
        accuracy_target=1.0,  # 100% template compliance
    ),

    # Content Agent - Claude-4
    AgentType.CONTENT: AgentConfig(
        agent_type=AgentType.CONTENT,
        llm_provider=LLMProvider.ANTHROPIC,
        model_name="claude-sonnet-4-20250514",
        temperature=0.6,  # Balanced for content generation
        max_tokens=4096,
        timeout=30,
        max_retries=3,
        langchain_agent_type="ZERO_SHOT_REACT_DESCRIPTION",
        response_time_target=4.0,  # <4 seconds
        accuracy_target=0.95,  # 95% financial accuracy
    ),

    # Image Coordination Agent - GPT-4.1/5
    AgentType.IMAGE_COORDINATION: AgentConfig(
        agent_type=AgentType.IMAGE_COORDINATION,
        llm_provider=LLMProvider.OPENAI,
        model_name="gpt-4-turbo",  # or gpt-4o for vision
        temperature=0.7,
        max_tokens=2048,
        timeout=30,
        max_retries=3,
        langchain_agent_type="TOOL_CALLING_AGENT",
        response_time_target=2.0,  # <2 seconds
        accuracy_target=0.90,  # 90% visual relevance
    ),

    # QA Agent - Claude-4
    AgentType.QA: AgentConfig(
        agent_type=AgentType.QA,
        llm_provider=LLMProvider.ANTHROPIC,
        model_name="claude-sonnet-4-20250514",
        temperature=0.2,  # Very low for precise validation
        max_tokens=2048,
        timeout=30,
        max_retries=3,
        langchain_agent_type="REACT_AGENT",  # ReAct with Self-Ask Pattern
        response_time_target=1.0,  # <1 second
        accuracy_target=0.99,  # 99% error detection
    ),

    # Format Agent - Claude-4
    AgentType.FORMAT: AgentConfig(
        agent_type=AgentType.FORMAT,
        llm_provider=LLMProvider.ANTHROPIC,
        model_name="claude-sonnet-4-20250514",
        temperature=0.3,  # Low for precise formatting
        max_tokens=8192,  # Higher for HTML generation
        timeout=30,
        max_retries=3,
        langchain_agent_type="ZERO_SHOT_REACT_DESCRIPTION",  # Zero-shot with Structured Output
        response_time_target=2.0,  # <2 seconds
        accuracy_target=1.0,  # 100% formatting compliance
    ),

    # Validation Engine - Claude-4
    AgentType.VALIDATION: AgentConfig(
        agent_type=AgentType.VALIDATION,
        llm_provider=LLMProvider.ANTHROPIC,
        model_name="claude-sonnet-4-20250514",
        temperature=0.1,  # Lowest for systematic validation
        max_tokens=2048,
        timeout=30,
        max_retries=3,
        langchain_agent_type="PLAN_AND_EXECUTE",
        response_time_target=1.0,  # <1 second
        accuracy_target=1.0,  # 100% completeness check
    ),
}


def get_agent_config(agent_type: AgentType) -> AgentConfig:
    """Get configuration for a specific agent type.

    Args:
        agent_type: Type of agent

    Returns:
        Agent configuration

    Raises:
        ValueError: If agent type not found
    """
    if agent_type not in AGENT_CONFIGS:
        raise ValueError(f"No configuration found for agent type: {agent_type}")

    return AGENT_CONFIGS[agent_type]


def list_agent_configs() -> Dict[str, Dict]:
    """List all agent configurations.

    Returns:
        Dictionary mapping agent type to config dict
    """
    return {
        agent_type.value: {
            "llm_provider": config.llm_provider.value,
            "model": config.model_name,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "langchain_agent_type": config.langchain_agent_type,
            "response_time_target": config.response_time_target,
            "accuracy_target": config.accuracy_target,
        }
        for agent_type, config in AGENT_CONFIGS.items()
    }
