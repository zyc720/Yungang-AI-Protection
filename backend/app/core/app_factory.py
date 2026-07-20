"""
FastAPI application factory.

Creates and configures the FastAPI application instance with:
- CORS middleware for frontend development
- Unified exception handlers
- API router registration
- Lifespan lifecycle management
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.lifespan import lifespan
from app.core.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
)
from app.core.exceptions import AppException
from app.api.router import api_router
from app.utils.logging_config import setup_logging
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured application instance ready to serve.
    """
    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(
        title="Yungang Grottoes Intelligent E-Dictionary",
        description=(
            "RAG-based intelligent dictionary for Yungang Grottoes "
            "cultural heritage. All knowledge comes from the "
            "《云冈石窟辞典》knowledge base."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — allow frontend dev server origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register exception handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Register API routes
    app.include_router(api_router, prefix="/api")

    logger.info("FastAPI application created successfully")
    return app
