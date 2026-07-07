"""Paper service for managing papers."""

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.models.chapter import Chapter
from backend.models.paper import Paper
from backend.models.user_summary import UserSummary
from backend.services.processing_service import ProcessingService
from backend.services.summarization_service import SummarizationService
from backend.services.validation_service import ValidationService

logger = logging.getLogger(__name__)


class PaperService:
    """Service for managing papers in the database."""

    @staticmethod
    async def create_paper(
        session: AsyncSession,
        url: str,
    ) -> tuple[Paper | None, str]:
        """Create a new paper record with pending status.

        Args:
            session: Async database session
            url: arXiv URL to create paper from

        Returns:
            Tuple of (paper, error_message)
        """
        # Validate URL
        is_valid, error_msg = ValidationService.validate_arxiv_url(url)
        if not is_valid:
            return None, error_msg

        # Extract arXiv ID
        arxiv_id = ValidationService.extract_arxiv_id(url)
        if not arxiv_id:
            return None, "Could not extract arXiv ID from URL."

        # Normalize URL
        normalized_url = ValidationService.normalize_arxiv_url(url)

        # Check if paper already exists
        result = await session.execute(select(Paper).where(Paper.arxiv_id == arxiv_id))
        existing_paper = result.scalar_one_or_none()

        if existing_paper:
            return existing_paper, "Paper already exists."

        # Create new paper
        paper = Paper(
            arxiv_id=arxiv_id,
            url=normalized_url,
            title=f"Paper {arxiv_id}",  # Will be updated during processing
            status="pending",
        )

        session.add(paper)
        await session.commit()
        await session.refresh(paper)

        # Start processing in background
        asyncio.create_task(PaperService._process_paper_background(session, paper))

        return paper, ""

    @staticmethod
    async def _process_paper_background(
        session: AsyncSession,
        paper: Paper,
    ) -> None:
        """Process paper in background: fetch, parse, generate summaries.

        Args:
            session: Async database session
            paper: Paper object to process
        """
        try:
            # Process paper (fetch and parse)
            success, error_msg = await ProcessingService.process_paper(session, paper)

            if not success:
                # Processing failed, update status
                paper.status = "error"
                await session.commit()
                return

            # Generate reference summaries
            success, error_msg = await SummarizationService.generate_reference_summaries(
                session, paper
            )

            if not success:
                # Summarization failed, but paper is still processed
                logger.warning(f"Summarization failed for paper {paper.arxiv_id}: {error_msg}")

        except Exception as e:
            logger.error(f"Background processing failed for paper {paper.arxiv_id}: {str(e)}")
            paper.status = "error"
            await session.commit()

    @staticmethod
    async def get_paper(session: AsyncSession, paper_id: int) -> Paper | None:
        """Get a paper by ID.

        Args:
            session: Async database session
            paper_id: ID of the paper to retrieve

        Returns:
            Paper object or None if not found
        """
        result = await session.execute(select(Paper).where(Paper.id == paper_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_papers(session: AsyncSession) -> list[Paper]:
        """Get all papers.

        Args:
            session: Async database session

        Returns:
            List of all papers
        """
        result = await session.execute(select(Paper))
        return result.scalars().all()

    @staticmethod
    async def get_papers_with_completion(
        session: AsyncSession,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[dict]:
        """Get all papers with completion percentage and sorting.

        Args:
            session: Async database session
            sort_by: Field to sort by ('created_at', 'title', 'completion')
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            List of paper dictionaries with completion percentage
        """
        # Get all papers
        result = await session.execute(select(Paper))
        papers = result.scalars().all()

        # Calculate completion percentage for each paper
        papers_with_completion = []
        for paper in papers:
            completion = await PaperService._calculate_completion_percentage(session, paper.id)
            papers_with_completion.append(
                {
                    "paper": paper,
                    "completion": completion,
                }
            )

        # Sort papers
        papers_with_completion = PaperService._sort_papers(
            papers_with_completion, sort_by, sort_order
        )

        return papers_with_completion

    @staticmethod
    async def _calculate_completion_percentage(
        session: AsyncSession,
        paper_id: int,
    ) -> float:
        """Calculate completion percentage for a paper.

        Args:
            session: Async database session
            paper_id: ID of the paper

        Returns:
            Completion percentage (0-100)
        """
        # Get all chapters for this paper
        result = await session.execute(select(Chapter).where(Chapter.paper_id == paper_id))
        chapters = result.scalars().all()

        if not chapters:
            return 0.0

        # Count chapters with summaries
        completed_count = 0
        for chapter in chapters:
            # Check if there are any user summaries for this chapter
            summary_result = await session.execute(
                select(UserSummary).where(UserSummary.chapter_id == chapter.id)
            )
            summaries = summary_result.scalars().all()
            if summaries:
                completed_count += 1

        # Calculate percentage
        return (completed_count / len(chapters)) * 100

    @staticmethod
    def _sort_papers(
        papers_with_completion: list[dict],
        sort_by: str,
        sort_order: str,
    ) -> list[dict]:
        """Sort papers by specified criteria.

        Args:
            papers_with_completion: List of paper dictionaries with completion
            sort_by: Field to sort by
            sort_order: Sort order

        Returns:
            Sorted list of paper dictionaries
        """
        reverse = sort_order == "desc"

        if sort_by == "title":
            return sorted(
                papers_with_completion,
                key=lambda x: x["paper"].title.lower() if x["paper"].title else "",
                reverse=reverse,
            )
        elif sort_by == "completion":
            return sorted(
                papers_with_completion,
                key=lambda x: x["completion"],
                reverse=reverse,
            )
        else:  # Default: sort by created_at
            return sorted(
                papers_with_completion,
                key=lambda x: x["paper"].created_at,
                reverse=reverse,
            )

    @staticmethod
    async def delete_paper(session: AsyncSession, paper_id: int) -> bool:
        """Delete a paper by ID.

        Args:
            session: Async database session
            paper_id: ID of the paper to delete

        Returns:
            True if deleted, False if not found
        """
        result = await session.execute(select(Paper).where(Paper.id == paper_id))
        paper = result.scalar_one_or_none()

        if paper:
            await session.delete(paper)
            await session.commit()
            return True

        return False
