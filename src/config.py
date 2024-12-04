"""Configuration settings for the application."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with default values."""

    CHUNK_SIZE: int = 1024 * 1024 * 100
    LOG_LEVEL: str = "INFO"
    MAX_WORKERS: int = 4
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_CHUNK_SIZE: int = 1000

    PG_HOST: str = "postgres"
    PG_PORT: int = 5432
    PG_DB: str = "logdb"
    PG_USER: str = "loguser"
    PG_PASSWORD: str = "logpassword"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
