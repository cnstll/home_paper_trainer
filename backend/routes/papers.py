"""Paper routes for submitting and managing papers."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models.chapter import Chapter
from backend.models.paper import Paper
from backend.services.paper_service import PaperService
from backend.services.validation_service import ValidationService

router = APIRouter(prefix="/papers", tags=["papers"])

# Setup templates
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def list_papers(
    request: Request,
    db: AsyncSession = Depends(get_db),
    sort_by: str = "created_at",
    sort_order: str = "desc",
):
    """List all papers with submission form and sorting."""
    try:
        # Get papers with completion percentage
        papers_with_completion = await PaperService.get_papers_with_completion(
            db, sort_by=sort_by, sort_order=sort_order
        )
    except Exception:
        papers_with_completion = []

    # Extract just the papers for the template
    papers = [pwc["paper"] for pwc in papers_with_completion]
    completions = {pwc["paper"].id: pwc["completion"] for pwc in papers_with_completion}

    return templates.TemplateResponse(
        "papers/index.html",
        {
            "request": request,
            "papers": papers,
            "completions": completions,
            "sort_by": sort_by,
            "sort_order": sort_order,
        },
    )


@router.post("/", response_class=HTMLResponse)
async def submit_paper(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Submit a new arXiv URL for processing."""
    form_data = await request.form()
    url = form_data.get("url", "").strip()

    # Validate URL first
    is_valid, error_msg = ValidationService.validate_arxiv_url(url)

    if not url:
        error_msg = "Please enter a URL."
        is_valid = False

    if not is_valid:
        try:
            papers_with_completion = await PaperService.get_papers_with_completion(db)
        except Exception:
            papers_with_completion = []
        papers = [pwc["paper"] for pwc in papers_with_completion]
        completions = {pwc["paper"].id: pwc["completion"] for pwc in papers_with_completion}
        return templates.TemplateResponse(
            "papers/index.html",
            {
                "request": request,
                "papers": papers,
                "completions": completions,
                "error": error_msg,
            },
        )

    # Create paper
    try:
        paper, error_msg = await PaperService.create_paper(db, url)
        if error_msg:
            try:
                papers_with_completion = await PaperService.get_papers_with_completion(db)
            except Exception:
                papers_with_completion = []
            papers = [pwc["paper"] for pwc in papers_with_completion]
            completions = {pwc["paper"].id: pwc["completion"] for pwc in papers_with_completion}
            return templates.TemplateResponse(
                "papers/index.html",
                {
                    "request": request,
                    "papers": papers,
                    "completions": completions,
                    "error": error_msg,
                },
            )
    except Exception as e:
        try:
            papers_with_completion = await PaperService.get_papers_with_completion(db)
        except Exception:
            papers_with_completion = []
        papers = [pwc["paper"] for pwc in papers_with_completion]
        completions = {pwc["paper"].id: pwc["completion"] for pwc in papers_with_completion}
        return templates.TemplateResponse(
            "papers/index.html",
            {
                "request": request,
                "papers": papers,
                "completions": completions,
                "error": f"Error creating paper: {str(e)}",
            },
        )

    # Success - redirect to papers list
    return HTMLResponse(
        status_code=303,
        headers={"Location": "/papers"},
    )


@router.get("/{paper_id}/chapters", response_class=HTMLResponse)
async def list_chapters(
    request: Request,
    paper_id: int,
    db: AsyncSession = Depends(get_db),
):
    """List all chapters for a specific paper."""
    # Get the paper
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    # Get all chapters for this paper, ordered by chapter_order
    result = await db.execute(
        select(Chapter).where(Chapter.paper_id == paper_id).order_by(Chapter.chapter_order)
    )
    chapters = result.scalars().all()

    return templates.TemplateResponse(
        "papers/chapters.html",
        {
            "request": request,
            "paper": paper,
            "chapters": chapters,
        },
    )


@router.get("/{paper_id}/chapters/{chapter_id}/read", response_class=HTMLResponse)
async def read_chapter(
    request: Request,
    paper_id: int,
    chapter_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Display reading interface for a specific chapter."""
    # Get the paper
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    # Get the chapter
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.paper_id == paper_id)
    )
    chapter = result.scalar_one_or_none()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    return templates.TemplateResponse(
        "papers/read.html",
        {
            "request": request,
            "paper": paper,
            "chapter": chapter,
        },
    )
