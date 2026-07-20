"""
Custom exception hierarchy for the Yungang Dictionary RAG application.

All application exceptions inherit from AppException, which carries
a user-safe message and an HTTP status code. Internal implementation
details go into the `detail` field and are logged but not exposed to
the frontend. Raw Python tracebacks must never reach API responses.
"""


class AppException(Exception):
    """Base application exception with status code and user-safe message.

    Attributes:
        message: User-facing error message (safe to expose in API response).
        status_code: HTTP status code.
        detail: Internal detail for debugging (logged, not exposed to users).
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: str | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class NotFoundException(AppException):
    """Resource not found (404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        detail: str | None = None,
    ) -> None:
        super().__init__(message, status_code=404, detail=detail)


class RetrievalException(AppException):
    """Retrieval operation failed (500)."""

    def __init__(
        self,
        message: str = "Retrieval failed",
        detail: str | None = None,
    ) -> None:
        super().__init__(message, status_code=500, detail=detail)


class LLMException(AppException):
    """LLM service error (502 Bad Gateway)."""

    def __init__(
        self,
        message: str = "LLM service error",
        detail: str | None = None,
    ) -> None:
        super().__init__(message, status_code=502, detail=detail)


class ValidationException(AppException):
    """Input validation error (422)."""

    def __init__(
        self,
        message: str = "Validation error",
        detail: str | None = None,
    ) -> None:
        super().__init__(message, status_code=422, detail=detail)


class ConfigurationException(AppException):
    """Configuration error (500)."""

    def __init__(
        self,
        message: str = "Configuration error",
        detail: str | None = None,
    ) -> None:
        super().__init__(message, status_code=500, detail=detail)
