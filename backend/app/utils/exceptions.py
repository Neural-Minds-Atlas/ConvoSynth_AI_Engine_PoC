"""Custom exceptions for ConvoSynth backend."""
from typing import Any, Dict, Optional


class ConvoSynthException(Exception):
    """Base exception for all ConvoSynth errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(ConvoSynthException):
    """Database-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class AuthenticationException(ConvoSynthException):
    """Authentication-related errors."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationException(ConvoSynthException):
    """Authorization-related errors."""

    def __init__(self, message: str = "Not authorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class ValidationException(ConvoSynthException):
    """Input validation errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class AgentException(ConvoSynthException):
    """Agent execution errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class NotFoundException(ConvoSynthException):
    """Resource not found errors."""

    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status_code=404, details={"resource": resource, "identifier": identifier})


class RBACException(ConvoSynthException):
    """RBAC validation errors."""

    def __init__(
        self,
        message: str = "Access denied",
        denied_items: Optional[list] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        if denied_items:
            details["denied_items"] = denied_items
        super().__init__(message, status_code=403, details=details)
