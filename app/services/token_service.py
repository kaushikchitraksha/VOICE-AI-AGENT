"""
Token generation service - Fixed to pass credentials explicitly
"""
import datetime as dt
from typing import Optional
import structlog

from livekit.api import AccessToken, VideoGrants, RoomConfiguration, RoomAgentDispatch

from app.config.settings import get_settings
from app.models.requests import TokenRequest
from app.models.responses import TokenResponse
from app.core.exceptions import TokenGenerationError

logger = structlog.get_logger()

class TokenService:
    """Service for generating LiveKit access tokens"""
    
    def __init__(self):
        self.settings = get_settings()
    
    async def generate_token(self, request: TokenRequest) -> TokenResponse:
        """
        Generate a LiveKit access token with specified permissions
        
        Args:
            request: Token request parameters
            
        Returns:
            TokenResponse with generated token and metadata
            
        Raises:
            TokenGenerationError: If token generation fails
        """
        
        try:
            # Validate TTL
            if request.ttl_minutes > self.settings.max_token_ttl_minutes:
                raise TokenGenerationError(
                    f"TTL exceeds maximum allowed: {self.settings.max_token_ttl_minutes} minutes"
                )
            
            # Create video grants
            grants = VideoGrants(
                room_join=True,
                room=request.room,
                can_publish=True,
                can_subscribe=True
            )
            
            # Restrict publishing sources if mic_only is enabled
            if request.mic_only:
                grants.can_publish_sources = ["microphone"]

            # Build access token - PASS CREDENTIALS EXPLICITLY
            token_builder = (
                AccessToken(
                    api_key=self.settings.livekit_api_key,
                    api_secret=self.settings.livekit_api_secret
                )
                .with_identity(request.identity)
                .with_name(request.name or request.identity)
                .with_grants(grants)
                .with_ttl(dt.timedelta(minutes=request.ttl_minutes))
            )

            # Add room configuration with agent dispatch if requested
            if request.dispatch_agent:
                room_config = RoomConfiguration(
                    agents=[RoomAgentDispatch(
                        agent_name=self.settings.agent_name,
                        metadata=self._build_agent_metadata()
                    )]
                )
                token_builder = token_builder.with_room_config(room_config)

            # Generate JWT token
            jwt_token = token_builder.to_jwt()
            
            logger.info("Token generated",
                       room=request.room,
                       identity=request.identity,
                       ttl_minutes=request.ttl_minutes)
            
            return TokenResponse(
                token=jwt_token,
                ws_url=self.settings.livekit_ws_url,
                room=request.room,
                identity=request.identity,
                ttl_minutes=request.ttl_minutes,
                expires_at=dt.datetime.utcnow() + dt.timedelta(minutes=request.ttl_minutes)
            )
            
        except Exception as e:
            logger.exception("Token generation failed", request=request.dict())
            if isinstance(e, TokenGenerationError):
                raise
            raise TokenGenerationError(f"Failed to generate token: {str(e)}")
    
    def _build_agent_metadata(self) -> str:
        """Build metadata for agent dispatch"""
        return f'{{"source":"api","timestamp":"{dt.datetime.utcnow().isoformat()}","environment":"{self.settings.environment}"}}'
    
    async def validate_token_request(self, request: TokenRequest) -> None:
        """
        Validate token request parameters
        
        Args:
            request: Token request to validate
            
        Raises:
            TokenGenerationError: If validation fails
        """
        
        # Room name validation
        if len(request.room) > self.settings.max_room_name_length:
            raise TokenGenerationError(
                f"Room name exceeds maximum length: {self.settings.max_room_name_length}"
            )
        
        # Identity validation
        if request.identity and len(request.identity) > self.settings.max_identity_length:
            raise TokenGenerationError(
                f"Identity exceeds maximum length: {self.settings.max_identity_length}"
            )
        
        # TTL validation
        if request.ttl_minutes < 1:
            raise TokenGenerationError("TTL must be at least 1 minute")
        
        if request.ttl_minutes > self.settings.max_token_ttl_minutes:
            raise TokenGenerationError(
                f"TTL exceeds maximum allowed: {self.settings.max_token_ttl_minutes} minutes"
            )