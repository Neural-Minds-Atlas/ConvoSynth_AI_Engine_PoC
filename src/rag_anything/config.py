"""RAG engine configuration."""
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

from src.config.settings import get_settings

settings = get_settings()


class RAGConfig(BaseModel):
    """Configuration for RAG engine with MinerU parser and LightRAG."""

    # Storage
    working_dir: Path = Field(
        default=Path(settings.lightrag_working_dir),
        description="Working directory for RAG storage",
    )

    # API Keys
    openai_api_key: str = Field(
        default=settings.openai_api_key if hasattr(settings, 'openai_api_key') else "",
        description="OpenAI API key for embeddings"
    )
    anthropic_api_key: str = Field(
        default=settings.anthropic_api_key,
        description="Anthropic API key for Claude"
    )
    cohere_api_key: str = Field(
        default=settings.cohere_api_key if hasattr(settings, 'cohere_api_key') else "",
        description="Cohere API key for reasoning model"
    )

    # Embedding Configuration
    embedding_model_name: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model"
    )
    embedding_model: str = Field(
        default=settings.lightrag_embedding_model,
        description="Fallback sentence transformer model",
    )
    embedding_dim: int = Field(
        default=1536,
        description="Embedding vector dimension for text-embedding-3-small",
    )

    # LLM Configuration
    claude_model: str = Field(
        default=settings.claude_model,
        description="Claude model for RAG generation"
    )
    llm_model: str = Field(
        default=settings.lightrag_llm_model,
        description="LLM model for knowledge graph extraction",
    )
    llm_max_tokens: int = Field(
        default=settings.lightrag_max_tokens,
        description="Max tokens for LLM responses",
    )
    cohere_model: str = Field(
        default="command-a-03-2025",
        description="Cohere model for knowledge graph extraction and reasoning"
    )

    # Vector Store (Qdrant)
    qdrant_url: str = Field(
        default=settings.qdrant_url,
        description="Qdrant vector database URL",
    )
    qdrant_api_key: Optional[str] = Field(
        default=settings.qdrant_api_key if settings.qdrant_api_key else None,
        description="Qdrant API key for cloud instances",
    )
    qdrant_collection: str = Field(
        default=settings.qdrant_collection_name,
        description="Qdrant collection name",
    )

    # Retrieval Parameters
    top_k_vector: int = Field(
        default=10, 
        description="Number of results from vector search"
    )
    top_k_graph: int = Field(
        default=5, 
        description="Number of results from graph search"
    )
    hybrid_alpha: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Hybrid search weight: 0=graph only, 1=vector only",
    )

    # Document Processing (MinerU Parser)
    enable_ocr: bool = Field(
        default=True, 
        description="Enable OCR for scanned PDFs"
    )
    extract_tables: bool = Field(
        default=True, 
        description="Extract tables from documents"
    )
    extract_images: bool = Field(
        default=True, 
        description="Extract images from documents"
    )
    extract_equations: bool = Field(
        default=True, 
        description="Extract mathematical equations"
    )

    # Domain-Specific Processing
    financial_mode: bool = Field(
        default=True,
        description="Enable financial document processing",
    )
    extract_metrics: bool = Field(
        default=True,
        description="Extract financial metrics (revenue, EBITDA, etc.)",
    )

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True