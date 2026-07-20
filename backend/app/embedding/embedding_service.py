"""
BGE-M3 embedding service wrapped around sentence-transformers.

BGE-M3 is a multilingual embedding model that supports:
- Dense embeddings (1024 dimensions)
- Sparse lexical embeddings
- Chinese + English text

This is a singleton — loading the model is expensive (~2 GB download
on first use) and should happen only once per process lifetime.
"""

import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Singleton wrapper around the BGE-M3 embedding model.

    Usage:
        service = EmbeddingService()
        embeddings = service.encode_query("云冈石窟的历史")
        doc_embeddings = service.encode_documents(["document text", ...])
    """

    _instance: "EmbeddingService | None" = None

    def __new__(cls) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _initialize(self) -> None:
        """Load the BGE-M3 model on first use (lazy initialization)."""
        if self._initialized:
            return
        settings = get_settings()
        logger.info(
            "Loading BGE-M3 model: %s (device: %s)",
            settings.bge_model_name,
            settings.embedding_device,
        )
        self._model: SentenceTransformer = SentenceTransformer(
            settings.bge_model_name,
            device=settings.embedding_device,
        )
        self._dim: int = settings.embedding_dim
        self._initialized = True
        logger.info("BGE-M3 model loaded successfully (dim=%d)", self._dim)

    def encode(
        self,
        texts: str | list[str],
        normalize: bool = True,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        """Encode text(s) to dense embedding vectors.

        Args:
            texts: Single string or list of strings to encode.
            normalize: If True, L2-normalize output vectors (recommended
                for cosine similarity retrieval).
            show_progress_bar: If True, show tqdm progress bar.

        Returns:
            numpy array of shape (n_texts, embedding_dim).
        """
        self._initialize()
        embeddings = self._model.encode(
            texts,
            normalize_embeddings=normalize,
            show_progress_bar=show_progress_bar,
        )
        return np.array(embeddings)

    def encode_query(self, query: str) -> np.ndarray:
        """Encode a retrieval query with BGE-M3 instruction prefix.

        BGE-M3 benefits from a query-specific instruction prefix that
        signals the model to produce a retrieval-oriented representation.

        Args:
            query: The raw user query string.

        Returns:
            Normalized embedding vector of shape (embedding_dim,).
        """
        self._initialize()
        query_with_instruction = (
            "为这个句子生成表示以用于检索相关文章：" + query
        )
        return self.encode(query_with_instruction, normalize=True)

    def encode_documents(self, documents: list[str]) -> np.ndarray:
        """Encode documents for indexing (no instruction prefix).

        Args:
            documents: List of document text strings to index.

        Returns:
            Normalized embedding vectors of shape (n_docs, embedding_dim).
        """
        return self.encode(documents, normalize=True)

    @property
    def dimension(self) -> int:
        """Return the embedding dimension (1024 for BGE-M3)."""
        self._initialize()
        return self._dim
