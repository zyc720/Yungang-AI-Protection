"""
Logging configuration for the Yungang Dictionary RAG application.

All modules must use the standard `logging` module.
Using `print()` anywhere in the codebase is prohibited.
"""

import logging
import sys


def setup_logging(log_level: str = "INFO") -> None:
    """Configure the root logger with a standard format.

    Args:
        log_level: One of DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
        ),
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("pymilvus").setLevel(logging.WARNING)
