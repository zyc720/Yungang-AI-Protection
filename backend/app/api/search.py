"""Search endpoint — pure document retrieval without LLM generation."""

import logging
from fastapi import APIRouter, Depends
from app.schemas.request import SearchRequest
from app.services.search_service import SearchService
from app.api.dependencies import get_search_service
from app.utils.response_builder import success_response

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"])


@router.post("/search")
async def search(
    request: SearchRequest,
    service: SearchService = Depends(get_search_service),
):
    """Search the knowledge base for relevant dictionary entries.

    Performs hybrid retrieval (BM25 + BGE-M3 vector) to find the
    most relevant document chunks matching the query. No LLM is
    involved in this endpoint.

    Args:
        request: SearchRequest with query and optional top_k.

    Returns:
        UnifiedResponse with SearchResponse as data.
    """
    result = service.search(query=request.query, top_k=request.top_k)
    logger.info("API /search: query='%s', results=%d", request.query, result.total)
    return success_response(data=result.model_dump())
