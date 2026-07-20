"""
DeepSeek API client using the OpenAI-compatible SDK.

DeepSeek's API is compatible with the OpenAI SDK — we configure a
different base_url and api_key. The client is a singleton for
connection reuse across requests.

Implements the LLMClient abstract interface for provider-agnostic usage.
"""

import logging
from openai import OpenAI
from app.config.settings import get_settings
from app.llm.base import LLMClient

logger = logging.getLogger(__name__)


class DeepSeekClient(LLMClient):
    """Client for the DeepSeek API via OpenAI-compatible SDK.

    Usage:
        client = DeepSeekClient()
        answer = client.chat([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Yungang Grottoes?"},
        ])
    """

    _instance: "DeepSeekClient | None" = None

    def __new__(cls) -> "DeepSeekClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the OpenAI SDK client on first use."""
        if self._initialized:
            return
        settings = get_settings()
        self._client: OpenAI = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        self._model: str = settings.deepseek_model
        self._initialized = True
        logger.info(
            "DeepSeek client initialized (model=%s, base_url=%s)",
            self._model,
            settings.deepseek_base_url,
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        """Send a chat completion request to DeepSeek.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts.
            temperature: Low temperature for factual accuracy (default 0.1).
            max_tokens: Maximum response length in tokens.

        Returns:
            The LLM's response text.

        Raises:
            LLMException: On any API error (network, auth, rate limit, etc.).
        """
        self._initialize()
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )
            content = response.choices[0].message.content
            logger.debug("DeepSeek response length: %d chars", len(content) if content else 0)
            return content if content else ""
        except Exception as e:
            from app.core.exceptions import LLMException
            logger.error("DeepSeek API error: %s", str(e))
            raise LLMException(
                message="Failed to get response from LLM service",
                detail=str(e),
            ) from e
