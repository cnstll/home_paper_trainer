"""Main FastAPI application for Home Paper Trainer."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db


app = FastAPI(
    title="Home Paper Trainer API",
    description="A project management and learning platform",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup."""
    await init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Home Paper Trainer - Welcome!"}


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
