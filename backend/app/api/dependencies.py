"""
FastAPI dependency injection providers.

Module-level singletons are lazily created and reused across requests.
This avoids creating new retriever/LLM instances on every API call.

The LLM client is selected based on the LLM_PROVIDER setting:
- "vllm"  -> VLLMClient (local deployment)
- "deepseek" -> DeepSeekClient (cloud API)
"""

import logging
from app.config.settings import get_settings
from app.llm.base import LLMClient
from app.services.search_service import SearchService
from app.retrieval.hybrid_retriever import HybridRetriever

logger = logging.getLogger(__name__)

# Module-level singletons
_search_service: SearchService | None = None
_hybrid_retriever: HybridRetriever | None = None
_llm_client: LLMClient | None = None


def _create_llm_client() -> LLMClient:
    """Create the appropriate LLM client based on configuration.

    Returns:
        LLMClient: The configured LLM client instance (singleton).

    Raises:
        ValueError: If LLM_PROVIDER is set to an unsupported value.
    """
    settings = get_settings()
    provider = settings.llm_provider.lower()

    if provider == "vllm":
        from app.llm.vllm_client import VLLMClient
        logger.info("Creating VLLMClient for local vllm deployment")
        return VLLMClient()
    elif provider == "deepseek":
        from app.llm.deepseek_client import DeepSeekClient
        logger.info("Creating DeepSeekClient for cloud API")
        return DeepSeekClient()
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: '{settings.llm_provider}'. "
            f"Valid options: 'vllm', 'deepseek'"
        )


def get_llm_client() -> LLMClient:
    """FastAPI dependency: provide the singleton LLM client.

    Returns:
        LLMClient: The application-wide LLM client instance.
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = _create_llm_client()
    return _llm_client


def get_search_service() -> SearchService:
    """FastAPI dependency: provide the singleton SearchService.

    Returns:
        SearchService: The application-wide search service instance.
    """
    global _search_service
    if _search_service is None:
        _search_service = SearchService(llm_client=get_llm_client())
    return _search_service


def get_hybrid_retriever() -> HybridRetriever:
    """FastAPI dependency: provide the singleton HybridRetriever.

    Returns:
        HybridRetriever: The application-wide hybrid retriever instance.
    """
    global _hybrid_retriever
    if _hybrid_retriever is None:
        _hybrid_retriever = HybridRetriever()
    return _hybrid_retriever
