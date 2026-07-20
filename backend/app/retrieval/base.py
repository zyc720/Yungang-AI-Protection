"""
Abstract base class and data classes for the retrieval layer.

All retrievers must implement RetrievalInterface — this is the unified
interface required by CLAUDE.md section 17. Business logic must never
call Milvus directly; it goes through a RetrievalInterface implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class RetrievalResult:
    """A single document retrieved from the knowledge base.

    Attributes:
        entry_id: Dictionary entry identifier.
        title: Entry title (e.g., grotto name).
        page: Page number in the dictionary (may be None).
        chunk_id: Unique chunk identifier.
        content: The chunk's text content.
        score: Relevance score (semantics depend on retrieval method).
        retrieval_method: Which method produced this result
            ("bm25", "vector", "hybrid_rrf", "hybrid_weighted").
    """

    entry_id: str
    title: str
    page: int | None
    chunk_id: str
    content: str
    score: float
    retrieval_method: str


@dataclass
class RetrievalResponse:
    """A collection of retrieval results for a single query.

    Attributes:
        results: Ordered list of results (best first).
        query: The original query string.
        method: Name of the retrieval method used.
        total: Number of results returned.
    """

    results: list[RetrievalResult]
    query: str
    method: str
    total: int


class RetrievalInterface(ABC):
    """Unified interface for all retrieval strategies.

    Every retriever (BM25, vector, hybrid) must implement this interface.
    This ensures retrievers are swappable and the business layer is not
    coupled to any specific retrieval implementation.
    """

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> RetrievalResponse:
        """Retrieve the top_k most relevant documents for the query.

        Args:
            query: The search query string.
            top_k: Maximum number of results to return.

        Returns:
            RetrievalResponse with ranked results.
        """
        ...

    @abstractmethod
    def add_documents(self, documents: list[dict]) -> None:
        """Add documents to the retriever's index.

        Args:
            documents: List of dicts with keys matching the knowledge
                chunk schema (entry_id, title, page, chunk_id, content).
        """
        ...

    @property
    @abstractmethod
    def method_name(self) -> str:
        """Human-readable name of this retrieval method."""
        ...
