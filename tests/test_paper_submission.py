"""Tests for paper submission functionality (Issue #3)."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.validation_service import ValidationService


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


class TestValidationService:
    """Tests for URL validation."""

    def test_valid_arxiv_urls(self):
        """Test that valid arXiv URLs are accepted."""
        valid_urls = [
            "https://arxiv.org/abs/2304.00001",
            "https://arxiv.org/pdf/2304.00001",
            "https://arxiv.org/abs/2304.00001v1",
            "arxiv.org/abs/2304.00001",
            "www.arxiv.org/abs/2304.00001",
        ]

        for url in valid_urls:
            is_valid, error = ValidationService.validate_arxiv_url(url)
            assert is_valid, f"URL {url} should be valid, got error: {error}"

    def test_invalid_arxiv_urls(self):
        """Test that invalid URLs are rejected."""
        invalid_urls = [
            "https://google.com",
            "not-a-url",
            "https://arxiv.org",
            "",
        ]

        for url in invalid_urls:
            is_valid, error = ValidationService.validate_arxiv_url(url)
            assert not is_valid, f"URL {url} should be invalid"
            assert error == "Invalid arXiv URL. Please try again."

    def test_extract_arxiv_id(self):
        """Test arXiv ID extraction."""
        test_cases = [
            ("https://arxiv.org/abs/2304.00001", "2304.00001"),
            ("https://arxiv.org/pdf/2304.00001v1", "2304.00001"),
            ("arxiv.org/abs/2304.00001", "2304.00001"),
        ]

        for url, expected_id in test_cases:
            arxiv_id = ValidationService.extract_arxiv_id(url)
            assert arxiv_id == expected_id, f"Expected {expected_id}, got {arxiv_id}"

    def test_normalize_arxiv_url(self):
        """Test URL normalization."""
        test_cases = [
            ("https://arxiv.org/pdf/2304.00001", "https://arxiv.org/abs/2304.00001"),
            ("arxiv.org/abs/2304.00001", "https://arxiv.org/abs/2304.00001"),
            ("https://arxiv.org/abs/2304.00001", "https://arxiv.org/abs/2304.00001"),
        ]

        for url, expected in test_cases:
            normalized = ValidationService.normalize_arxiv_url(url)
            assert normalized == expected, f"Expected {expected}, got {normalized}"


class TestPaperRoutes:
    """Tests for paper routes - these tests don't require database."""

    def test_validation_service_integration(self):
        """Test that validation service works correctly."""
        # Test the service directly
        service = ValidationService()

        # Valid URL
        is_valid, error = service.validate_arxiv_url("https://arxiv.org/abs/2304.00001")
        assert is_valid
        assert error is None

        # Invalid URL
        is_valid, error = service.validate_arxiv_url("https://google.com")
        assert not is_valid
        assert error == "Invalid arXiv URL. Please try again."

    def test_extract_and_normalize_integration(self):
        """Test extraction and normalization together."""
        url = "https://arxiv.org/pdf/2304.00001v2"

        # Normalize
        normalized = ValidationService.normalize_arxiv_url(url)
        assert normalized == "https://arxiv.org/abs/2304.00001v2"

        # Extract ID
        arxiv_id = ValidationService.extract_arxiv_id(normalized)
        assert arxiv_id == "2304.00001"
