"""Pytest fixtures for the Yungang Dictionary RAG backend tests."""

import pytest
from fastapi.testclient import TestClient
from app.core.app_factory import create_app


@pytest.fixture
def app():
    """Create a test FastAPI application instance."""
    return create_app()


@pytest.fixture
def client(app):
    """Create a FastAPI TestClient for the test application."""
    return TestClient(app)
