# ============================================================================
# File: api/middleware/auth.py
# ============================================================================
"""Authentication middleware."""

from typing import Optional
from fastapi import FastAPI, Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Simple API key authentication middleware.
    
    For production, use JWT tokens or OAuth2.
    """
    
    def __init__(self, app, api_key: Optional[str] = None):
        """Initialize auth middleware.
        
        Args:
            app: FastAPI app
            api_key: Required API key (if None, auth is disabled)
        """
        super().__init__(app)
        self.api_key = api_key
        self.enabled = api_key is not None
    
    async def dispatch(self, request: Request, call_next):
        """Check authentication before processing request.
        
        Args:
            request: Incoming request
            call_next: Next handler
            
        Returns:
            Response or auth error
        """
        # Skip auth if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Skip auth for public endpoints
        public_paths = ["/health", "/docs", "/redoc", "/openapi.json"]
        if request.url.path in public_paths:
            return await call_next(request)
        
        # Check for API key in header
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            logger.warning("auth_failed_missing_key", path=request.url.path)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required. Provide X-API-Key header."
            )
        
        if api_key != self.api_key:
            logger.warning(
                "auth_failed_invalid_key",
                path=request.url.path,
                client_ip=request.client.host if request.client else "unknown"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # Authentication successful
        return await call_next(request)


def setup_auth_middleware(app: FastAPI, api_key: Optional[str] = None):
    """Add authentication middleware.
    
    Args:
        app: FastAPI application instance
        api_key: Required API key (None to disable auth)
    """
    app.add_middleware(AuthMiddleware, api_key=api_key)
    
    if api_key:
        logger.info("auth_middleware_configured", enabled=True)
    else:
        logger.info("auth_middleware_configured", enabled=False)