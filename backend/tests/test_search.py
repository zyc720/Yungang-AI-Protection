"""API endpoint tests for search, chat, and health."""

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for GET /api/health."""

    def test_health_returns_200(self, client: TestClient):
        """Health endpoint should return HTTP 200 with status info."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 200
        assert data["message"] == "success"
        assert "status" in data["data"]
        assert "milvus" in data["data"]


class TestSearchEndpoint:
    """Tests for POST /api/search."""

    def test_search_empty_query_rejected(self, client: TestClient):
        """Empty query should return 422 validation error."""
        response = client.post("/api/search", json={"query": ""})
        assert response.status_code == 422

    def test_search_missing_query_rejected(self, client: TestClient):
        """Missing query field should return 422."""
        response = client.post("/api/search", json={})
        assert response.status_code == 422

    def test_search_valid_request_accepted(self, client: TestClient):
        """Valid search request should return 200 (even if no results)."""
        response = client.post(
            "/api/search",
            json={"query": "云冈石窟", "top_k": 3},
        )
        # 200 if Milvus is accessible, may be 500 if Milvus is down
        # but should never be 422 for a valid request
        assert response.status_code in (200, 500)
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == 200
            assert "results" in data["data"]
            assert "total" in data["data"]


class TestChatEndpoint:
    """Tests for POST /api/chat."""

    def test_chat_empty_query_rejected(self, client: TestClient):
        """Empty query should return 422."""
        response = client.post("/api/chat", json={"query": ""})
        assert response.status_code == 422

    def test_chat_valid_request_accepted(self, client: TestClient):
        """Valid chat request should return 200 (or 500 if no LLM key)."""
        response = client.post(
            "/api/chat",
            json={"query": "云冈石窟的历史", "top_k": 3},
        )
        # 200 if everything works, 500 if Milvus/LLM unavailable
        assert response.status_code in (200, 500)
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == 200
            assert "answer" in data["data"]
            assert "sources" in data["data"]
