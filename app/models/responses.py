"""
Response data models
"""
import datetime as dt
from typing import Optional
from pydantic import BaseModel, Field

class TokenResponse(BaseModel):
    """Token response model"""
    token: str = Field(..., description="JWT access token")
    ws_url: str = Field(..., description="WebSocket URL for LiveKit")
    room: str = Field(..., description="Room name")
    identity: str = Field(..., description="User identity")
    ttl_minutes: int = Field(..., description="Token TTL in minutes")
    expires_at: dt.datetime = Field(..., description="Token expiration timestamp")

class DispatchResponse(BaseModel):
    """Dispatch response model"""
    dispatch_id: str = Field(..., description="Unique dispatch identifier")
    room: str = Field(..., description="Room name")
    agent_name: str = Field(..., description="Agent name")
    note: Optional[str] = Field(None, description="Additional notes")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    ws_url: str = Field(..., description="WebSocket URL")
    agent_name: str = Field(..., description="Default agent name")
    environment: str = Field(..., description="Current environment")
    timestamp: str = Field(..., description="Response timestamp")
    version: str = Field(..., description="API version")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    timestamp: str = Field(default_factory=lambda: dt.datetime.utcnow().isoformat())
    error_code: Optional[str] = Field(None, description="Specific error code")
    request_id: Optional[str] = Field(None, description="Request correlation ID")

    @classmethod
    def from_exception(cls, exc: Exception, request_id: Optional[str] = None) -> "ErrorResponse":
        """Create error response from exception"""
        from app.core.exceptions import APIException
        
        if isinstance(exc, APIException):
            return cls(
                error=exc.error_code or "API_ERROR",
                detail=exc.detail,
                error_code=exc.error_code,
                request_id=request_id
            )
        
        return cls(
            error="INTERNAL_ERROR",
            detail=str(exc),
            request_id=request_id
        )