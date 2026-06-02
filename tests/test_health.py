"""Tests for health endpoints."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def test_app():
    """Create a test app."""
    return app


def test_health_endpoint(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Home Paper Trainer" in response.text


def test_api_health_endpoint(client):
    """Test the /api/health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_api_docs_endpoint(client):
    """Test the API docs endpoint."""
    response = client.get("/api/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text or "ReDoc" in response.text
