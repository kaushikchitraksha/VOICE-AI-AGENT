"""
Authentication and token management endpoints
"""
import secrets
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status, Depends
import structlog

from app.models.requests import TokenRequest
from app.models.responses import TokenResponse
from app.services.token_service import TokenService
from app.core.exceptions import TokenGenerationError
from app.api.dependencies import get_token_service

logger = structlog.get_logger()
router = APIRouter()

@router.get("/token", response_model=TokenResponse)
async def get_token(
    room: str = Query(..., min_length=1, max_length=100, description="Room name"),
    identity: Optional[str] = Query(None, max_length=100, description="User identity"),
    name: Optional[str] = Query(None, max_length=100, description="Display name"),
    ttl_minutes: int = Query(60, ge=1, le=1440, description="Token TTL in minutes"),
    mic_only: bool = Query(True, description="Limit publishing to microphone only"),
    dispatch_agent: bool = Query(False, description="Whether to dispatch agent on join"),
    token_service: TokenService = Depends(get_token_service)
):
    """
    Generate a LiveKit access token for joining a room.
    
    This endpoint creates a JWT token that allows a client to join a LiveKit room
    with specified permissions and optional agent dispatch.
    """
    
    try:
        # Generate identity if not provided
        if not identity:
            identity = f"guest-{secrets.token_urlsafe(8)}"

        # Create token request
        token_request = TokenRequest(
            room=room,
            identity=identity,
            name=name,
            ttl_minutes=ttl_minutes,
            mic_only=mic_only,
            dispatch_agent=dispatch_agent
        )

        # Generate token
        token_response = await token_service.generate_token(token_request)
        
        logger.info("Token generated successfully",
                   room=room,
                   identity=identity,
                   ttl_minutes=ttl_minutes,
                   dispatch_agent=dispatch_agent)
        
        return token_response
        
    except TokenGenerationError as e:
        logger.warning("Token generation validation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Token generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate token"
        )

@router.post("/token", response_model=TokenResponse)
async def create_token(
    request: TokenRequest,
    token_service: TokenService = Depends(get_token_service)
):
    """
    Generate a Room access token using POST request body.
    
    Alternative endpoint that accepts token parameters in the request body
    instead of query parameters.
    """
    
    try:
        # Generate identity if not provided
        if not request.identity:
            request.identity = f"guest-{secrets.token_urlsafe(8)}"

        # Generate token
        token_response = await token_service.generate_token(request)
        
        logger.info("Token generated successfully",
                   room=request.room,
                   identity=request.identity,
                   ttl_minutes=request.ttl_minutes,
                   dispatch_agent=request.dispatch_agent)
        
        return token_response
        
    except TokenGenerationError as e:
        logger.warning("Token generation validation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Token generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate token"
        )