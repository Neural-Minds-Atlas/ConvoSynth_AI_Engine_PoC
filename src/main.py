"""ConvoSynth FastAPI Application - Main Entry Point."""
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import structlog
import uvicorn

from src.config.settings import get_settings
from src.orchestration import SequentialWorkflow
from src.rag_anything.client import RAGAnythingClient
from src.api.middleware import (
    setup_cors,
    setup_logging_middleware,
    setup_rate_limiting,
    setup_auth_middleware
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger(__name__)
settings = get_settings()

# Global instances
workflow: SequentialWorkflow = None
rag_client: RAGAnythingClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global workflow, rag_client

    logger.info("convosynth_starting", version="1.0.0")

    # Initialize RAG client
    try:
        rag_client = RAGAnythingClient()
        await rag_client.initialize()
        logger.info("rag_client_initialized")
    except Exception as e:
        logger.warning("rag_client_init_failed", error=str(e))
        rag_client = None

    # Initialize workflow with RAG client
    workflow = SequentialWorkflow(rag_client=rag_client)
    logger.info("workflow_initialized", rag_client_provided=rag_client is not None)

    # Initialize Outline Agent
    try:
        from src.api.routes.outline import initialize_outline_agent
        initialize_outline_agent(
            model_provider="claude",
            model_name="claude-sonnet-4-20250514",
            temperature=0.3,
            max_tokens=8192,  # Increased for longer outlines
            timeout=120,  # Increased timeout to 2 minutes
            max_iterations=15  # Increased max iterations
        )
        logger.info("outline_agent_initialized")
    except Exception as e:
        logger.warning("outline_agent_init_failed", error=str(e))

    # Initialize Content Agent
    try:
        from src.api.routes.content import initialize_content_agent
        initialize_content_agent(rag_client=rag_client)
        logger.info("content_agent_initialized")
    except Exception as e:
        logger.warning("content_agent_init_failed", error=str(e))

    # Initialize MongoDB (from teammate's version)
    if settings.use_mongodb:
        try:
            from src.db import init_db, close_db
            await init_db()
            logger.info("mongodb_initialized")
            app.state.mongodb_enabled = True
        except Exception as e:
            logger.warning("mongodb_init_failed", error=str(e))
            app.state.mongodb_enabled = False
    else:
        logger.info("mongodb_disabled", use_mongodb=settings.use_mongodb)
        app.state.mongodb_enabled = False

    # Set in app state for route access
    app.state.workflow = workflow
    app.state.rag_client = rag_client
    logger.info(
        "app_state_set",
        workflow_set=workflow is not None,
        rag_client_set=rag_client is not None,
        mongodb_enabled=app.state.mongodb_enabled
    )

    yield

    # Cleanup
    logger.info("convosynth_shutting_down")

    # Cleanup MongoDB (from teammate's version)
    if settings.use_mongodb and app.state.mongodb_enabled:
        try:
            from src.db import close_db
            await close_db()
            logger.info("mongodb_closed")
        except Exception as e:
            logger.warning("mongodb_cleanup_failed", error=str(e))


# Create FastAPI app
app = FastAPI(
    title="ConvoSynth API",
    description="Multi-agent RAG system for financial presentation generation and document management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup middleware (order matters!)
# 1. Logging - first to capture all requests
setup_logging_middleware(app)

# 2. CORS - using your existing settings
setup_cors(app, allowed_origins=settings.allowed_origins_list)

# 3. Rate limiting - protect against abuse
setup_rate_limiting(
    app,
    requests_per_minute=getattr(settings, 'rate_limit_per_minute', 60),
    requests_per_hour=getattr(settings, 'rate_limit_per_hour', 1000)
)

# 4. Authentication - optional, set API_KEY in .env to enable
setup_auth_middleware(
    app,
    api_key=getattr(settings, 'api_key', None)
)

# Import and register routes - merged from both versions
from src.api.routes import health, rag, documents, chat, admin, agents, query_agent, document_selection, outline, content

# Register all routes under /api/v1
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(rag.router, prefix="/api/v1", tags=["rag"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(query_agent.router, prefix="/api/v1/agents", tags=["agents"])  # Query Agent routes
app.include_router(document_selection.router, prefix="/api/v1/agents/document-selection")  # Document Selection Agent routes
app.include_router(outline.router, prefix="/api/v1/agents")  # Outline Agent routes
app.include_router(content.router, tags=["content"])  # Content Agent routes (already has /api/v1/content prefix)

# MongoDB routes (from teammate's version - conditionally imported if enabled)
if settings.use_mongodb:
    try:
        from src.api.routes import auth, conversation_mongodb
        app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
        app.include_router(conversation_mongodb.router, prefix="/api/v1", tags=["conversation-mongodb"])
        logger.info("mongodb_routes_registered")
    except Exception as e:
        logger.warning("mongodb_routes_registration_failed", error=str(e))


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "ConvoSynth API",
        "version": "1.0.0",
        "status": "operational",
        "description": "Multi-agent RAG system for financial presentations",
        "features": [
            "Document upload and ingestion (PDF, CSV, XLSX, TXT, DOCX, MD)",
            "Intelligent document querying with RAG",
            "Financial presentation generation",
            "Multi-agent conversational workflow",
            "Multi-format document support",
            "Knowledge graph construction"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/v1/health",
            "upload": "/api/v1/documents/upload",
            "query": "/api/v1/chat/query",
            "agents": {
                "conversation_generate": "/api/v1/agents/conversation-generate",
                "conversation_edit": "/api/v1/agents/conversation-edit",
                "query_agent": "/api/v1/agents/query-agent",
                "document_selection": "/api/v1/agents/document-selection/select-documents",
                "metadata_corpus": "/api/v1/agents/document-selection/metadata/corpus",
                "metadata_search": "/api/v1/agents/document-selection/metadata/search",
                "outline_generate": "/api/v1/agents/outline/generate",
                "outline_edit": "/api/v1/agents/outline/edit",
                "outline_validate": "/api/v1/agents/outline/validate",
                "outline_health": "/api/v1/agents/outline/health",
                "content_generate": "/api/v1/content/generate",
                "content_health": "/api/v1/content/health",
                "content_test": "/api/v1/content/test",
                "generate_presentation": "/api/v1/agents/generate-presentation",
                "agents_info": "/api/v1/agents/info"
            }
        }
    }


@app.get("/api/v1/info")
async def api_info():
    """Get API and system information."""
    return {
        "api_version": "1.0.0",
        "rag_initialized": rag_client is not None and rag_client._initialized,
        "workflow_initialized": workflow is not None,
        "supported_formats": ["PDF", "TXT", "CSV", "XLSX", "DOCX", "MD"],
        "query_modes": ["hybrid", "naive", "local", "global"],
        "rate_limits": {
            "per_minute": getattr(settings, 'rate_limit_per_minute', 60),
            "per_hour": getattr(settings, 'rate_limit_per_hour', 1000)
        },
        "authentication_enabled": getattr(settings, 'api_key', None) is not None
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with detailed logging."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        error_type=type(exc).__name__,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An error occurred",
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    logger.info(
        "starting_convosynth_server",
        host=settings.app_host,
        port=settings.app_port,
        debug=settings.debug
    )
    
    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )