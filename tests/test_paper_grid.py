"""Tests for paper grid functionality (Issue #5)."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.services.paper_service import PaperService


class TestPaperGrid:
    """Tests for paper grid display and sorting."""

    @pytest.mark.asyncio
    async def test_calculate_completion_percentage_no_chapters(self):
        """Test completion percentage calculation with no chapters."""
        mock_session = AsyncMock()

        # Mock empty chapters query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result

        completion = await PaperService._calculate_completion_percentage(mock_session, 1)
        assert completion == 0.0

    @pytest.mark.asyncio
    async def test_calculate_completion_percentage_partial(self):
        """Test completion percentage calculation with partial completion."""
        mock_session = AsyncMock()

        # Mock chapters query
        mock_chapter1 = MagicMock()
        mock_chapter1.id = 1
        mock_chapter2 = MagicMock()
        mock_chapter2.id = 2

        mock_result_chapters = MagicMock()
        mock_result_chapters.scalars.return_value.all.return_value = [mock_chapter1, mock_chapter2]

        # Mock summaries query - only first chapter has summaries
        mock_summary = MagicMock()
        mock_result_summaries1 = MagicMock()
        mock_result_summaries1.scalars.return_value.all.return_value = [mock_summary]

        mock_result_summaries2 = MagicMock()
        mock_result_summaries2.scalars.return_value.all.return_value = []

        # Setup session to return different results for different queries
        mock_session.execute.side_effect = [
            mock_result_chapters,
            mock_result_summaries1,
            mock_result_summaries2,
        ]

        completion = await PaperService._calculate_completion_percentage(mock_session, 1)
        assert completion == 50.0

    @pytest.mark.asyncio
    async def test_calculate_completion_percentage_full(self):
        """Test completion percentage calculation with full completion."""
        mock_session = AsyncMock()

        # Mock chapters query
        mock_chapter1 = MagicMock()
        mock_chapter1.id = 1
        mock_chapter2 = MagicMock()
        mock_chapter2.id = 2

        mock_result_chapters = MagicMock()
        mock_result_chapters.scalars.return_value.all.return_value = [mock_chapter1, mock_chapter2]

        # Mock summaries query - both chapters have summaries
        mock_summary = MagicMock()
        mock_result_summaries1 = MagicMock()
        mock_result_summaries1.scalars.return_value.all.return_value = [mock_summary]

        mock_result_summaries2 = MagicMock()
        mock_result_summaries2.scalars.return_value.all.return_value = [mock_summary]

        # Setup session to return different results for different queries
        mock_session.execute.side_effect = [
            mock_result_chapters,
            mock_result_summaries1,
            mock_result_summaries2,
        ]

        completion = await PaperService._calculate_completion_percentage(mock_session, 1)
        assert completion == 100.0

    def test_sort_papers_by_title(self):
        """Test sorting papers by title."""
        mock_paper1 = MagicMock()
        mock_paper1.title = "Alpha Paper"
        mock_paper1.created_at = datetime.now()

        mock_paper2 = MagicMock()
        mock_paper2.title = "Zeta Paper"
        mock_paper2.created_at = datetime.now()

        papers_with_completion = [
            {"paper": mock_paper2, "completion": 0},
            {"paper": mock_paper1, "completion": 0},
        ]

        # Sort ascending
        sorted_asc = PaperService._sort_papers(papers_with_completion, "title", "asc")
        assert sorted_asc[0]["paper"].title == "Alpha Paper"
        assert sorted_asc[1]["paper"].title == "Zeta Paper"

        # Sort descending
        sorted_desc = PaperService._sort_papers(papers_with_completion, "title", "desc")
        assert sorted_desc[0]["paper"].title == "Zeta Paper"
        assert sorted_desc[1]["paper"].title == "Alpha Paper"

    def test_sort_papers_by_completion(self):
        """Test sorting papers by completion percentage."""
        mock_paper1 = MagicMock()
        mock_paper1.title = "Paper 1"
        mock_paper1.created_at = datetime.now()

        mock_paper2 = MagicMock()
        mock_paper2.title = "Paper 2"
        mock_paper2.created_at = datetime.now()

        papers_with_completion = [
            {"paper": mock_paper1, "completion": 25.0},
            {"paper": mock_paper2, "completion": 75.0},
        ]

        # Sort ascending
        sorted_asc = PaperService._sort_papers(papers_with_completion, "completion", "asc")
        assert sorted_asc[0]["completion"] == 25.0
        assert sorted_asc[1]["completion"] == 75.0

        # Sort descending
        sorted_desc = PaperService._sort_papers(papers_with_completion, "completion", "desc")
        assert sorted_desc[0]["completion"] == 75.0
        assert sorted_desc[1]["completion"] == 25.0

    def test_sort_papers_by_date(self):
        """Test sorting papers by date."""
        mock_paper1 = MagicMock()
        mock_paper1.title = "Paper 1"
        mock_paper1.created_at = datetime.now() - timedelta(days=1)

        mock_paper2 = MagicMock()
        mock_paper2.title = "Paper 2"
        mock_paper2.created_at = datetime.now()

        papers_with_completion = [
            {"paper": mock_paper2, "completion": 0},
            {"paper": mock_paper1, "completion": 0},
        ]

        # Sort ascending (oldest first)
        sorted_asc = PaperService._sort_papers(papers_with_completion, "created_at", "asc")
        assert sorted_asc[0]["paper"].title == "Paper 1"
        assert sorted_asc[1]["paper"].title == "Paper 2"

        # Sort descending (newest first)
        sorted_desc = PaperService._sort_papers(papers_with_completion, "created_at", "desc")
        assert sorted_desc[0]["paper"].title == "Paper 2"
        assert sorted_desc[1]["paper"].title == "Paper 1"
