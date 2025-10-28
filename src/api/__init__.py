"""API module for ConvoSynth."""

# ============================================================================
# File: api/__init__.py
# ============================================================================
"""API package initialization."""

from fastapi import APIRouter
from .routes import health, documents, chat, admin

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

__all__ = ["api_router"]