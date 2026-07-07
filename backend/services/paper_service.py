"""Paper service for managing papers."""

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.models.paper import Paper
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
