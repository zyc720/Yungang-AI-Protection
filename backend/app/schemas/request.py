"""Pydantic request schemas for API endpoints."""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request schema for the /api/search endpoint.

    Performs pure document retrieval without LLM generation.
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Search query string",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of results to return",
    )
    use_hybrid: bool = Field(
        default=True,
        description="Use hybrid retrieval (BM25 + vector); false = vector only",
    )


class ChatRequest(BaseModel):
    """Request schema for the /api/chat endpoint.

    Full RAG pipeline: retrieve + LLM generation with citations.
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User question",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of retrieved documents for context",
    )
    conversation_id: str | None = Field(
        default=None,
        description="Optional conversation context identifier for future use",
    )
