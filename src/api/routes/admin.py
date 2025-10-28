# ============================================================================
# File: api/routes/admin.py
# ============================================================================
"""Admin and monitoring endpoints."""

from typing import Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
import structlog

from src.api.dependencies import get_rag_client
from src.rag_anything.client import RAGAnythingClient
from src.rag_anything.storage import LightRAGManager
from src.rag_anything.config import RAGConfig

logger = structlog.get_logger(__name__)

router = APIRouter()


class StorageStatsResponse(BaseModel):
    """Storage statistics response."""
    exists: bool
    directory: str
    files: list
    total_size: int


class StorageClearResponse(BaseModel):
    """Storage clear response."""
    cleared: bool
    message: str


class SystemStatsResponse(BaseModel):
    """System statistics response."""
    rag_initialized: bool
    storage_stats: Dict[str, Any]
    uploaded_documents: int
    config: Dict[str, Any]


@router.get("/storage/stats", response_model=StorageStatsResponse)
async def get_storage_stats(
    rag_client: RAGAnythingClient = Depends(get_rag_client)
):
    """Get RAG storage statistics.
    
    Returns information about stored documents, embeddings, and graphs.
    
    Args:
        rag_client: RAG client instance
        
    Returns:
        Storage statistics
    """
    try:
        config = rag_client.config if rag_client else RAGConfig()
        manager = LightRAGManager(config.working_dir)
        
        stats = manager.get_storage_stats()
        
        # Calculate total size
        total_size = sum(f.get("size", 0) for f in stats.get("files", []))
        
        return StorageStatsResponse(
            exists=stats.get("exists", False),
            directory=stats.get("directory", ""),
            files=stats.get("files", []),
            total_size=total_size
        )
    
    except Exception as e:
        logger.error("storage_stats_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get storage stats: {str(e)}"
        )


@router.delete("/storage/clear", response_model=StorageClearResponse)
async def clear_storage(
    rag_client: RAGAnythingClient = Depends(get_rag_client)
):
    """Clear all RAG storage.
    
    WARNING: This deletes all processed documents, embeddings, and knowledge graphs.
    Uploaded documents are not affected.
    
    Args:
        rag_client: RAG client instance
        
    Returns:
        Clear operation result
    """
    try:
        config = rag_client.config if rag_client else RAGConfig()
        manager = LightRAGManager(config.working_dir)
        
        success = await manager.clear_storage()
        
        if success:
            logger.info("storage_cleared_via_admin")
            return StorageClearResponse(
                cleared=True,
                message="RAG storage cleared successfully. You need to re-ingest documents."
            )
        else:
            raise Exception("Storage clear operation failed")
    
    except Exception as e:
        logger.error("storage_clear_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear storage: {str(e)}"
        )


@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    rag_client: RAGAnythingClient = Depends(get_rag_client)
):
    """Get comprehensive system statistics.
    
    Returns:
        System statistics including RAG, storage, and uploads
    """
    try:
        # RAG stats
        rag_stats = rag_client.get_stats() if rag_client else {}
        
        # Storage stats
        config = rag_client.config if rag_client else RAGConfig()
        manager = LightRAGManager(config.working_dir)
        storage_stats = manager.get_storage_stats()
        
        # Upload stats
        upload_dir = Path("data/uploads")
        uploaded_count = len(list(upload_dir.glob("*"))) if upload_dir.exists() else 0
        
        return SystemStatsResponse(
            rag_initialized=rag_stats.get("initialized", False),
            storage_stats=storage_stats,
            uploaded_documents=uploaded_count,
            config={
                "working_dir": str(config.working_dir),
                "embedding_model": config.embedding_model_name,
                "llm_model": config.claude_model,
                "parser": "mineru",
                "multimodal_enabled": True
            }
        )
    
    except Exception as e:
        logger.error("system_stats_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system stats: {str(e)}"
        )


@router.post("/reinitialize")
async def reinitialize_rag(
    rag_client: RAGAnythingClient = Depends(get_rag_client)
):
    """Reinitialize RAG system.
    
    Useful after clearing storage or configuration changes.
    
    Args:
        rag_client: RAG client instance
        
    Returns:
        Reinitialization result
    """
    if not rag_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG client not available"
        )
    
    try:
        await rag_client.initialize()
        
        logger.info("rag_reinitialized_via_admin")
        
        return {
            "reinitialized": True,
            "message": "RAG system reinitialized successfully",
            "stats": rag_client.get_stats()
        }
    
    except Exception as e:
        logger.error("rag_reinitialize_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reinitialize RAG: {str(e)}"
        )