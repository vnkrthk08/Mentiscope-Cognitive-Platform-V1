"""
ASAT â€“ Application Configuration
Loads all settings from environment variables (.env file).
No credentials are hardcoded. See .env.example for required variables.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All database names, table prefixes, and credentials are configurable
    so they can be aligned with the official MentiScope shared schema later.
    """

    # â”€â”€ Database (PostgreSQL) â”€â”€
    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_name: str = "asat"
    db_user: str = "postgres"
    db_password: str = ""

    # â”€â”€ Application â”€â”€
    app_port: int = 8000
    app_secret_key: str = "change-me-in-production"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # â”€â”€ Module Identity (MentiScope Integration) â”€â”€
    module_id: str = "asat_attention"
    module_name: str = "Adaptive Shape Attention Task"
    construct: str = "Attention"

    @property
    def database_url(self) -> str:
        """Async SQLite connection string for SQLAlchemy."""
        return "sqlite+aiosqlite:///./mentiscope.db"

    @property
    def database_url_sync(self) -> str:
        """Sync SQLite connection string (for migrations/scripts)."""
        return "sqlite:///./mentiscope.db"

    @property
    def cors_origin_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
settings = Settings()
