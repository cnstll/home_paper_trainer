"""Processing service for fetching and parsing papers with Docling."""

import logging
from typing import TYPE_CHECKING, Optional

from docling.document_converter import DocumentConverter
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.chapter import Chapter
from backend.models.paper import Paper
from backend.services.validation_service import ValidationService

if TYPE_CHECKING:
    from docling.datamodel.document import DoclingDocument

logger = logging.getLogger(__name__)


class ProcessingService:
    """Service for processing arXiv papers using Docling."""

    @staticmethod
    async def process_paper(
        session: AsyncSession,
        paper: Paper,
    ) -> tuple[bool, str | None]:
        """Process a paper: fetch, parse, and store chapters.

        Args:
            session: Async database session
            paper: Paper object to process

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Update status to processing
            paper.status = "processing"
            await session.commit()

            # Fetch and parse the paper
            url = paper.url
            doc = await ProcessingService._fetch_and_parse_paper(url)

            if doc is None:
                paper.status = "error"
                await session.commit()
                return False, "This paper couldn't be parsed. Try another arXiv URL."

            # Extract metadata and chapters
            metadata, chapters_data = ProcessingService._extract_metadata_and_chapters(doc)

            # Update paper metadata
            paper.title = metadata.get("title", f"Paper {paper.arxiv_id}")
            paper.authors = metadata.get("authors", [])
            await session.commit()

            # Store chapters
            for order, chapter_data in enumerate(chapters_data):
                chapter = Chapter(
                    paper_id=paper.id,
                    title=chapter_data["title"],
                    content=chapter_data["content"],
                    word_count=chapter_data["word_count"],
                    chapter_order=order,
                    reference_summary="",  # Will be generated later
                )
                session.add(chapter)

            await session.commit()

            # Update paper status to processed
            paper.status = "processed"
            await session.commit()

            return True, None

        except Exception as e:
            logger.error(f"Error processing paper {paper.arxiv_id}: {str(e)}")
            paper.status = "error"
            await session.commit()
            return False, f"Error processing paper: {str(e)}"

    @staticmethod
    async def _fetch_and_parse_paper(url: str) -> Optional["DoclingDocument"]:
        """Fetch and parse a paper from arXiv URL.

        Args:
            url: arXiv URL to fetch and parse

        Returns:
            Parsed DoclingDocument object or None on failure
        """
        try:
            # Normalize URL to abs format
            normalized_url = ValidationService.normalize_arxiv_url(url)

            # Use Docling to parse the paper
            converter = DocumentConverter()
            result = converter.convert(normalized_url)

            return result.document

        except Exception as e:
            logger.error(f"Error fetching/parsing paper from {url}: {str(e)}")
            return None

    @staticmethod
    def _extract_metadata_and_chapters(
        doc: "DoclingDocument",
    ) -> tuple[dict, list[dict]]:
        """Extract metadata and chapters from a parsed document.

        Args:
            doc: Parsed DoclingDocument object

        Returns:
            Tuple of (metadata_dict, chapters_list)
        """
        # Extract metadata
        metadata = {
            "title": getattr(doc, "title", None) or "",
            "authors": [author.name for author in getattr(doc, "authors", [])]
            if getattr(doc, "authors", None)
            else [],
        }

        # Extract chapters/sections
        chapters: list[dict] = []

        # Try to get document structure
        if hasattr(doc, "document") and doc.document:
            # Docling documents have a document structure
            for i, section in enumerate(doc.document.children):
                if hasattr(section, "text") and section.text:
                    title = getattr(section, "title", f"Section {i + 1}")
                    content = section.text
                    word_count = len(content.split())

                    chapters.append(
                        {
                            "title": title,
                            "content": content,
                            "word_count": word_count,
                        }
                    )
        else:
            # Fallback: treat entire document as one chapter
            content = getattr(doc, "text", None) or ""
            word_count = len(content.split())

            chapters.append(
                {
                    "title": "Full Paper",
                    "content": content,
                    "word_count": word_count,
                }
            )

        return metadata, chapters
