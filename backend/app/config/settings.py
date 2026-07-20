"""
Application configuration management using pydantic-settings.

All configuration is read from environment variables or .env file.
Hardcoding of API keys, paths, or tokens is strictly prohibited.
"""

import logging
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from .env and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Provider selection: "deepseek" or "vllm"
    llm_provider: str = Field(
        default="vllm",
        alias="LLM_PROVIDER",
    )

    # DeepSeek API (used when LLM_PROVIDER=deepseek)
    deepseek_api_key: str = Field(
        default="",
        alias="DEEPSEEK_API_KEY",
    )
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com/v1",
        alias="DEEPSEEK_BASE_URL",
    )
    deepseek_model: str = Field(
        default="deepseek-chat",
        alias="DEEPSEEK_MODEL",
    )

    # vLLM local deployment (used when LLM_PROVIDER=vllm)
    vllm_base_url: str = Field(
        default="http://localhost:8002/v1",
        alias="VLLM_BASE_URL",
    )
    vllm_model: str = Field(
        default="casperhansen/deepseek-r1-distill-qwen-32b-awq",
        alias="VLLM_MODEL",
    )

    # Milvus
    milvus_host: str = Field(default="localhost", alias="MILVUS_HOST")
    milvus_port: int = Field(default=19530, alias="MILVUS_PORT")
    milvus_db_name: str = Field(
        default="yungang_dictionary",
        alias="MILVUS_DB_NAME",
    )
    milvus_collection_name: str = Field(
        default="knowledge_chunks",
        alias="MILVUS_COLLECTION_NAME",
    )
    use_milvus_lite: bool = Field(default=True, alias="USE_MILVUS_LITE")

    # BGE-M3 Embedding
    bge_model_name: str = Field(
        default="BAAI/bge-m3",
        alias="BGE_MODEL_NAME",
    )
    embedding_device: str = Field(default="cpu", alias="EMBEDDING_DEVICE")
    embedding_dim: int = Field(default=1024, alias="EMBEDDING_DIM")

    # Application
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Retrieval
    retrieval_top_k: int = Field(default=5, alias="RETRIEVAL_TOP_K")
    bm25_weight: float = Field(default=0.3, alias="BM25_WEIGHT")
    vector_weight: float = Field(default=0.7, alias="VECTOR_WEIGHT")


# Module-level singleton
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the cached Settings singleton, creating it on first call.

    Returns:
        Settings: The application settings instance.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        logger.info("Settings loaded from .env")
    return _settings
