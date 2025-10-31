# ============================================================================
# File: api/middleware/cors.py
# ============================================================================
"""CORS (Cross-Origin Resource Sharing) configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

logger = structlog.get_logger(__name__)


def setup_cors(app: FastAPI, allowed_origins: list = None):
    """Configure CORS middleware.
    
    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed origins (default: allow all)
    """
    if allowed_origins is None:
        # Development: Allow all origins
        # Production: Specify exact origins
        allowed_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logger.info("cors_middleware_configured", origins=allowed_origins)