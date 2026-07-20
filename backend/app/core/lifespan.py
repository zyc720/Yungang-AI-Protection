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

    # Ensure Milvus collection exists and is loaded into memory.
    # The collection may be in "released" state from a previous session
    # (Milvus Lite does not persist the load state across process restarts).
    try:
        from app.database.collection_setup import ensure_collection_exists

        ensure_collection_exists()
    except Exception:
        logger.warning(
            "Failed to ensure Milvus collection is ready",
            exc_info=True,
        )

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
