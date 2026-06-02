"""Database connection and session management."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

from backend.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Async session factory
async def get_db():
    """Get an async database session."""
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


async def init_db():
    """Initialize database - create tables if they don't exist."""
    async with engine.begin() as conn:
        # Import all models here to ensure they're registered with Base
        from backend.database.models import User, Project, Paper, Note  # noqa: F401
        await conn.run_sync(declarative_base().metadata.create_all)


Base = declarative_base()
