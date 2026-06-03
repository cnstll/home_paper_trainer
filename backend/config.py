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
        case_sensitive=True,
    )

    # Application
    app_name: str = "Home Paper Trainer"
    debug: bool = True

    # Database - OVERRIDE IN PRODUCTION
    database_url: str = (
        "postgresql+asyncpg://paper_trainer:paper_trainer@localhost:5432/paper_trainer"
    )

    # API
    api_v1_prefix: str = "/api/v1"

    # Security - OVERRIDE IN PRODUCTION
    secret_key: str = "dev-only-change-in-production-use-secrets-manager"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


settings = Settings()
