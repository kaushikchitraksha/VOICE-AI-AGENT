"""
Health check and monitoring endpoints
"""
import datetime as dt
from fastapi import APIRouter
import structlog

from app.models.responses import HealthResponse
from app.config.settings import get_settings

logger = structlog.get_logger()
router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring and load balancing.
    
    Returns the current status of the service including configuration
    and timestamp information.
    """
    settings = get_settings()
    
    return HealthResponse(
        status="healthy",
        ws_url=settings.livekit_ws_url,
        agent_name=settings.agent_name,
        environment=settings.environment.value,
        timestamp=dt.datetime.utcnow().isoformat(),
        version="1.0.0"
    )

@router.get("/readiness")
async def readiness_check():
    """
    Readiness check for Kubernetes deployments.
    
    Validates that all required configuration is present
    and the service is ready to accept requests.
    """
    settings = get_settings()
    
    # Check required configuration
    required_config = [
        settings.livekit_ws_url,
        settings.livekit_api_key,
        settings.livekit_api_secret
    ]
    
    if not all(required_config):
        logger.error("Service not ready - missing configuration")
        return {"status": "not_ready", "reason": "missing_configuration"}
    
    return {"status": "ready"}

@router.get("/liveness")
async def liveness_check():
    """
    Liveness check for Kubernetes deployments.
    
    Simple endpoint to verify the service is still running
    and responding to requests.
    """
    return {"status": "alive", "timestamp": dt.datetime.utcnow().isoformat()}