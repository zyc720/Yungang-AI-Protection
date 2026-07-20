"""
Unified API response builder.

All API responses must use the standard format:
    {"status": 200, "message": "success", "data": {...}}
"""

from typing import Any
from pydantic import BaseModel


class UnifiedResponse(BaseModel):
    """Standard API response wrapper."""

    status: int = 200
    message: str = "success"
    data: Any = None


def success_response(
    data: Any = None,
    message: str = "success",
) -> UnifiedResponse:
    """Build a successful API response.

    Args:
        data: The response payload.
        message: Human-readable status message.

    Returns:
        UnifiedResponse with status 200.
    """
    return UnifiedResponse(status=200, message=message, data=data)


def error_response(
    status: int,
    message: str,
    data: Any = None,
) -> UnifiedResponse:
    """Build an error API response.

    Args:
        status: HTTP error status code.
        message: Human-readable error message.
        data: Optional error details.

    Returns:
        UnifiedResponse with the given error status.
    """
    return UnifiedResponse(status=status, message=message, data=data)
