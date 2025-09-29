"""
Agent dispatch endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
import structlog

from app.models.requests import DispatchRequest
from app.models.responses import DispatchResponse
from app.services.agent_service import AgentService
from app.core.exceptions import AgentDispatchError
from app.api.dependencies import get_agent_service

logger = structlog.get_logger()
router = APIRouter()

@router.post("/dispatch", response_model=DispatchResponse)
async def create_dispatch(
    request: DispatchRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Create an agent dispatch request for a LiveKit room.
    
    This endpoint dispatches an AI agent to join a specific room.
    Includes duplicate request detection to prevent multiple dispatches.
    """
    
    try:
        dispatch_response = await agent_service.create_dispatch(request)
        
        logger.info("Agent dispatch requested",
                   room=request.room,
                   agent_name=request.agent_name,
                   dispatch_id=dispatch_response.dispatch_id)
        
        return dispatch_response
        
    except AgentDispatchError as e:
        logger.warning("Agent dispatch validation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Agent dispatch failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create agent dispatch"
        )
