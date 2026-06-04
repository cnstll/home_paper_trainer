"""Database connection and session management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base

from backend.config import settings

# SQLAlchemy base
Base = declarative_base()


@asynccontextmanager
async def lifespan(app) -> AsyncGenerator[None, None]:
    """Application lifespan manager - creates and disposes database engine."""
    # Startup: Create engine and store in app state
    app.state.db_engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
    )
    yield
    # Shutdown: Dispose engine
    if hasattr(app.state, "db_engine"):
        await app.state.db_engine.dispose()


# Async session factory
async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session."""
    engine = request.app.state.db_engine
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
