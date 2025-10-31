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
    environment: str = "development"  # Added from backend
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    api_host: str = "0.0.0.0"  # Added from backend (alias for app_host)
    api_port: int = 8000  # Added from backend (alias for app_port)
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

    # Conversation Agent LLM Provider (from backend config)
    conversation_llm_provider: str = "anthropic"  # Options: "anthropic", "openai", "cohere", "mistral"

    # Conversation Agent Configuration (from backend)
    conversation_agent_max_iterations: int = 20
    conversation_agent_max_execution_time: int = 60
    conversation_agent_memory_limit: int = 10

    # CORS Configuration (consolidated from backend)
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

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

    # MongoDB Atlas - ALWAYS ENABLED (consolidated from backend)
    mongodb_uri: str = "mongodb+srv://nakshatramanglik14:naksh1414@conversecluster.worvjwm.mongodb.net/?retryWrites=true&w=majority&appName=ConverseCluster"
    mongodb_db_name: str = "test"  # Using existing 'test' database as requested
    mongodb_min_pool_size: int = 10
    mongodb_max_pool_size: int = 100
    use_mongodb: bool = True  # Always enabled - consolidated architecture

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

    @property
    def mongodb_url(self) -> str:
        """Get formatted MongoDB URL (from backend)."""
        return f"{self.mongodb_uri}/{self.mongodb_db_name}"

    @property
    def is_production(self) -> bool:
        """Check if running in production (from backend)."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development (from backend)."""
        return self.environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
