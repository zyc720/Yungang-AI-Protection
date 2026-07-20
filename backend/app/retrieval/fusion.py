"""
Fusion algorithms for combining BM25 and vector retrieval results.

Two strategies are provided:
1. Reciprocal Rank Fusion (RRF): Combines rankings, not scores. More
   robust because it doesn't require score normalization. Default method.
2. Weighted Fusion: Normalizes scores per-method to [0,1] then applies
   a weighted linear combination. Requires at least one result per method
   for proper normalization.
"""

import logging
from app.retrieval.base import RetrievalResult

logger = logging.getLogger(__name__)


def reciprocal_rank_fusion(
    bm25_results: list[RetrievalResult],
    vector_results: list[RetrievalResult],
    k: int = 60,
    top_k: int = 5,
) -> list[RetrievalResult]:
    """Fuse two ranked result lists using Reciprocal Rank Fusion (RRF).

    RRF score: sum_{r in rankings} 1 / (k + rank(d, r))

    This is the recommended fusion method because it:
    - Does not require score normalization
    - Is robust to different score distributions
    - Naturally handles documents in only one ranking
    - Uses the classic k=60 constant from the RRF paper

    Args:
        bm25_results: BM25 results ordered by score descending.
        vector_results: Vector results ordered by score descending.
        k: RRF constant (default 60).
        top_k: Number of fused results to return.

    Returns:
        Fused results sorted by RRF score descending, with
        retrieval_method set to "hybrid_rrf".
    """
    scores: dict[str, tuple[RetrievalResult, float]] = {}

    # Process BM25 rankings
    for rank, result in enumerate(bm25_results, start=1):
        key = f"{result.entry_id}:{result.chunk_id}"
        rrf_score = 1.0 / (k + rank)
        scores[key] = (result, rrf_score)

    # Process vector rankings
    for rank, result in enumerate(vector_results, start=1):
        key = f"{result.entry_id}:{result.chunk_id}"
        rrf_score = 1.0 / (k + rank)
        if key in scores:
            existing_result, existing_score = scores[key]
            # Keep the result with the higher individual score
            best = result if result.score > existing_result.score else existing_result
            scores[key] = (best, existing_score + rrf_score)
        else:
            scores[key] = (result, rrf_score)

    # Sort by RRF score, take top_k
    sorted_items = sorted(
        scores.values(), key=lambda x: x[1], reverse=True
    )[:top_k]

    fused = []
    for result, rrf_score in sorted_items:
        result.score = rrf_score
        result.retrieval_method = "hybrid_rrf"
        fused.append(result)

    logger.debug(
        "RRF fusion: %d bm25 + %d vector -> %d fused results",
        len(bm25_results),
        len(vector_results),
        len(fused),
    )
    return fused


def weighted_fusion(
    bm25_results: list[RetrievalResult],
    vector_results: list[RetrievalResult],
    bm25_weight: float = 0.3,
    vector_weight: float = 0.7,
    top_k: int = 5,
) -> list[RetrievalResult]:
    """Fuse results using min-max normalized weighted score combination.

    Normalizes each result set's scores to [0, 1], then combines with
    the given weights. Requires at least one result per method for
    proper normalization.

    Args:
        bm25_results: BM25 results ordered by score descending.
        vector_results: Vector results ordered by score descending.
        bm25_weight: Weight for BM25 scores (default 0.3).
        vector_weight: Weight for vector scores (default 0.7).
        top_k: Number of fused results to return.

    Returns:
        Fused results sorted by combined score descending, with
        retrieval_method set to "hybrid_weighted".
    """

    def _normalize(results: list[RetrievalResult]) -> list[RetrievalResult]:
        if not results:
            return results
        scores = [r.score for r in results]
        min_s, max_s = min(scores), max(scores)
        if max_s == min_s:
            for r in results:
                r.score = 1.0
        else:
            for r in results:
                r.score = (r.score - min_s) / (max_s - min_s)
        return results

    norm_bm25 = _normalize([r for r in bm25_results])
    norm_vector = _normalize([r for r in vector_results])

    combined: dict[str, tuple[RetrievalResult, float]] = {}

    for r in norm_bm25:
        key = f"{r.entry_id}:{r.chunk_id}"
        combined[key] = (r, r.score * bm25_weight)

    for r in norm_vector:
        key = f"{r.entry_id}:{r.chunk_id}"
        if key in combined:
            existing_result, existing_score = combined[key]
            best = r if r.score > existing_result.score else existing_result
            combined[key] = (best, existing_score + r.score * vector_weight)
        else:
            combined[key] = (r, r.score * vector_weight)

    sorted_items = sorted(
        combined.values(), key=lambda x: x[1], reverse=True
    )[:top_k]

    results = []
    for result, score in sorted_items:
        result.score = score
        result.retrieval_method = "hybrid_weighted"
        results.append(result)

    logger.debug(
        "Weighted fusion: %d bm25 + %d vector -> %d fused results (w1=%.1f, w2=%.1f)",
        len(bm25_results),
        len(vector_results),
        len(results),
        bm25_weight,
        vector_weight,
    )
    return results
