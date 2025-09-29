"""
Application configuration and settings - Fixed for Pydantic V2
"""
from functools import lru_cache
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LiveKitSettings(BaseModel):
    """LiveKit specific configuration"""
    ws_url: str = Field(..., description="WebSocket URL for LiveKit")
    api_url: str = Field(..., description="HTTPS URL for LiveKit API")
    api_key: str = Field(..., description="LiveKit API Key")
    api_secret: str = Field(..., description="LiveKit API Secret")

class SecuritySettings(BaseModel):
    """Security related configuration"""
    trusted_hosts: List[str] = Field(default=["*"], description="Trusted host patterns")
    max_token_ttl_minutes: int = Field(default=1440, description="Maximum token TTL in minutes")
    default_token_ttl_minutes: int = Field(default=60, description="Default token TTL in minutes")
    cors_allow_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = Field(default=["*"])
    cors_allow_headers: List[str] = Field(default=["*"])

class CacheSettings(BaseModel):
    """Cache configuration"""
    dispatch_cache_ttl_seconds: int = Field(default=3, description="Dispatch cache TTL")
    max_room_name_length: int = Field(default=100, description="Maximum room name length")
    max_identity_length: int = Field(default=100, description="Maximum identity length")

class Settings(BaseSettings):
    """Main application settings"""
    
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # LiveKit configuration
    livekit_ws_url: str = Field(..., description="LiveKit WebSocket URL")
    livekit_url: str = Field(..., description="LiveKit API URL")
    livekit_api_key: str = Field(..., description="LiveKit API Key")
    livekit_api_secret: str = Field(..., description="LiveKit API Secret")
    
    # Agent configuration
    agent_name: str = Field(default="py-agent", description="Default agent name")
    
    # Security settings - Accept Union to handle both string and list
    trusted_hosts: Union[str, List[str]] = Field(default=["*"])
    max_token_ttl_minutes: int = Field(default=1440, ge=1, le=10080)  # Max 1 week
    default_token_ttl_minutes: int = Field(default=60, ge=1, le=1440)
    
    # CORS settings - Accept Union to handle both string and list
    cors_allow_origins: Union[str, List[str]] = Field(default=["*"])
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = Field(default=["*"])
    cors_allow_headers: List[str] = Field(default=["*"])
    
    # Cache settings
    dispatch_cache_ttl_seconds: int = Field(default=3, ge=1, le=60)
    max_room_name_length: int = Field(default=100, ge=1, le=255)
    max_identity_length: int = Field(default=100, ge=1, le=255)
    
    # Pydantic V2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Ignore extra environment variables
    )

    @field_validator('cors_allow_origins', 'trusted_hosts', mode='before')
    @classmethod
    def parse_list_from_string(cls, v):
        """Parse comma-separated strings into lists, handle special case of '*'"""
        if isinstance(v, str):
            # Handle the special case of "*"
            if v.strip() == "*":
                return ["*"]
            # Handle comma-separated values
            return [item.strip() for item in v.split(',') if item.strip()]
        # If it's already a list, return as-is
        return v

    @field_validator('livekit_ws_url', 'livekit_url', mode='before')
    @classmethod
    def validate_urls(cls, v):
        """Validate LiveKit URLs"""
        if isinstance(v, str) and not v.startswith(('ws://', 'wss://', 'http://', 'https://')):
            raise ValueError("Invalid URL format")
        return v

    def get_trusted_hosts_list(self) -> List[str]:
        """Get trusted hosts as a list"""
        if isinstance(self.trusted_hosts, str):
            return [self.trusted_hosts]
        return self.trusted_hosts

    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        if isinstance(self.cors_allow_origins, str):
            return [self.cors_allow_origins]
        return self.cors_allow_origins

    @property
    def livekit_config(self) -> LiveKitSettings:
        """Get LiveKit configuration"""
        return LiveKitSettings(
            ws_url=self.livekit_ws_url,
            api_url=self.livekit_url,
            api_key=self.livekit_api_key,
            api_secret=self.livekit_api_secret
        )

    @property
    def security_config(self) -> SecuritySettings:
        """Get security configuration"""
        return SecuritySettings(
            trusted_hosts=self.get_trusted_hosts_list(),
            max_token_ttl_minutes=self.max_token_ttl_minutes,
            default_token_ttl_minutes=self.default_token_ttl_minutes,
            cors_allow_origins=self.get_cors_origins_list(),
            cors_allow_credentials=self.cors_allow_credentials,
            cors_allow_methods=self.cors_allow_methods,
            cors_allow_headers=self.cors_allow_headers,
        )

    @property
    def cache_config(self) -> CacheSettings:
        """Get cache configuration"""
        return CacheSettings(
            dispatch_cache_ttl_seconds=self.dispatch_cache_ttl_seconds,
            max_room_name_length=self.max_room_name_length,
            max_identity_length=self.max_identity_length,
        )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()