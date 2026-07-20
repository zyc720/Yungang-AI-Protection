"""
Dense vector retriever using BGE-M3 embeddings and Milvus ANN search.

Encodes the query with BGE-M3, then performs approximate nearest neighbor
(ANN) search in Milvus using cosine similarity.
"""

import logging
from app.retrieval.base import RetrievalInterface, RetrievalResult, RetrievalResponse
from app.embedding.embedding_service import EmbeddingService
from app.database.milvus_client import MilvusConnectionManager
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class VectorRetriever(RetrievalInterface):
    """Dense vector retrieval with BGE-M3 + Milvus ANN search."""

    def __init__(self) -> None:
        self._embedding_service = EmbeddingService()
        self._milvus = MilvusConnectionManager()

    def retrieve(self, query: str, top_k: int = 5) -> RetrievalResponse:
        """Retrieve top_k documents via vector similarity search.

        Args:
            query: The search query.
            top_k: Maximum number of results.

        Returns:
            RetrievalResponse with vector-search-ranked results.
        """
        settings = get_settings()

        # Encode the query
        query_embedding = self._embedding_service.encode_query(query)
        query_vector = query_embedding.tolist()

        collection_name = settings.milvus_collection_name
        if not self._milvus.client.has_collection(collection_name):
            logger.warning(
                "Collection '%s' not found, returning empty results",
                collection_name,
            )
            return RetrievalResponse(
                results=[], query=query, method=self.method_name, total=0
            )

        # ANN search in Milvus
        search_results = self._milvus.client.search(
            collection_name=collection_name,
            data=[query_vector],
            limit=top_k,
            output_fields=["entry_id", "title", "page", "chunk_id", "content"],
        )

        results = []
        for hits in search_results:
            for hit in hits:
                results.append(
                    RetrievalResult(
                        entry_id=hit["entity"]["entry_id"],
                        title=hit["entity"]["title"],
                        page=hit["entity"].get("page"),
                        chunk_id=hit["entity"]["chunk_id"],
                        content=hit["entity"]["content"],
                        score=float(hit["distance"]),
                        retrieval_method=self.method_name,
                    )
                )

        logger.info(
            "Vector retrieval: query='%s', found %d results",
            query,
            len(results),
        )
        return RetrievalResponse(
            results=results,
            query=query,
            method=self.method_name,
            total=len(results),
        )

    def add_documents(self, documents: list[dict]) -> None:
        """Insert documents into Milvus with their BGE-M3 embeddings.

        Args:
            documents: List of dicts with entry_id, title, page, chunk_id, content.
        """
        settings = get_settings()

        # Generate embeddings for all new documents
        contents = [d["content"] for d in documents]
        embeddings = self._embedding_service.encode_documents(contents)

        data = []
        for i, doc in enumerate(documents):
            data.append({
                "entry_id": doc["entry_id"],
                "title": doc["title"],
                "page": doc.get("page", 0),
                "chunk_id": doc["chunk_id"],
                "content": doc["content"],
                "embedding": embeddings[i].tolist(),
            })

        self._milvus.client.insert(
            collection_name=settings.milvus_collection_name,
            data=data,
        )
        logger.info("Inserted %d documents into Milvus", len(data))

    @property
    def method_name(self) -> str:
        return "vector"
