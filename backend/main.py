"""Main FastAPI application for Home Paper Trainer."""

from importlib.metadata import version

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import lifespan
from backend.routes import health_router, papers_router

# Get version from pyproject.toml
APP_VERSION = version("home-paper-trainer")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Home Paper Trainer API",
    description="A project management and learning platform",
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Configure CORS from settings
cors_origins = settings.cors_origins.split(",") if settings.cors_origins else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files from settings
static_dir = settings.static_dir if hasattr(settings, "static_dir") else "frontend/static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(health_router)
app.include_router(papers_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Home Paper Trainer - Welcome!"}
