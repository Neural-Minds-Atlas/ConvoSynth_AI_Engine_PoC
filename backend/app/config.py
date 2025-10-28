"""Application configuration using Pydantic Settings."""
from typing import List, Optional
from pathlib import Path
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the backend directory path
BACKEND_DIR = Path(__file__).parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="ConvoSynth Backend", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # MongoDB
    mongodb_uri: str = Field(alias="MONGODB_URI")
    mongodb_db_name: str = Field(default="convosynth", alias="MONGODB_DB_NAME")
    mongodb_min_pool_size: int = Field(default=10, alias="MONGODB_MIN_POOL_SIZE")
    mongodb_max_pool_size: int = Field(default=100, alias="MONGODB_MAX_POOL_SIZE")

    # Anthropic Claude
    anthropic_api_key: str = Field(alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-sonnet-4-20250514", alias="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(default=2048, alias="ANTHROPIC_MAX_TOKENS")
    anthropic_temperature: float = Field(default=0.8, alias="ANTHROPIC_TEMPERATURE")
    anthropic_timeout: int = Field(default=30, alias="ANTHROPIC_TIMEOUT")

    # JWT Authentication
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=1440,
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"],
        alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], alias="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], alias="CORS_ALLOW_HEADERS")

    # Conversation Agent
    conversation_agent_max_iterations: int = Field(
        default=6,
        alias="CONVERSATION_AGENT_MAX_ITERATIONS"
    )
    conversation_agent_max_execution_time: int = Field(
        default=30,
        alias="CONVERSATION_AGENT_MAX_EXECUTION_TIME"
    )
    conversation_agent_memory_limit: int = Field(
        default=10,
        alias="CONVERSATION_AGENT_MEMORY_LIMIT"
    )

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.strip("[]").split(",")]
        return v

    @validator("cors_allow_methods", pre=True)
    def parse_cors_methods(cls, v):
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.strip("[]").split(",")]
        return v

    @validator("cors_allow_headers", pre=True)
    def parse_cors_headers(cls, v):
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.strip("[]").split(",")]
        return v

    @property
    def mongodb_url(self) -> str:
        """Get formatted MongoDB URL."""
        return f"{self.mongodb_uri}/{self.mongodb_db_name}"

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()
