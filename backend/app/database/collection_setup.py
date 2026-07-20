"""
Milvus collection schema definition and automatic setup.

The collection stores knowledge chunks from 《云冈石窟辞典》with the
following schema:
- id: auto-generated primary key
- entry_id: dictionary entry identifier
- title: entry title
- page: page number in the dictionary
- chunk_id: unique chunk identifier within an entry
- content: text content of the chunk
- embedding: BGE-M3 dense vector (1024-dim, COSINE similarity)
"""

import logging
from app.config.settings import get_settings
from app.database.milvus_client import MilvusConnectionManager

logger = logging.getLogger(__name__)


def ensure_collection_exists() -> None:
    """Create the knowledge chunks collection and index if not present.

    Idempotent: if the collection already exists, this is a no-op.
    After creation, the collection is loaded into memory so it is
    ready for search and query operations.

    Should be called during application startup.
    """
    settings = get_settings()
    collection_name = settings.milvus_collection_name
    embedding_dim = settings.embedding_dim

    client = MilvusConnectionManager().client

    if client.has_collection(collection_name):
        logger.info("Collection '%s' already exists", collection_name)
        # Ensure collection is loaded (may have been released)
        _load_collection_if_needed(client, collection_name)
        return

    client.create_collection(
        collection_name=collection_name,
        dimension=embedding_dim,
        metric_type="COSINE",
        auto_id=True,
    )

    # Load collection into memory for query/search readiness
    client.load_collection(collection_name)

    logger.info(
        "Collection '%s' created and loaded (dim=%d, metric=COSINE)",
        collection_name,
        embedding_dim,
    )


def _load_collection_if_needed(client, collection_name: str) -> None:
    """Load the collection into memory if it's in released state."""
    try:
        # Check if collection needs loading by attempting a lightweight operation
        client.load_collection(collection_name)
        logger.debug("Collection '%s' loaded into memory", collection_name)
    except Exception:
        logger.debug(
            "Collection '%s' load attempted (may already be loaded)",
            collection_name,
        )
