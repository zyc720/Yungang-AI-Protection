"""Pydantic response schemas for API endpoints."""

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """A single document retrieval result."""

    entry_id: str = Field(..., description="Dictionary entry identifier")
    title: str = Field(..., description="Entry title")
    page: int | None = Field(default=None, description="Page number in the dictionary")
    chunk_id: str = Field(..., description="Chunk identifier")
    content: str = Field(..., description="Chunk text content")
    score: float = Field(..., description="Retrieval relevance score")
    retrieval_method: str = Field(
        ...,
        description="Retrieval method: bm25, vector, or hybrid",
    )


class SearchResponse(BaseModel):
    """Response for the /api/search endpoint."""

    results: list[SearchResult] = Field(
        default_factory=list,
        description="Retrieved document chunks",
    )
    total: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original search query")
    retrieval_method: str = Field(
        ...,
        description="Retrieval method used",
    )


class CitedSource(BaseModel):
    """A cited source from the knowledge base."""

    entry_id: str = Field(..., description="Entry identifier")
    title: str = Field(..., description="Entry title")
    page: int | None = Field(default=None, description="Page number")
    excerpt: str = Field(
        default="",
        description="Excerpt of the source text used",
    )


class ChatResponse(BaseModel):
    """Response for the /api/chat endpoint (full RAG pipeline)."""

    answer: str = Field(..., description="LLM-generated answer based on retrieved documents")
    sources: list[CitedSource] = Field(
        default_factory=list,
        description="Cited knowledge base sources",
    )
    confidence: str = Field(
        ...,
        description="Confidence level: high, medium, low, or not_found",
    )
    query: str = Field(..., description="Original user question")
