"""Health check endpoint for monitoring and load balancers."""

import logging
from fastapi import APIRouter
from app.utils.response_builder import success_response
from app.database.milvus_client import MilvusConnectionManager
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Check application health status.

    Returns:
        Health status including Milvus connectivity and model info.
    """
    settings = get_settings()
    milvus_ok = MilvusConnectionManager().health_check()

    logger.debug(
        "Health check: milvus=%s",
        "connected" if milvus_ok else "disconnected",
    )
    return success_response(
        data={
            "status": "healthy",
            "version": "0.1.0",
            "milvus": "connected" if milvus_ok else "disconnected",
            "model": settings.bge_model_name,
        }
    )
