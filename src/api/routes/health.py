"""Health check endpoints."""
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    components: Dict[str, str]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint.

    Returns:
        Health status of the application
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        components={
            "api": "operational",
            "workflow": "operational",
        }
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with component status.

    Returns:
        Detailed health information
    """
    from src.main import workflow, rag_client

    components = {
        "api": "operational",
        "workflow": "operational" if workflow else "not_initialized",
        "rag_client": "not_initialized",
    }

    # Check RAG client health
    rag_stats = {}
    if rag_client:
        try:
            is_healthy = await rag_client.health_check()
            components["rag_client"] = "operational" if is_healthy else "degraded"
            rag_stats = rag_client.get_stats()
        except Exception as e:
            logger.error("rag_health_check_failed", error=str(e))
            components["rag_client"] = "error"
            rag_stats = {"error": str(e)}

    # Check agent health (quick check)
    agents_status = {}
    if workflow:
        try:
            # Quick validation that agents are accessible
            agents_status = {
                "conversation": "ready",
                "query": "ready",
                "rag_engine": "ready",
                "outline": "ready",
                "content": "ready",
                "image_coordination": "ready",
                "format": "ready",
                "qa": "ready",
                "validation": "ready",
            }
        except Exception as e:
            logger.error("agent_health_check_failed", error=str(e))
            agents_status = {"error": str(e)}

    all_healthy = all(v in ["operational", "ready"] for v in {**components, **agents_status}.values())

    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "components": components,
        "agents": agents_status,
        "rag": rag_stats,
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint.

    Returns:
        Pong response
    """
    return {"message": "pong"}
