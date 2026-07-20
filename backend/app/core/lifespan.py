"""
FastAPI lifespan context manager for startup and shutdown events.

Handles initialization and cleanup of singletons:
- Milvus connection
- Embedding model (loaded lazily on first use)
- BM25 index (loaded from Milvus on first retrieval)
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application lifecycle.

    Startup:
        - Log application start
        - (Heavy resources like embedding models are loaded lazily)

    Shutdown:
        - Close Milvus connections
        - Clean up resources
    """
    # Startup
    logger.info("Starting up Yungang Dictionary RAG backend...")
    logger.info("Application is ready to accept requests")

    yield

    # Shutdown
    logger.info("Shutting down Yungang Dictionary RAG backend...")
    try:
        from app.database.milvus_client import MilvusConnectionManager

        MilvusConnectionManager().close()
    except Exception:
        logger.warning("Error closing Milvus connection", exc_info=True)

    logger.info("Shutdown complete")
