"""Summarization service for generating reference summaries using Mistral API."""

import logging

import mistralai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.models.chapter import Chapter
from backend.models.paper import Paper

logger = logging.getLogger(__name__)

# Mistral API configuration
MISTRAL_MODEL = "mistral-small-latest"
SUMMARIZATION_PROMPT = """Summarise the following chapter from a scientific paper
concisely and accurately.
Focus on the core contributions, methods, and results.
Output only the summary - no preamble, no commentary.

Chapter: {chapter_content}"""


class SummarizationService:
    """Service for generating reference summaries using Mistral API."""

    @staticmethod
    async def generate_reference_summaries(
        session: AsyncSession,
        paper: Paper,
    ) -> tuple[bool, str | None]:
        """Generate reference summaries for all chapters of a paper.

        Args:
            session: Async database session
            paper: Paper object to generate summaries for

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Get all chapters for this paper
            result = await session.execute(select(Chapter).where(Chapter.paper_id == paper.id))
            chapters = result.scalars().all()

            if not chapters:
                return True, None  # No chapters to summarize

            # Generate summary for each chapter
            for chapter in chapters:
                if not chapter.reference_summary:
                    summary = await SummarizationService._generate_chapter_summary(chapter.content)
                    if summary:
                        chapter.reference_summary = summary
                        await session.commit()
                    else:
                        logger.warning(
                            f"Failed to generate summary for chapter {chapter.id} "
                            f"of paper {paper.arxiv_id}"
                        )

            return True, None

        except Exception as e:
            logger.error(f"Error generating reference summaries: {str(e)}")
            return False, "Feedback generation failed. Please try again."

    @staticmethod
    async def _generate_chapter_summary(chapter_content: str) -> str | None:
        """Generate a summary for a single chapter using Mistral API.

        Args:
            chapter_content: Content of the chapter to summarize

        Returns:
            Generated summary or None on failure
        """
        try:
            # Check if we have API key
            api_key = getattr(mistralai, "api_key", None)
            if not api_key:
                logger.warning("Mistral API key not configured")
                return None

            # Create Mistral client
            client = mistralai.Mistral(
                api_key=api_key,
            )

            # Prepare prompt
            prompt = SUMMARIZATION_PROMPT.format(
                chapter_content=chapter_content[:4000]  # Limit to 4000 chars for now
            )

            # Generate summary
            response = client.chat(
                model=MISTRAL_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500,
            )

            # Extract summary from response
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content

            return None

        except Exception as e:
            logger.error(f"Error generating chapter summary: {str(e)}")
            return None
