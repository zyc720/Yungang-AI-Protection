"""Unit tests for fusion algorithms and retrieval data structures."""

from app.retrieval.base import RetrievalResult
from app.retrieval.fusion import reciprocal_rank_fusion, weighted_fusion


def _make_result(
    entry_id: str,
    title: str,
    page: int | None,
    chunk_id: str,
    content: str,
    score: float,
    method: str = "bm25",
) -> RetrievalResult:
    """Helper to create a RetrievalResult for testing."""
    return RetrievalResult(
        entry_id=entry_id,
        title=title,
        page=page,
        chunk_id=chunk_id,
        content=content,
        score=score,
        retrieval_method=method,
    )


class TestReciprocalRankFusion:
    """Tests for reciprocal_rank_fusion()."""

    def test_empty_inputs(self):
        """RRF with no results should return empty list."""
        result = reciprocal_rank_fusion([], [], top_k=5)
        assert len(result) == 0

    def test_single_source_only(self):
        """RRF with only BM25 results should return those results."""
        bm25 = [_make_result("e1", "Title A", 1, "c1", "content", 0.9)]
        result = reciprocal_rank_fusion(bm25, [], top_k=5)
        assert len(result) == 1
        assert result[0].entry_id == "e1"
        assert result[0].retrieval_method == "hybrid_rrf"

    def test_vector_source_only(self):
        """RRF with only vector results should return those results."""
        vector = [_make_result("e2", "Title B", 2, "c2", "content", 0.95, "vector")]
        result = reciprocal_rank_fusion([], vector, top_k=5)
        assert len(result) == 1
        assert result[0].entry_id == "e2"

    def test_combines_rankings(self):
        """RRF should boost items appearing in both rankings."""
        bm25 = [
            _make_result("e1", "A", 1, "c1", "content A", 0.9),
            _make_result("e2", "B", 2, "c2", "content B", 0.5),
        ]
        vector = [
            _make_result("e2", "B", 2, "c2", "content B", 0.95, "vector"),
            _make_result("e3", "C", 3, "c3", "content C", 0.8, "vector"),
        ]
        result = reciprocal_rank_fusion(bm25, vector, top_k=3)
        # e2 appears in both rankings => highest RRF score
        assert result[0].entry_id == "e2"
        assert result[0].retrieval_method == "hybrid_rrf"
        assert len(result) == 3

    def test_respects_top_k_limit(self):
        """RRF should return at most top_k results."""
        bm25 = [
            _make_result(f"e{i}", f"Title {i}", i, f"c{i}", f"content {i}", 0.9 - i * 0.1)
            for i in range(5)
        ]
        result = reciprocal_rank_fusion(bm25, [], top_k=3)
        assert len(result) == 3


class TestWeightedFusion:
    """Tests for weighted_fusion()."""

    def test_weighted_fusion_basic(self):
        """Weighted fusion should combine scores from both methods."""
        bm25 = [_make_result("e1", "A", 1, "c1", "content A", 0.9)]
        vector = [_make_result("e2", "B", 2, "c2", "content B", 0.95, "vector")]
        result = weighted_fusion(bm25, vector, bm25_weight=0.3, vector_weight=0.7, top_k=2)
        assert len(result) == 2
        for r in result:
            assert r.retrieval_method == "hybrid_weighted"

    def test_weighted_fusion_empty_second(self):
        """Weighted fusion with one empty list should still work."""
        bm25 = [_make_result("e1", "A", 1, "c1", "content", 0.9)]
        result = weighted_fusion(bm25, [], bm25_weight=0.3, vector_weight=0.7, top_k=5)
        assert len(result) == 1

    def test_weighted_fusion_respects_top_k(self):
        """Should return at most top_k results."""
        bm25 = [
            _make_result(f"e{i}", f"T{i}", None, f"c{i}", "x", 0.9 - i * 0.1)
            for i in range(5)
        ]
        vector = [
            _make_result(f"v{i}", f"V{i}", None, f"vc{i}", "y", 0.8 - i * 0.1, "vector")
            for i in range(5)
        ]
        result = weighted_fusion(bm25, vector, top_k=3)
        assert len(result) == 3
