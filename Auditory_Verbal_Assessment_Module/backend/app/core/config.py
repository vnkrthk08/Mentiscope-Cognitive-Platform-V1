import os
from typing import List, Optional
from pathlib import Path
from pydantic import Field, AliasChoices, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.constants import Environment, API_V1_STR, PROJECT_NAME, PROJECT_VERSION, ALGORITHM_HS256


BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @model_validator(mode="after")
    def force_mock_for_tests(self) -> "Settings":
        import os
        if self.ENVIRONMENT.value == "testing" or os.getenv("ENVIRONMENT") == "testing":
            self.LLM_MODE = "mock"
        return self


    # 1. Application Settings
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    PROJECT_NAME: str = PROJECT_NAME
    VERSION: str = PROJECT_VERSION
    API_V1_STR: str = API_V1_STR
    DEBUG: bool = False
    SECRET_KEY: str = Field(
        default="SUPER_SECRET_PRODUCTION_KEY_MENTISCOPE_2026_CHANGE_IN_ENV",
        validation_alias=AliasChoices("SECRET_KEY", "JWT_SECRET"),
    )
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "*"]
    CONFIG_REPO_PATH: str = os.getenv("CONFIG_REPO_PATH", "config_repo")

    # 2. Database Settings (SQLAlchemy Async)
    POSTGRES_USER: str = "mentiscope_user"
    POSTGRES_PASSWORD: str = "mentiscope_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "mentiscope_db"
    DATABASE_URL: Optional[str] = None
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            # Normalize driver for asyncpg
            url = self.DATABASE_URL
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif url.startswith("sqlite://"):
                url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
            return url
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # 3. Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None

    @property
    def active_redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # 4. Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT_JSON: bool = True

    # 5. Security Settings
    ALGORITHM: str = ALGORITHM_HS256
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # 6. Provider Settings
    SPEECH_PROVIDER: str = "Whisper"
    LLM_PROVIDER: str = "openrouter"
    LLM_MODE: str = "mock"

    OPENROUTER_API_KEY: str = Field(
        default="",
        validation_alias=AliasChoices("OPENROUTER_API_KEY", "NVIDIA_API_KEY"),
    )
    OPENROUTER_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b:free"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"

    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-5-sonnet"

    # 7. Feature Flags
    ENABLE_ADAPTIVE_FOLLOWUP: bool = True
    ENABLE_LLM_EVALUATION: bool = True
    ENABLE_RESEARCH_ANALYTICS: bool = True
    STRICT_SECURITY_POLICIES: bool = True
    ENABLE_STREAMING_FOLLOWUP: bool = Field(
        default=False,
        validation_alias=AliasChoices("ENABLE_STREAMING_FOLLOWUP"),
    )
    STREAMING_ROLLOUT_PERCENTAGE: int = Field(
        default=0,
        validation_alias=AliasChoices("STREAMING_ROLLOUT_PERCENTAGE"),
    )
    STREAMING_TIMEOUT_SECONDS: int = Field(
        default=30,
        validation_alias=AliasChoices("STREAMING_TIMEOUT_SECONDS"),
    )
    LLM_EVALUATION_TIMEOUT_SECONDS: float = Field(
        default=5.0,
        validation_alias=AliasChoices("LLM_EVALUATION_TIMEOUT_SECONDS"),
    )



# Global settings singleton
settings = Settings()
