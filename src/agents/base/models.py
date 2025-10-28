"""Data models for agents."""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Agent types based on functionality."""
    CONVERSATION = "conversation"
    QUERY = "query"
    DOCUMENT_SELECTION = "document_selection"
    RAG_ENGINE = "rag_engine"
    OUTLINE = "outline"
    CONTENT = "content"
    IMAGE_COORDINATION = "image_coordination"
    QA = "qa"
    FORMAT = "format"
    VALIDATION = "validation"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    ANTHROPIC = "anthropic"  # Claude
    OPENAI = "openai"  # GPT-4
    COHERE = "cohere"  # Cohere models


class AgentRequest(BaseModel):
    """Request model for agent execution."""
    user_input: str = Field(..., description="User input or query")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    documents: Optional[List[str]] = Field(default=None, description="List of document paths")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User preferences")
    session_id: Optional[str] = Field(default=None, description="Session identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "Create a presentation about Q3 financial results",
                "context": {"company": "Acme Corp", "quarter": "Q3"},
                "documents": ["financial_report_q3.pdf"],
                "preferences": {"theme": "professional", "slides": 10}
            }
        }


class AgentResponse(BaseModel):
    """Response model from agent execution."""
    agent_type: AgentType = Field(..., description="Type of agent that processed the request")
    success: bool = Field(..., description="Whether execution was successful")
    output: Dict[str, Any] = Field(..., description="Agent output data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    errors: Optional[List[str]] = Field(default=None, description="Error messages if any")

    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "outline",
                "success": True,
                "output": {
                    "outline": [
                        {"slide": 1, "title": "Q3 Overview", "bullets": ["Revenue", "Expenses"]}
                    ]
                },
                "metadata": {"execution_time": 1.5, "model": "claude-4"}
            }
        }


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    agent_type: AgentType
    llm_provider: LLMProvider
    model_name: str = Field(..., description="Specific model name (e.g., claude-4-sonnet)")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=100, le=100000)
    timeout: int = Field(default=30, description="Timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10)
    langchain_agent_type: Optional[str] = Field(default=None, description="LangChain agent type")

    # Performance targets
    response_time_target: Optional[float] = Field(default=None, description="Target response time in seconds")
    accuracy_target: Optional[float] = Field(default=None, description="Target accuracy (0-1)")

    class Config:
        protected_namespaces = ()  # Allow model_ prefix fields
        json_schema_extra = {
            "example": {
                "agent_type": "query",
                "llm_provider": "anthropic",
                "model_name": "claude-4-sonnet-20250514",
                "temperature": 0.3,
                "max_tokens": 2048,
                "response_time_target": 2.0,
                "accuracy_target": 0.98,
                "langchain_agent_type": "OPENAI_FUNCTIONS"
            }
        }


class PromptTemplate(BaseModel):
    """Template for agent prompts."""
    system_prompt: str = Field(..., description="System prompt for the agent")
    user_prompt_template: str = Field(..., description="Template for user prompts with placeholders")
    few_shot_examples: Optional[List[Dict[str, str]]] = Field(default=None, description="Few-shot examples")

    class Config:
        json_schema_extra = {
            "example": {
                "system_prompt": "You are a financial analysis expert.",
                "user_prompt_template": "Analyze the following data: {data}",
                "few_shot_examples": [
                    {"input": "Revenue: $100M", "output": "Strong performance"}
                ]
            }
        }


class ConversationMessage(BaseModel):
    """Message in a conversation."""
    role: str = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(default=None, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class ConversationHistory(BaseModel):
    """Conversation history for an agent."""
    session_id: str = Field(..., description="Session identifier")
    messages: List[ConversationMessage] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict, description="Session context")

    def add_message(self, role: str, content: str, **kwargs):
        """Add a message to the conversation history."""
        msg = ConversationMessage(role=role, content=content, **kwargs)
        self.messages.append(msg)
        return msg

    def get_recent_messages(self, n: int = 10) -> List[ConversationMessage]:
        """Get the n most recent messages."""
        return self.messages[-n:] if n < len(self.messages) else self.messages
