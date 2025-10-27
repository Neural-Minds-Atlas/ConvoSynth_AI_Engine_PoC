# ============================================================================
# File: api/middleware/rate_limit.py
# ============================================================================
"""Rate limiting middleware."""

import time
from typing import Dict
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware.
    
    For production, use Redis-based rate limiting.
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        """Initialize rate limiter.
        
        Args:
            app: FastAPI app
            requests_per_minute: Max requests per minute per IP
            requests_per_hour: Max requests per hour per IP
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # Store request timestamps per IP
        # Format: {ip: [timestamp1, timestamp2, ...]}
        self.request_history: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limits before processing request.
        
        Args:
            request: Incoming request
            call_next: Next handler
            
        Returns:
            Response or rate limit error
        """
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health"]:
            return await call_next(request)
        
        # Current timestamp
        now = time.time()
        
        # Clean old requests (older than 1 hour)
        self.request_history[client_ip] = [
            ts for ts in self.request_history[client_ip]
            if now - ts < 3600  # 1 hour
        ]
        
        # Check rate limits
        recent_requests = [
            ts for ts in self.request_history[client_ip]
            if now - ts < 60  # Last minute
        ]
        
        hourly_requests = self.request_history[client_ip]
        
        # Check minute limit
        if len(recent_requests) >= self.requests_per_minute:
            logger.warning(
                "rate_limit_exceeded_minute",
                client_ip=client_ip,
                requests=len(recent_requests)
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
            )
        
        # Check hour limit
        if len(hourly_requests) >= self.requests_per_hour:
            logger.warning(
                "rate_limit_exceeded_hour",
                client_ip=client_ip,
                requests=len(hourly_requests)
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.requests_per_hour} requests per hour"
            )
        
        # Record this request
        self.request_history[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            self.requests_per_minute - len(recent_requests) - 1
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            self.requests_per_hour - len(hourly_requests) - 1
        )
        
        return response


def setup_rate_limiting(
    app: FastAPI,
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000
):
    """Add rate limiting middleware.
    
    Args:
        app: FastAPI application instance
        requests_per_minute: Max requests per minute per IP
        requests_per_hour: Max requests per hour per IP
    """
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=requests_per_minute,
        requests_per_hour=requests_per_hour
    )
    
    logger.info(
        "rate_limit_middleware_configured",
        per_minute=requests_per_minute,
        per_hour=requests_per_hour
    )