"""Database connection and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

from backend.config import settings

# Create async engine lazily
engine = None


def get_engine():
    """Get or create the async engine."""
    global engine
    if engine is None:
        engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            future=True,
        )
    return engine


# Async session factory
async def get_db():
    """Get an async database session."""
    engine = get_engine()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


async def init_db():
    """Initialize database connection."""
    # Connection is established lazily on first use
    pass


Base = declarative_base()
