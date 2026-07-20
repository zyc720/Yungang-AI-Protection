"""
SearchService — the main orchestrator for search and chat operations.

This is the single entry point used by the API layer. It coordinates:
1. Hybrid retrieval (BM25 + BGE-M3 vector)
2. Prompt construction
3. LLM generation
4. Response parsing

Dependencies (retrievers, LLM client) are injected via the constructor,
enabling easy testing with mocks.
"""

import logging
from app.retrieval.base import RetrievalInterface, RetrievalResponse
from app.retrieval.hybrid_retriever import HybridRetriever
from app.llm.base import LLMClient
from app.llm.prompt_builder import build_prompt
from app.llm.response_parser import parse_llm_response
from app.schemas.response import (
    SearchResponse,
    SearchResult,
    ChatResponse,
)

logger = logging.getLogger(__name__)


class SearchService:
    """Orchestrator for RAG search and chat operations.

    This service hides all the complexity of the RAG pipeline behind
    two simple methods: search() for pure retrieval, and chat() for
    the full retrieve-then-generate flow.

    Usage:
        service = SearchService()
        search_result = service.search("云冈石窟", top_k=5)
        chat_result = service.chat("云冈石窟建于哪一年？", top_k=5)
    """

    def __init__(
        self,
        retriever: RetrievalInterface | None = None,
        llm_client: LLMClient | None = None,
    ) -> None:
        """Initialize the search service with optional dependency injection.

        Args:
            retriever: A RetrievalInterface implementation. Defaults to
                HybridRetriever.
            llm_client: An LLMClient implementation. Defaults to None, in
                which case the dependency injection factory is responsible
                for providing the appropriate client.
        """
        self._retriever = retriever or HybridRetriever()
        self._llm_client = llm_client

    def search(self, query: str, top_k: int = 5) -> SearchResponse:
        """Pure document search without LLM generation.

        Retrieves documents from the knowledge base using hybrid retrieval
        and returns them directly as search results.

        Args:
            query: The search query string.
            top_k: Maximum number of results to return.

        Returns:
            SearchResponse with ranked document chunks.
        """
        retrieval_response: RetrievalResponse = self._retriever.retrieve(
            query, top_k=top_k
        )

        results = [
            SearchResult(
                entry_id=r.entry_id,
                title=r.title,
                page=r.page,
                chunk_id=r.chunk_id,
                content=r.content,
                score=r.score,
                retrieval_method=r.retrieval_method,
            )
            for r in retrieval_response.results
        ]

        logger.info(
            "Search completed: query='%s', found %d results (method=%s)",
            query,
            len(results),
            retrieval_response.method,
        )
        return SearchResponse(
            results=results,
            total=len(results),
            query=query,
            retrieval_method=retrieval_response.method,
        )

    def chat(self, query: str, top_k: int = 5) -> ChatResponse:
        """Full RAG pipeline: retrieve documents and generate an answer.

        1. Retrieve documents using hybrid retrieval
        2. Build a constrained prompt from the retrieved documents
        3. Call DeepSeek LLM to generate an answer
        4. Parse citations and determine confidence from the response

        If no documents are retrieved, returns a "not_found" response
        without calling the LLM.

        Args:
            query: The user's question.
            top_k: Number of documents to retrieve for context.

        Returns:
            ChatResponse with LLM-generated answer and cited sources.
        """
        # Step 1: Retrieve
        retrieval_response: RetrievalResponse = self._retriever.retrieve(
            query, top_k=top_k
        )

        if not retrieval_response.results:
            logger.info("Chat: no documents retrieved for query='%s'", query)
            return ChatResponse(
                answer="知识库中未检索到相关信息。",
                sources=[],
                confidence="not_found",
                query=query,
            )

        # Step 2: Build prompt
        messages = build_prompt(query, retrieval_response.results)

        # Step 3: Call LLM
        llm_answer = self._llm_client.chat(messages)

        # Step 4: Parse response for citations and confidence
        answer, sources, confidence = parse_llm_response(
            llm_answer, retrieval_response.results
        )

        logger.info(
            "Chat completed: query='%s', confidence=%s, sources=%d",
            query,
            confidence,
            len(sources),
        )
        return ChatResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            query=query,
        )
