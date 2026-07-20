"""
Response parser for LLM output.

Extracts cited sources, detects "not found" responses, and determines
confidence levels based on citation count and retrieval scores.
"""

import re
import logging
from app.schemas.response import CitedSource
from app.retrieval.base import RetrievalResult

logger = logging.getLogger(__name__)

# Patterns that indicate the knowledge base lacks the answer
NOT_FOUND_PATTERNS = [
    "知识库中未检索到相关信息",
    "未检索到相关信息",
    "无法找到相关信息",
    "参考资料中没有",
    "参考资料为空",
]


def parse_llm_response(
    llm_response: str,
    retrieved_docs: list[RetrievalResult],
) -> tuple[str, list[CitedSource], str]:
    """Parse the LLM response to extract answer, citations, and confidence.

    Args:
        llm_response: The raw text response from DeepSeek.
        retrieved_docs: The documents that were sent as context (used to
            match citations back to retrieved chunks).

    Returns:
        Tuple of (cleaned_answer, list_of_cited_sources, confidence_level)
        where confidence_level is one of: "high", "medium", "low", "not_found".
    """
    # Check for "not found" pattern
    is_not_found = any(
        pattern in llm_response for pattern in NOT_FOUND_PATTERNS
    )
    if is_not_found:
        return llm_response, [], "not_found"

    # Extract citations matching 【来源：词条标题，页码 X】or 【来源：词条标题】
    citation_pattern = r"【来源：(.+?)(?:，页码\s*(\d+))?】"
    matches = re.findall(citation_pattern, llm_response)

    cited_sources: list[CitedSource] = []
    seen_titles: set[str] = set()

    for title, page in matches:
        title = title.strip()
        if title in seen_titles:
            continue
        seen_titles.add(title)

        # Find the matching document in retrieved_docs
        excerpt = ""
        actual_page: int | None = int(page) if page else None
        for doc in retrieved_docs:
            if doc.title == title:
                excerpt = (
                    doc.content[:200] + "..."
                    if len(doc.content) > 200
                    else doc.content
                )
                if actual_page is None:
                    actual_page = doc.page
                break

        cited_sources.append(
            CitedSource(
                entry_id=title,
                title=title,
                page=actual_page,
                excerpt=excerpt,
            )
        )

    # Determine confidence based on citation count and retrieval scores
    avg_score = (
        sum(d.score for d in retrieved_docs) / len(retrieved_docs)
        if retrieved_docs
        else 0
    )

    if len(cited_sources) >= 2 and avg_score > 0.7:
        confidence = "high"
    elif len(cited_sources) >= 1:
        confidence = "medium"
    else:
        confidence = "low"

    logger.debug(
        "Parsed LLM response: citations=%d, confidence=%s",
        len(cited_sources),
        confidence,
    )
    return llm_response, cited_sources, confidence
