"""
Main API router that combines all endpoint routers
"""
from fastapi import APIRouter

from app.api.endpoints import auth, agent, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication & Tokens"]
)

api_router.include_router(
    agent.router,
    prefix="/agent",
    tags=["Agent Management"]
)

api_router.include_router(
    health.router,
    tags=["Health & Monitoring"]
)

# Legacy endpoints for backward compatibility
@api_router.get("/status", deprecated=True)
async def legacy_status():
    """Legacy status endpoint - use /health instead"""
    from app.config.settings import get_settings
    settings = get_settings()
    
    return {
        "ws_url": settings.livekit_ws_url,
        "agent_name": settings.agent_name,
        "ok": bool(settings.livekit_ws_url and settings.agent_name),
    }