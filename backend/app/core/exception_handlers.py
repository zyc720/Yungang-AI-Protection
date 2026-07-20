"""
FastAPI exception handlers that convert all exceptions into the unified
response format. No raw Python tracebacks are ever exposed to the frontend.
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException
from app.utils.response_builder import UnifiedResponse

logger = logging.getLogger(__name__)


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    """Handle AppException and its subclasses.

    Returns a user-safe error message with the appropriate HTTP status code.
    Internal details are logged but not exposed to the caller.
    """
    logger.error(
        "AppException: %s | Detail: %s | Path: %s",
        exc.message,
        exc.detail,
        request.url.path,
        exc_info=True,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=UnifiedResponse(
            status=exc.status_code,
            message=exc.message,
            data=None,
        ).model_dump(),
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch-all handler for unexpected exceptions.

    Always returns HTTP 500 with a generic message. The full traceback
    is logged for debugging but never sent to the client.
    """
    logger.exception(
        "Unhandled exception: %s | Path: %s",
        str(exc),
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content=UnifiedResponse(
            status=500,
            message="Internal server error",
            data=None,
        ).model_dump(),
    )
