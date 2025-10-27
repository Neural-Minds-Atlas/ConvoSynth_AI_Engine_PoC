"""FastAPI dependencies for dependency injection."""

from typing import Optional
from fastapi import Depends, Request
import structlog

from src.rag_anything.client import RAGAnythingClient
from src.orchestration import SequentialWorkflow

logger = structlog.get_logger(__name__)


async def get_rag_client(request: Request) -> Optional[RAGAnythingClient]:
    """Get RAG client from app state.
    
    The RAG client is initialized during app startup and stored in app.state.
    This dependency retrieves it for use in routes.
    
    Args:
        request: FastAPI request object
        
    Returns:
        RAG client instance or None if not initialized
    """
    rag_client = getattr(request.app.state, 'rag_client', None)
    
    if rag_client is None:
        logger.warning("rag_client_not_available_in_state")
        return None
    
    if not rag_client._initialized:
        logger.warning("rag_client_not_initialized")
        return None
    
    return rag_client


async def get_workflow(request: Request) -> Optional[SequentialWorkflow]:
    """Get workflow from app state.
    
    The workflow is initialized during app startup and stored in app.state.
    This dependency retrieves it for use in routes.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Workflow instance or None if not initialized
    """
    workflow = getattr(request.app.state, 'workflow', None)
    
    if workflow is None:
        logger.warning("workflow_not_available_in_state")
    
    return workflow


async def get_rag_and_workflow(request: Request) -> tuple[Optional[RAGAnythingClient], Optional[SequentialWorkflow]]:
    """Get both RAG client and workflow from app state.
    
    Convenience dependency for routes that need both.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Tuple of (rag_client, workflow), either may be None
    """
    rag_client = await get_rag_client(request)
    workflow = await get_workflow(request)
    
    return rag_client, workflow