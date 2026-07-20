"""
vLLM local deployment client using the OpenAI-compatible SDK.

vLLM exposes an OpenAI-compatible API at its /v1 endpoint. This client
uses the same openai.OpenAI SDK as DeepSeekClient, differing only in
base_url and api_key (vllm does not require authentication).

The client is a singleton for connection reuse across requests.

Note: The DeepSeek-R1 distilled model may produce &lt;think&gt;...&lt;/think&gt;
reasoning blocks in its output. These are stripped before returning.
"""

import logging
import re
from openai import OpenAI
from app.llm.base import LLMClient
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

# DeepSeek-R1 distilled models wrap reasoning in <think>...</think> blocks.
# Some output formats may also use HTML-escaped &lt;think&gt; tags.
# We strip these so the answer parser receives clean text.
_THINK_PATTERN = re.compile(
    r"<think>.*?</think>\s*",
    re.DOTALL,
)
_THINK_ESCAPED_PATTERN = re.compile(
    r"&lt;think&gt;.*?&lt;/think&gt;\s*",
    re.DOTALL,
)


class VLLMClient(LLMClient):
    """Client for a locally-deployed vLLM server via OpenAI-compatible API.

    Usage:
        client = VLLMClient()
        answer = client.chat([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Yungang Grottoes?"},
        ])
    """

    _instance: "VLLMClient | None" = None

    def __new__(cls) -> "VLLMClient":
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
            api_key="not-needed",  # vLLM does not require authentication
            base_url=settings.vllm_base_url,
        )
        self._model: str = settings.vllm_model
        self._initialized = True
        logger.info(
            "VLLMClient initialized (model=%s, base_url=%s)",
            self._model,
            settings.vllm_base_url,
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        """Send a chat completion request to the local vLLM server.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts.
            temperature: Low temperature for factual accuracy (default 0.1).
            max_tokens: Maximum response length in tokens.

        Returns:
            The LLM's response text with reasoning blocks stripped.

        Raises:
            LLMException: On any API error (network, connection refused, etc.).
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
            logger.debug(
                "vLLM response length: %d chars",
                len(content) if content else 0,
            )
            if content:
                content = _strip_think(content)
            return content if content else ""
        except Exception as e:
            from app.core.exceptions import LLMException
            logger.error("vLLM API error: %s", str(e))
            raise LLMException(
                message="Failed to get response from LLM service",
                detail=str(e),
            ) from e


def _strip_think(text: str) -> str:
    """Remove <think>...</think> reasoning blocks from model output.

    DeepSeek-R1 family models emit chain-of-thought reasoning wrapped in
    XML <think> tags. The RAG pipeline expects clean answer text, so we
    strip these blocks before returning to the caller.

    Handles both raw <think> tags and HTML-escaped &lt;think&gt; variants.

    Args:
        text: Raw model output possibly containing <think> blocks.

    Returns:
        Cleaned text with all <think> blocks removed.
    """
    stripped = _THINK_PATTERN.sub("", text)
    stripped = _THINK_ESCAPED_PATTERN.sub("", stripped)
    stripped = stripped.strip()
    if stripped != text:
        logger.debug("Stripped <think> block(s) from vLLM response")
    return stripped
