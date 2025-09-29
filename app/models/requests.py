"""
Request data models
"""
from typing import Optional
from pydantic import BaseModel, Field, validator

class TokenRequest(BaseModel):
    """Token request validation model"""
    room: str = Field(..., min_length=1, max_length=100, description="Room name")
    identity: Optional[str] = Field(None, max_length=100, description="User identity")
    name: Optional[str] = Field(None, max_length=100, description="Display name")
    ttl_minutes: int = Field(60, ge=1, le=1440, description="Token TTL in minutes")
    mic_only: bool = Field(True, description="Limit publishing to microphone only")
    dispatch_agent: bool = Field(False, description="Whether to dispatch agent on join")

    @validator('room')
    def validate_room_name(cls, v):
        """Validate room name format"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Room name must contain only alphanumeric characters, hyphens, and underscores')
        return v

    @validator('identity')
    def validate_identity(cls, v):
        """Validate identity format"""
        if v and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Identity must contain only alphanumeric characters, hyphens, and underscores')
        return v

class DispatchRequest(BaseModel):
    """Agent dispatch request validation model"""
    room: str = Field(..., min_length=1, max_length=100, description="Room name")
    agent_name: Optional[str] = Field(None, max_length=100, description="Agent name override")
    metadata: Optional[str] = Field("{}", description="Agent metadata as JSON string")

    @validator('metadata')
    def validate_metadata_json(cls, v):
        """Validate that metadata is valid JSON"""
        if v:
            try:
                import json
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('Metadata must be valid JSON string')
        return v or "{}"