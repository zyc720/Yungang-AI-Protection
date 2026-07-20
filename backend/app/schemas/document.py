"""Pydantic schemas for knowledge base documents and chunks."""

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """A single chunk of a dictionary entry.

    Each chunk is the atomic unit of retrieval. Long entries are split
    into multiple chunks, each with its own embedding.
    """

    entry_id: str = Field(..., description="Unique identifier of the dictionary entry")
    title: str = Field(..., description="Entry title (e.g., a grotto name)")
    page: int | None = Field(default=None, description="Page number in the dictionary")
    chunk_id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., description="Chunk text content")
    embedding: list[float] | None = Field(
        default=None,
        description="Dense vector embedding (not returned in API responses)",
    )


class KnowledgeEntry(BaseModel):
    """A complete dictionary entry with all its chunks."""

    entry_id: str = Field(..., description="Unique identifier of the dictionary entry")
    title: str = Field(..., description="Entry title")
    page: int | None = Field(default=None, description="Page number in the dictionary")
    total_chunks: int = Field(default=1, description="Number of chunks this entry is split into")
    chunks: list[DocumentChunk] = Field(
        default_factory=list,
        description="All chunks belonging to this entry",
    )
