"""Configuration settings for the application."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Home Paper Trainer"
    debug: bool = True
    
    # Database
    database_url: str = "postgres://paper_trainer:paper_trainer@localhost:5432/paper_trainer"
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
