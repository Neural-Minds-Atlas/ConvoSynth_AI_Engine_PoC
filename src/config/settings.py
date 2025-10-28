"""Application settings and configuration."""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    app_name: str = "ConvoSynth"
    app_version: str = "1.0.0"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    api_key: str | None = None
    access_token_expire_minutes: int = 30
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"

    # Claude API
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"
    claude_max_tokens: int = 8192
    claude_temperature: float = 0.7

    # OpenAI (for embeddings)
    openai_api_key: str = ""

    # Cohere (for reasoning and knowledge graph)
    cohere_api_key: str = ""
    cohere_base_url: str = ""

    # Ollama (self-hosted GPU server)
    ollama_base_url: str = ""
    ollama_model: str = "command-r"
    use_ollama: bool = False  # For knowledge graph building during ingestion

    # LM Studio (local OpenAI-compatible server)
    lmstudio_base_url: str = "http://localhost:1234/v1"
    lmstudio_model: str = "local-model"
    lmstudio_api_key: str = "lm-studio"

    # vLLM (high-performance inference server)
    vllm_base_url: str = "http://localhost:8000/v1"
    vllm_model: str = "mistralai/Mistral-7B-Instruct-v0.2"
    vllm_api_key: str = "EMPTY"

    # LLM Enhancement Provider (for RAG query answer generation)
    llm_enhancement_provider: str = "claude"  # Options: "ollama", "claude", "cohere", "lmstudio", "vllm"

    # Nano Banana
    nano_banana_api_key: str = ""
    nano_banana_base_url: str = "https://api.nanobanana.ai/v1"

    # Vector Store (Qdrant)
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection_name: str = "convosynth_embeddings"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_password: str = ""
    redis_ttl: int = 3600

    # LightRAG
    lightrag_working_dir: str = "./data/rag_storage"
    lightrag_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    lightrag_llm_model: str = "claude-sonnet-4-20250514"
    lightrag_max_tokens: int = 32000

    # Performance
    total_latency_target_seconds: int = 20
    conversation_agent_timeout: int = 2
    query_agent_timeout: int = 2
    rag_engine_timeout: int = 3
    outline_agent_timeout: int = 2
    content_agent_timeout: int = 4
    image_coordination_timeout: int = 3
    format_agent_timeout: int = 2
    qa_agent_timeout: int = 1
    validation_engine_timeout: int = 1

    # File Upload
    max_upload_size_mb: int = 50
    allowed_document_types: str = "pdf,docx,xlsx,html,txt,csv,md"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "./logs/application.log"

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # LangSmith
    langchain_tracing_v2: bool = False
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: str = ""
    langchain_project: str = "convosynth-production"

    # MongoDB (NEW - for conversation persistence and user management)
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "convosynth"
    mongodb_min_pool_size: int = 10
    mongodb_max_pool_size: int = 100
    use_mongodb: bool = False  # Set to True to enable MongoDB features

    # JWT Authentication (NEW - for MongoDB auth system)
    jwt_secret_key: str = "your-jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440  # 24 hours

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def allowed_document_types_list(self) -> List[str]:
        """Convert comma-separated document types to list."""
        return [dt.strip() for dt in self.allowed_document_types.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
