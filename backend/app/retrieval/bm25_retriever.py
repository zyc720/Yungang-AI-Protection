"""
BM25 sparse lexical retriever using jieba tokenization for Chinese text.

Maintains an in-memory corpus index loaded from Milvus. The BM25 index
must be rebuilt after inserting new documents via load_from_milvus().

For very large corpora (>100k chunks), consider an external BM25 service
or sharded in-memory index to keep memory usage bounded.
"""

import logging
import jieba
from rank_bm25 import BM25Okapi
from app.retrieval.base import RetrievalInterface, RetrievalResult, RetrievalResponse
from app.database.milvus_client import MilvusConnectionManager
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class BM25Retriever(RetrievalInterface):
    """BM25 sparse retrieval with jieba Chinese tokenization.

    The corpus is loaded from Milvus into memory. For a dictionary of
    moderate size (tens of thousands of chunks), this is efficient.
    """

    def __init__(self) -> None:
        self._corpus: list[str] = []
        self._documents: list[dict] = []
        self._bm25: BM25Okapi | None = None
        self._initialized: bool = False

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Tokenize Chinese text using jieba.

        Args:
            text: Input text to tokenize.

        Returns:
            List of token strings.
        """
        return list(jieba.cut(text))

    def _build_index(self) -> None:
        """Build the BM25 index from the current corpus."""
        if not self._corpus:
            logger.warning("BM25 corpus is empty, index will be empty")
            self._bm25 = None
        else:
            tokenized_corpus = [self._tokenize(doc) for doc in self._corpus]
            self._bm25 = BM25Okapi(tokenized_corpus)
        self._initialized = True
        logger.info("BM25 index built with %d documents", len(self._corpus))

    def load_from_milvus(self) -> None:
        """Load all documents from Milvus and build the BM25 index.

        This should be called once at startup and after any bulk
        document insertion.
        """
        settings = get_settings()
        client = MilvusConnectionManager().client
        collection_name = settings.milvus_collection_name

        if not client.has_collection(collection_name):
            logger.warning(
                "Collection '%s' not found, BM25 index will be empty",
                collection_name,
            )
            self._build_index()
            return

        # Query all documents — use pagination for very large corpora
        results = client.query(
            collection_name=collection_name,
            filter="id >= 0",
            output_fields=["entry_id", "title", "page", "chunk_id", "content"],
            limit=100000,
        )

        self._corpus = [r["content"] for r in results]
        self._documents = results
        self._build_index()

    def retrieve(self, query: str, top_k: int = 5) -> RetrievalResponse:
        """Retrieve top_k documents using BM25 scoring.

        Args:
            query: The search query.
            top_k: Maximum number of results.

        Returns:
            RetrievalResponse with BM25-ranked results.
        """
        if not self._initialized:
            self.load_from_milvus()

        if self._bm25 is None or not self._corpus:
            return RetrievalResponse(
                results=[], query=query, method=self.method_name, total=0
            )

        tokenized_query = self._tokenize(query)
        scores = self._bm25.get_scores(tokenized_query)

        if len(scores) == 0:
            return RetrievalResponse(
                results=[], query=query, method=self.method_name, total=0
            )

        top_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:top_k]

        results = []
        for idx in top_indices:
            doc = self._documents[idx]
            results.append(
                RetrievalResult(
                    entry_id=doc["entry_id"],
                    title=doc["title"],
                    page=doc.get("page"),
                    chunk_id=doc["chunk_id"],
                    content=doc["content"],
                    score=float(scores[idx]),
                    retrieval_method=self.method_name,
                )
            )

        return RetrievalResponse(
            results=results,
            query=query,
            method=self.method_name,
            total=len(results),
        )

    def add_documents(self, documents: list[dict]) -> None:
        """Add documents to the in-memory corpus and rebuild the BM25 index.

        Args:
            documents: List of dicts with entry_id, title, page, chunk_id, content.
        """
        self._documents.extend(documents)
        self._corpus.extend([d["content"] for d in documents])
        self._build_index()

    @property
    def method_name(self) -> str:
        return "bm25"
