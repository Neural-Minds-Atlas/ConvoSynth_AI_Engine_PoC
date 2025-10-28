"""RAG query endpoints."""
from typing import Optional, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
import structlog

from src.api.dependencies import get_rag_client
from src.rag_anything.client import RAGAnythingClient

logger = structlog.get_logger(__name__)

router = APIRouter()


class RAGQueryRequest(BaseModel):
    """Request to query RAG system."""
    query: str = Field(..., description="Query text", min_length=1, max_length=500)
    mode: Optional[str] = Field(default="hybrid", description="Query mode: hybrid, local, global, naive")
    top_k: Optional[int] = Field(default=None, ge=1, le=100, description="Number of results")


class RAGQueryResponse(BaseModel):
    """Response from RAG query."""
    query: str
    mode: str
    context: str
    context_length: int
    sources: list
    metadata: Optional[Dict[str, Any]] = None


class RAGStatsResponse(BaseModel):
    """RAG system statistics."""
    initialized: bool
    working_dir: str
    embedding_model: str
    parser: str
    multimodal_enabled: bool


@router.post("/rag/query", response_model=RAGQueryResponse)
async def query_rag(
    req: RAGQueryRequest,
    rag_client: RAGAnythingClient = Depends(get_rag_client)
):
    """Query the RAG system for relevant context.

    Args:
        req: Query request
        rag_client: RAG client instance (injected)

    Returns:
        Retrieved context with sources

    Raises:
        HTTPException: If RAG is not initialized or query fails
    """
    if not rag_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG system not initialized. Please check server logs."
        )

    logger.info(
        "rag_query_requested",
        query_length=len(req.query),
        mode=req.mode,
    )

    try:
        result = await rag_client.query(
            query_text=req.query,
            mode=req.mode,
            top_k=req.top_k
        )

        context = result.get("context", "")

        return RAGQueryResponse(
            query=req.query,
            mode=result.get("mode", req.mode),
            context=context,
            context_length=len(context),
            sources=result.get("sources", []),
            metadata={
                "query_mode": result.get("mode"),
                "top_k": req.top_k,
            }
        )

    except Exception as e:
        logger.error(
            "rag_query_failed",
            error=str(e),
            error_type=type(e).__name__,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query failed: {str(e)}"
        )


@router.get("/rag/stats", response_model=RAGStatsResponse)
async def get_rag_stats(
    rag_client: RAGAnythingClient = Depends(get_rag_client)
):
    """Get RAG system statistics.

    Args:
        rag_client: RAG client instance (injected)

    Returns:
        RAG system statistics

    Raises:
        HTTPException: If RAG is not initialized
    """
    if not rag_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG system not initialized"
        )

    try:
        stats = rag_client.get_stats()
        return RAGStatsResponse(**stats)

    except Exception as e:
        logger.error("rag_stats_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get RAG stats: {str(e)}"
        )


@router.get("/rag/health")
async def check_rag_health(
    rag_client: RAGAnythingClient = Depends(get_rag_client)
):
    """Check RAG system health.

    Args:
        rag_client: RAG client instance (injected)

    Returns:
        Health status
    """
    if not rag_client:
        return {
            "status": "not_initialized",
            "healthy": False,
            "message": "RAG system not initialized"
        }

    try:
        is_healthy = await rag_client.health_check()
        stats = rag_client.get_stats()

        return {
            "status": "operational" if is_healthy else "degraded",
            "healthy": is_healthy,
            "initialized": stats.get("initialized", False),
            "working_dir": stats.get("working_dir"),
            "parser": stats.get("parser"),
        }

    except Exception as e:
        logger.error("rag_health_check_failed", error=str(e))
        return {
            "status": "error",
            "healthy": False,
            "error": str(e)
        }
