"""
Custom application exceptions
"""
import datetime as dt
from typing import Optional, Any, Dict

class APIException(Exception):
    """Base API exception class"""
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = dt.datetime.utcnow()
        super().__init__(self.detail)

class ValidationError(APIException):
    """Validation error exception"""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(
            detail=detail,
            status_code=400,
            error_code="VALIDATION_ERROR",
            context={"field": field} if field else {}
        )

class TokenGenerationError(APIException):
    """Token generation error exception"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=400,
            error_code="TOKEN_GENERATION_ERROR"
        )

class AgentDispatchError(APIException):
    """Agent dispatch error exception"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=500,
            error_code="AGENT_DISPATCH_ERROR"
        )

class ConfigurationError(APIException):
    """Configuration error exception"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=500,
            error_code="CONFIGURATION_ERROR"
        )