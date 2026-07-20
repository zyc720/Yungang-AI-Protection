"""
Prompt builder for the RAG pipeline.

Constructs strictly constrained prompts that enforce:
1. Answer ONLY from provided reference documents
2. Cite specific sources using 【来源：词条标题，页码】format
3. Explicitly state when information is not found
4. No hallucination — no use of model's own knowledge
"""

import logging
from app.retrieval.base import RetrievalResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个专业的云冈石窟知识助手，基于《云冈石窟辞典》的知识为用户提供准确的答案。

## 核心规则（必须严格遵守）

1. **仅依据参考资料回答**：你只能使用下面"参考资料"中提供的内容来回答问题。

2. **禁止使用模型自身知识**：即使你了解云冈石窟的相关信息，也绝不能使用参考资料之外的任何知识。

3. **缺失处理**：如果参考资料中没有足够信息来回答问题，你必须明确回复：
   "知识库中未检索到相关信息。"

4. **引用来源**：每个关键事实后必须标注来源，每个来源单独使用一个方括号，
   格式为【来源：词条标题，页码】。禁止合并多个词条到一个方括号中。
   示例：【来源：第20窟，54】【来源：昙曜五窟，8】

5. **禁止编造**：不要编造、推测或补充参考资料中没有的内容。

## 回答格式

- 使用清晰、学术化的中文
- 先给出核心答案，再提供详细解释
- 最后列出所有引用的词条来源清单
"""


def build_prompt(
    query: str,
    retrieved_docs: list[RetrievalResult],
) -> list[dict[str, str]]:
    """Build the complete message list for the LLM API call.

    Args:
        query: The user's question.
        retrieved_docs: Top-k retrieved document chunks from the knowledge base.

    Returns:
        List of message dicts suitable for the OpenAI chat completions API.
    """
    # Build context from retrieved documents
    if not retrieved_docs:
        context = "（参考资料为空，没有检索到任何相关内容。）"
    else:
        context_parts = []
        for i, doc in enumerate(retrieved_docs, start=1):
            source_info = f"词条：{doc.title}"
            if doc.page is not None and doc.page > 0:
                source_info += f"，页码：{doc.page}"
            context_parts.append(
                f"[文档{i}] {source_info}\n内容：{doc.content}"
            )
        context = "\n\n---\n\n".join(context_parts)

    user_message = f"""## 参考资料

{context}

## 用户问题

{query}

请基于以上参考资料回答用户的问题。"""

    logger.debug(
        "Prompt built: %d docs, %d total chars",
        len(retrieved_docs),
        len(user_message),
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
