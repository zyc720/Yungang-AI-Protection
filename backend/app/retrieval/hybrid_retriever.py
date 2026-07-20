"""
Hybrid retriever that combines BM25 and BGE-M3 vector retrieval.

This is the primary retriever for the application. It uses:
1. BM25 for sparse lexical matching (jieba tokenization)
2. BGE-M3 for dense semantic matching
3. Reciprocal Rank Fusion (RRF) to combine results

The RRF fusion uses k=60 (classic RRF constant) and is preferred
over weighted fusion because it doesn't require score normalization.
"""

import logging
from app.retrieval.base import RetrievalInterface, RetrievalResponse
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.vector_retriever import VectorRetriever
from app.retrieval.fusion import reciprocal_rank_fusion
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class HybridRetriever(RetrievalInterface):
    """Hybrid retrieval: BM25 + BGE-M3 vector + RRF fusion.

    This is the default retriever used by SearchService. It retrieves
    more candidates than needed (top_k * 2) from each method, then
    fuses them to produce the final top_k results.
    """

    def __init__(self) -> None:
        self._bm25 = BM25Retriever()
        self._vector = VectorRetriever()

    def retrieve(self, query: str, top_k: int = 5) -> RetrievalResponse:
        """Retrieve top_k documents using hybrid BM25 + vector retrieval.

        Retrieves extra candidates from each method (2x top_k, minimum 10)
        for better fusion coverage, then applies RRF to produce the final
        top_k results.

        Args:
            query: The search query.
            top_k: Number of fused results to return.

        Returns:
            RetrievalResponse with RRF-fused results.
        """
        settings = get_settings()

        # Fetch more candidates than needed for richer fusion
        candidate_k = max(top_k * 2, 10)

        bm25_response = self._bm25.retrieve(query, top_k=candidate_k)
        vector_response = self._vector.retrieve(query, top_k=candidate_k)

        logger.info(
            "Hybrid retrieval: BM25=%d results, Vector=%d results, query='%s'",
            bm25_response.total,
            vector_response.total,
            query,
        )

        # RRF fusion
        fused = reciprocal_rank_fusion(
            bm25_response.results,
            vector_response.results,
            top_k=top_k,
        )

        return RetrievalResponse(
            results=fused,
            query=query,
            method=self.method_name,
            total=len(fused),
        )

    def add_documents(self, documents: list[dict]) -> None:
        """Add documents to both BM25 and vector indices.

        Args:
            documents: List of dicts with entry_id, title, page,
                chunk_id, content.
        """
        self._bm25.add_documents(documents)
        self._vector.add_documents(documents)
        logger.info("Added %d documents to hybrid retriever", len(documents))

    def load_from_milvus(self) -> None:
        """Load the BM25 index from Milvus for search readiness."""
        self._bm25.load_from_milvus()

    @property
    def method_name(self) -> str:
        return "hybrid"
