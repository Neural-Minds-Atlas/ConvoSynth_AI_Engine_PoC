# ============================================================================
# File: api/middleware/logging.py
# ============================================================================
"""Request logging middleware."""

import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details.
        
        Args:
            request: Incoming request
            call_next: Next middleware/route handler
            
        Returns:
            Response from handler
        """
        # Start timer
        start_time = time.time()
        
        # Extract request details
        request_id = request.headers.get("X-Request-ID", "unknown")
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(
            "http_request_received",
            request_id=request_id,
            method=method,
            path=path,
            client_ip=client_ip
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                "http_request_completed",
                request_id=request_id,
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2)
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(duration * 1000, 2))
            
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                "http_request_failed",
                request_id=request_id,
                method=method,
                path=path,
                error=str(e),
                duration_ms=round(duration * 1000, 2)
            )
            raise


def setup_logging_middleware(app: FastAPI):
    """Add logging middleware to application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(LoggingMiddleware)
    logger.info("logging_middleware_configured")