"""Health check routes."""
from fastapi import APIRouter, status

from app.db.mongodb import check_connection
from app.config import settings
from app.utils.logger import get_logger

router = APIRouter(tags=["Health"])
logger = get_logger(__name__)


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/health/db", status_code=status.HTTP_200_OK)
async def database_health():
    """Database health check endpoint.

    Returns:
        Database health status
    """
    db_healthy = await check_connection()

    if db_healthy:
        return {
            "status": "healthy",
            "database": "MongoDB",
            "connected": True,
        }
    else:
        return {
            "status": "unhealthy",
            "database": "MongoDB",
            "connected": False,
        }
