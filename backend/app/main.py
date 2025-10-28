"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db import init_db, close_db
from app.api.routes import auth, conversation, health
from app.utils.logger import setup_logging, get_logger
from app.utils.exceptions import ConvoSynthException

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info(
        "application_starting",
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )

    # Initialize database
    await init_db()

    logger.info("application_ready", host=settings.api_host, port=settings.api_port)

    yield

    # Shutdown
    logger.info("application_shutting_down")
    await close_db()
    logger.info("application_shutdown_complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ConvoSynth Backend API - Conversation Agent for Presentation Generation",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Exception handlers
@app.exception_handler(ConvoSynthException)
async def convosynth_exception_handler(request, exc: ConvoSynthException):
    """Handle ConvoSynth custom exceptions.

    Args:
        request: Request object
        exc: ConvoSynth exception

    Returns:
        JSON error response
    """
    logger.error(
        "convosynth_exception",
        exception_type=type(exc).__name__,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": type(exc).__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions.

    Args:
        request: Request object
        exc: Exception

    Returns:
        JSON error response
    """
    logger.error(
        "unhandled_exception",
        exception_type=type(exc).__name__,
        message=str(exc),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": {"error": str(exc)} if settings.debug else {},
        },
    )


# Include routers
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(conversation.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": "Welcome to ConvoSynth Backend API",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
