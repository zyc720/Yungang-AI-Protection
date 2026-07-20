"""
LLM package — provider abstraction and factory.

Exports:
    LLMClient         — abstract base class
    DeepSeekClient    — DeepSeek API implementation
    VLLMClient        — local vLLM implementation
    create_llm_client — factory that returns the configured LLMClient
"""

from app.llm.base import LLMClient
from app.llm.deepseek_client import DeepSeekClient
from app.llm.vllm_client import VLLMClient


def create_llm_client() -> LLMClient:
    """Factory: return the LLM client configured via LLM_PROVIDER.

    Reads settings to determine which provider to instantiate.
    This is the single place where provider selection happens.

    Returns:
        An LLMClient instance (DeepSeekClient or VLLMClient).

    Raises:
        ConfigurationException: If LLM_PROVIDER is unrecognized, or if
            DeepSeek is selected but no API key is configured.
    """
    from app.config.settings import get_settings
    from app.core.exceptions import ConfigurationException

    settings = get_settings()
    provider = settings.llm_provider.lower()

    if provider == "deepseek":
        if not settings.deepseek_api_key:
            raise ConfigurationException(
                message="DEEPSEEK_API_KEY is required when LLM_PROVIDER=deepseek",
                detail="Set DEEPSEEK_API_KEY in .env or switch LLM_PROVIDER to vllm.",
            )
        return DeepSeekClient()

    if provider == "vllm":
        return VLLMClient()

    raise ConfigurationException(
        message=f"Unknown LLM provider: '{settings.llm_provider}'",
        detail="Set LLM_PROVIDER to 'deepseek' or 'vllm'.",
    )
