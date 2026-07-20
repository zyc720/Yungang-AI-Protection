"""
Milvus connection manager — singleton that abstracts the connection
lifecycle for both development (milvus-lite) and production (standalone).

Supports two modes controlled by the USE_MILVUS_LITE setting:
- Milvus Lite: Embedded, file-based, no external server needed (dev).
- Milvus Standalone: Remote server at MILVUS_HOST:MILVUS_PORT (prod).
"""

import logging
from pymilvus import connections, MilvusClient
from app.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class MilvusConnectionManager:
    """Singleton manager for Milvus connections.

    Usage:
        manager = MilvusConnectionManager()
        client = manager.client  # lazy initialization
        manager.close()  # on shutdown
    """

    _instance: "MilvusConnectionManager | None" = None

    def __new__(cls) -> "MilvusConnectionManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _initialize(self) -> None:
        """Establish the Milvus connection on first access."""
        if self._initialized:
            return
        settings = get_settings()
        self._settings: Settings = settings

        if settings.use_milvus_lite:
            db_path = f"{settings.milvus_db_name}.db"
            logger.info("Using Milvus Lite (embedded mode): %s", db_path)
            self._client: MilvusClient = MilvusClient(db_path)
        else:
            uri = f"http://{settings.milvus_host}:{settings.milvus_port}"
            logger.info(
                "Connecting to Milvus standalone at %s:%d",
                settings.milvus_host,
                settings.milvus_port,
            )
            connections.connect(
                alias="default",
                host=settings.milvus_host,
                port=settings.milvus_port,
                db_name=settings.milvus_db_name,
            )
            self._client = MilvusClient(uri=uri)

        self._initialized = True

    @property
    def client(self) -> MilvusClient:
        """Return the MilvusClient instance, initializing on first access."""
        self._initialize()
        return self._client

    def close(self) -> None:
        """Close the Milvus connection gracefully."""
        if not self._initialized:
            return
        try:
            if not self._settings.use_milvus_lite:
                connections.disconnect("default")
            self._initialized = False
            logger.info("Milvus connection closed")
        except Exception:
            logger.warning("Error closing Milvus connection", exc_info=True)

    def health_check(self) -> bool:
        """Check whether Milvus is reachable and operational.

        Returns:
            True if Milvus is healthy, False otherwise.
        """
        try:
            self._initialize()
            if self._settings.use_milvus_lite:
                # Milvus Lite is always healthy if the file is accessible
                return True
            # For standalone, verify connectivity by listing collections
            self._client.list_collections()
            return True
        except Exception:
            logger.warning("Milvus health check failed", exc_info=True)
            return False
