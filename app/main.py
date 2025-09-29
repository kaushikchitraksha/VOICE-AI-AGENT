"""
FastAPI application factory and configuration
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config.settings import get_settings
from app.config.logging import setup_logging
from app.api.router import api_router
from app.api.middleware import LoggingMiddleware, SecurityHeadersMiddleware
from app.core.exceptions import APIException
from app.models.responses import ErrorResponse
import structlog

# Setup logging
setup_logging()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    settings = get_settings()
    
    # Startup
    logger.info("Starting LESA API server", 
               environment=settings.environment,
               debug=settings.debug)
    
    # Validate required settings
    if not all([
        settings.livekit_ws_url,
        settings.livekit_api_key,
        settings.livekit_api_secret
    ]):
        logger.error("Missing required application configuration")
        raise RuntimeError("Missing required application configuration")
    
    yield
    
    # Shutdown
    logger.info("Shutting down LESA API server")

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="LESA Token & Dispatch API",
        description="API for LESA token generation and agent dispatch",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Add middleware
    setup_middleware(app, settings)
    
    # Add exception handlers
    setup_exception_handlers(app)
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    return app

def setup_middleware(app: FastAPI, settings):
    """Setup application middleware"""
    
    # Security headers middleware (first)
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Request logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Trusted host middleware - use the new method
    trusted_hosts = settings.get_trusted_hosts_list()
    if trusted_hosts != ["*"]:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)
    
    # CORS middleware (last) - use the new method
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins_list(),
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers"""
    
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """Handle custom API exceptions"""
        logger.error("API exception occurred",
                    status_code=exc.status_code,
                    detail=exc.detail,
                    path=request.url.path)
        
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.from_exception(exc).dict()
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions"""
        logger.exception("Unexpected error occurred", path=request.url.path)
        
        settings = get_settings()
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal Server Error",
                detail="An unexpected error occurred" if not settings.debug else str(exc)
            ).dict()
        )

# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    from app.config.settings import get_settings
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level="info",
        reload=settings.debug,
        access_log=True,
    )