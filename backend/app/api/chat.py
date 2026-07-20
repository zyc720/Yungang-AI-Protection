"""Chat endpoint — full RAG pipeline with LLM answer generation."""

import logging
from fastapi import APIRouter, Depends
from app.schemas.request import ChatRequest
from app.services.search_service import SearchService
from app.api.dependencies import get_search_service
from app.utils.response_builder import success_response

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(
    request: ChatRequest,
    service: SearchService = Depends(get_search_service),
):
    """Full RAG chat: retrieve documents and generate an AI answer.

    The pipeline:
    1. Retrieves relevant chunks from the knowledge base
    2. Builds a strict prompt that forbids hallucination
    3. Calls DeepSeek to generate an answer with citations

    The LLM will explicitly state "知识库中未检索到相关信息" if
    no relevant information is found in the knowledge base.

    Args:
        request: ChatRequest with query and optional top_k.

    Returns:
        UnifiedResponse with ChatResponse (answer + cited sources) as data.
    """
    result = service.chat(query=request.query, top_k=request.top_k)
    logger.info(
        "API /chat: query='%s', confidence=%s, sources=%d",
        request.query,
        result.confidence,
        len(result.sources),
    )
    return success_response(data=result.model_dump())
