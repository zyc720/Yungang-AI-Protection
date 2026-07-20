"""
Abstract base class for LLM clients.

All LLM integrations (DeepSeek API, vllm local deployment, etc.) must
implement this interface. This follows the same pattern as RetrievalInterface
in the retrieval layer, enabling provider-agnostic RAG pipelines.
"""

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract interface for LLM chat completion providers.

    Each concrete implementation handles its own connection lifecycle
    (singleton, connection pool, etc.) and error translation.

    Usage:
        client = VLLMClient()
        answer = client.chat([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Yungang Grottoes?"},
        ])
    """

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        """Send a chat completion request and return the response text.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts in
                OpenAI-compatible format.
            temperature: Sampling temperature (default 0.1 for factual accuracy).
            max_tokens: Maximum response length in tokens.

        Returns:
            The LLM's response text.

        Raises:
            LLMException: On any provider error (network, auth, rate limit, etc.).
        """
        ...
