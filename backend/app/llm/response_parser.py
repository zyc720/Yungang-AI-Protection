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

# DeepSeek-R1 often wraps section headers in ### markers when formatting
# structured answers. Strip these so the frontend renders clean text.
_H3_LINE_PATTERN = re.compile(r"^\s*###\s+", re.MULTILINE)

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
    # Strip ### markdown headers that LLM may add for section formatting
    llm_response = _strip_markdown_h3(llm_response)

    # Check for "not found" pattern
    is_not_found = any(
        pattern in llm_response for pattern in NOT_FOUND_PATTERNS
    )
    if is_not_found:
        return llm_response, [], "not_found"

    # Extract citations matching:
    #   【来源：词条标题，页码 10】
    #   【来源：词条标题，页码：10】
    #   【来源：词条标题，10】          (LLM may omit "页码")
    #   【来源：词条标题】
    #   【来源：条目A，10；条目B，20】 (LLM may combine entries)
    #
    # Strategy: first find all 【来源：...】 brackets, then parse
    # individual entries inside each bracket (split by ； or ；).
    bracket_pattern = re.compile(r"【来源：(.+?)】")
    entry_pattern = re.compile(
        r"\s*([^，,;；\d]+?)\s*[，,]\s*(?:页码[：:]?\s*)?(\d+)\s*"
    )
    title_only_pattern = re.compile(r"^\s*([^，,;；\d]+?)\s*$")

    cited_sources: list[CitedSource] = []
    seen_titles: set[str] = set()

    for bracket_content in bracket_pattern.findall(llm_response):
        # Split by semicolons (both half-width and full-width)
        parts = re.split(r"[；;]", bracket_content)
        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Try parsing as "title，page" (with or without 页码)
            m = entry_pattern.match(part)
            if m:
                title = m.group(1).strip()
                page_num = int(m.group(2)) if m.group(2) else None
            else:
                # Try parsing as title-only
                m = title_only_pattern.match(part)
                if m:
                    title = m.group(1).strip()
                    page_num = None
                else:
                    # Fallback: use everything before the last comma/colon
                    # as title, and any trailing digits as page
                    fallback = re.match(
                        r"(.+?)[，,：:\s]*(\d+)?$", part
                    )
                    if fallback:
                        title = fallback.group(1).strip()
                        p = fallback.group(2)
                        page_num = int(p) if p else None
                    else:
                        title = part
                        page_num = None

            if title in seen_titles:
                continue
            seen_titles.add(title)

            # Find the matching document in retrieved_docs.
            excerpt = ""
            actual_page: int | None = page_num
            for doc in retrieved_docs:
                if (
                    title in doc.title
                    or doc.title in title
                    or title == doc.entry_id
                ):
                    excerpt = (
                        doc.content[:200] + "..."
                        if len(doc.content) > 200
                        else doc.content
                    )
                    if actual_page is None and doc.page and doc.page > 0:
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


def _strip_markdown_h3(text: str) -> str:
    """Remove leading ### markers at the start of lines.

    DeepSeek-R1 may wrap section headers like "核心答案", "详细解释",
    and "引用来源" in ### markdown H3 tags. These markers are a formatting
    artifact — strip them so the frontend renders clean, plain text
    without unintended markdown syntax.

    Args:
        text: LLM response possibly containing ###-prefixed lines.

    Returns:
        Text with leading ### removed from all lines.
    """
    stripped = _H3_LINE_PATTERN.sub("", text)
    if stripped != text:
        logger.debug("Stripped ### headers from LLM response")
    return stripped
