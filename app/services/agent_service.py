"""
Agent dispatch service
"""
import time
from typing import Dict, Tuple
import structlog

from livekit.api import LiveKitAPI, CreateAgentDispatchRequest

from app.config.settings import get_settings
from app.models.requests import DispatchRequest
from app.models.responses import DispatchResponse
from app.core.exceptions import AgentDispatchError

logger = structlog.get_logger()

class DispatchCache:
    """Thread-safe dispatch cache to prevent duplicates"""
    
    def __init__(self, ttl_seconds: int = 3):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[Tuple[str, str], float] = {}
    
    def should_skip(self, room: str, agent: str) -> bool:
        """Check if dispatch should be skipped due to recent duplicate"""
        now = time.time()
        key = (room, agent)
        
        # Clean expired entries
        expired_keys = [k for k, timestamp in self._cache.items() 
                       if now - timestamp > self.ttl_seconds]
        for k in expired_keys:
            self._cache.pop(k, None)
        
        # Check if recent dispatch exists
        if key in self._cache and (now - self._cache[key]) < self.ttl_seconds:
            return True
        
        # Record this dispatch
        self._cache[key] = now
        return False

class AgentService:
    """Service for managing LiveKit agent dispatches"""
    
    def __init__(self):
        self.settings = get_settings()
        self.dispatch_cache = DispatchCache(self.settings.dispatch_cache_ttl_seconds)
    
    async def create_dispatch(self, request: DispatchRequest) -> DispatchResponse:
        """
        Create an agent dispatch request
        
        Args:
            request: Dispatch request parameters
            
        Returns:
            DispatchResponse with dispatch details
            
        Raises:
            AgentDispatchError: If dispatch creation fails
        """
        
        try:
            agent_name = request.agent_name or self.settings.agent_name
            
            # Check for duplicate dispatch
            if self.dispatch_cache.should_skip(request.room, agent_name):
                logger.info("Skipping duplicate dispatch",
                           room=request.room,
                           agent=agent_name)
                return DispatchResponse(
                    dispatch_id="skipped",
                    room=request.room,
                    agent_name=agent_name,
                    note="duplicate-suppressed"
                )
            
            # Create dispatch
            dispatch_id = await self._create_livekit_dispatch(
                room=request.room,
                agent_name=agent_name,
                metadata=request.metadata
            )
            
            logger.info("Agent dispatch created successfully",
                       dispatch_id=dispatch_id,
                       room=request.room,
                       agent=agent_name)
            
            return DispatchResponse(
                dispatch_id=dispatch_id,
                room=request.room,
                agent_name=agent_name
            )
            
        except Exception as e:
            logger.exception("Agent dispatch failed")
            if isinstance(e, AgentDispatchError):
                raise
            raise AgentDispatchError(f"Failed to create agent dispatch: {str(e)}")
    
    async def _create_livekit_dispatch(self, room: str, agent_name: str, metadata: str) -> str:
        """Create LiveKit agent dispatch"""
        
        async with LiveKitAPI() as lk_api:
            request = CreateAgentDispatchRequest(
                agent_name=agent_name,
                room=room,
                metadata=metadata or "{}",
            )
            dispatch = await lk_api.agent_dispatch.create_dispatch(request)
            return dispatch.dispatch_id