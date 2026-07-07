"""Routes for Home Paper Trainer."""

from backend.routes.health import router as health_router
from backend.routes.papers import router as papers_router

__all__ = ["papers_router", "health_router"]
