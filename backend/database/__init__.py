"""Database connection and session management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

from backend.config import settings

# SQLAlchemy base
Base = declarative_base()

# Async engine (created lazily on first use)
_engine = None


def get_engine():
    """Get or create the async engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            future=True,
        )
    return _engine


# Async session factory
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session."""
    engine = get_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


@asynccontextmanager
async def lifespan(app) -> AsyncGenerator[None, None]:
    """Application lifespan manager - creates and disposes database engine."""
    global _engine
    # Startup: Create engine
    _engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True,
    )
    yield
    # Shutdown: Dispose engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
