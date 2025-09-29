"""
FastAPI dependencies
"""
from functools import lru_cache
from app.services.token_service import TokenService
from app.services.agent_service import AgentService
from app.config.settings import get_settings

@lru_cache()
def get_token_service() -> TokenService:
    """Get token service instance"""
    return TokenService()

@lru_cache()
def get_agent_service() -> AgentService:
    """Get agent service instance"""
    return AgentService()