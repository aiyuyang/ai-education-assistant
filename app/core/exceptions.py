"""
Custom exceptions for the application
"""
from typing import Any, Dict, Optional


class AIEducationAssistantException(Exception):
    """Base exception class"""
    
    def __init__(self, message: str, code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class ValidationError(AIEducationAssistantException):
    """Validation error"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=400, details=details)


class AuthenticationError(AIEducationAssistantException):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=401, details=details)


class AuthorizationError(AIEducationAssistantException):
    """Authorization error"""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=403, details=details)


class NotFoundError(AIEducationAssistantException):
    """Resource not found error"""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=404, details=details)


class ConflictError(AIEducationAssistantException):
    """Conflict error"""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=409, details=details)


class RateLimitError(AIEducationAssistantException):
    """Rate limit error"""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=429, details=details)


class ExternalServiceError(AIEducationAssistantException):
    """External service error"""
    
    def __init__(self, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=502, details=details)


class DatabaseError(AIEducationAssistantException):
    """Database error"""
    
    def __init__(self, message: str = "Database error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=500, details=details)
