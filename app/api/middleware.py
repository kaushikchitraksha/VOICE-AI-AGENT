"""
Custom middleware for the application
"""
import time
import uuid
from typing import Callable
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info("Request started",
                   request_id=request_id,
                   method=request.method,
                   url=str(request.url),
                   client_ip=request.client.host if request.client else None)
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info("Request completed",
                   request_id=request_id,
                   status_code=response.status_code,
                   duration_ms=round(duration * 1000, 2))
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response