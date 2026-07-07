"""Tests for paper processing functionality (Issue #4)."""

from unittest.mock import MagicMock, patch

import pytest

from backend.services.processing_service import ProcessingService
from backend.services.validation_service import ValidationService


class TestProcessingService:
    """Tests for paper processing service."""

    def test_normalize_url_for_processing(self):
        """Test URL normalization for processing."""
        url = "https://arxiv.org/pdf/2304.00001"
        normalized = ValidationService.normalize_arxiv_url(url)
        assert normalized == "https://arxiv.org/abs/2304.00001"

    def test_extract_arxiv_id_for_processing(self):
        """Test arXiv ID extraction for processing."""
        url = "https://arxiv.org/abs/2304.00001v2"
        arxiv_id = ValidationService.extract_arxiv_id(url)
        assert arxiv_id == "2304.00001"

    @pytest.mark.asyncio
    async def test_fetch_and_parse_paper_mock(self):
        """Test fetching and parsing paper with mocked Docling."""
        # Mock the DocumentConverter
        mock_doc = MagicMock()
        mock_doc.title = "Test Paper"
        mock_doc.authors = [MagicMock(name="Author 1"), MagicMock(name="Author 2")]
        mock_doc.text = "This is the full text of the paper."
        mock_doc.document = None

        mock_result = MagicMock()
        mock_result.document = mock_doc

        with patch("backend.services.processing_service.DocumentConverter") as mock_converter:
            mock_converter_instance = mock_converter.return_value
            mock_converter_instance.convert.return_value = mock_result

            # Test the method
            doc = await ProcessingService._fetch_and_parse_paper("https://arxiv.org/abs/2304.00001")

            assert doc is not None
            assert doc.title == "Test Paper"

    def test_extract_metadata_and_chapters_fallback(self):
        """Test metadata and chapter extraction with fallback."""
        # Create a mock document
        mock_author = MagicMock()
        mock_author.name = "Author 1"

        mock_doc = MagicMock()
        mock_doc.title = "Test Paper"
        mock_doc.authors = [mock_author]
        mock_doc.text = "This is the full text"
        mock_doc.document = None

        metadata, chapters = ProcessingService._extract_metadata_and_chapters(mock_doc)

        assert metadata["title"] == "Test Paper"
        assert metadata["authors"] == ["Author 1"]
        assert len(chapters) == 1
        assert chapters[0]["title"] == "Full Paper"
        assert chapters[0]["content"] == "This is the full text"
        assert chapters[0]["word_count"] == 5

    def test_extract_metadata_and_chapters_with_sections(self):
        """Test metadata and chapter extraction with sections."""
        # Create a mock document with sections
        mock_section1 = MagicMock()
        mock_section1.title = "Introduction"
        mock_section1.text = "This is the introduction."

        mock_section2 = MagicMock()
        mock_section2.title = "Methods"
        mock_section2.text = "These are the methods used."

        mock_document = MagicMock()
        mock_document.children = [mock_section1, mock_section2]

        mock_doc = MagicMock()
        mock_doc.title = "Test Paper"
        mock_doc.authors = []
        mock_doc.text = ""
        mock_doc.document = mock_document

        metadata, chapters = ProcessingService._extract_metadata_and_chapters(mock_doc)

        assert metadata["title"] == "Test Paper"
        assert len(chapters) == 2
        assert chapters[0]["title"] == "Introduction"
        assert chapters[1]["title"] == "Methods"


class TestSummarizationService:
    """Tests for summarization service."""

    def test_summarization_prompt(self):
        """Test that summarization prompt is correctly formatted."""
        from backend.services.summarization_service import SUMMARIZATION_PROMPT

        prompt = SUMMARIZATION_PROMPT.format(chapter_content="Test content")
        assert "Test content" in prompt
        assert "Summarise" in prompt

    @pytest.mark.asyncio
    async def test_generate_chapter_summary_mock(self):
        """Test chapter summary generation with mocked Mistral API."""
        from backend.services.summarization_service import SummarizationService

        # Mock the Mistral client
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "This is a test summary."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        with patch("backend.services.summarization_service.mistralai") as mock_mistral:
            mock_mistral.api_key = "test-key"
            mock_client = mock_mistral.Mistral.return_value
            mock_client.chat.return_value = mock_response

            summary = await SummarizationService._generate_chapter_summary("Test content")

            assert summary == "This is a test summary."
