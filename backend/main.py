"""Main FastAPI application for Home Paper Trainer."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import lifespan, get_db


# Create FastAPI app with lifespan
app = FastAPI(
    title="Home Paper Trainer API",
    description="A project management and learning platform",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Configure CORS - restricted to local development by default
# In production, set CORS_ORIGINS environment variable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8000", "http://127.0.0.1", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Home Paper Trainer - Welcome!"}


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
