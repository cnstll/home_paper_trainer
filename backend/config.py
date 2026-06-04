"""Configuration settings for the application.

NOTE: In production, ALL settings should be provided via environment variables.
      The defaults below are for development only and MUST NOT be used in production.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    In production, provide these via environment variables:
    - APP_NAME
    - DEBUG (false in production)
    - DATABASE_URL
    - SECRET_KEY
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "Home Paper Trainer"
    debug: bool = True

    # Database - REQUIRED: Must be provided via environment variable
    database_url: str

    # API
    api_v1_prefix: str = "/api/v1"

    # CORS - comma-separated list of allowed origins
    cors_origins: str = (
        "http://localhost,http://localhost:8000,http://127.0.0.1,http://127.0.0.1:8000"
    )

    # Static files directory
    static_dir: str = "frontend/static"

    # Security - REQUIRED: Must be provided via environment variable
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
