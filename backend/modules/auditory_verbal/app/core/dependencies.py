from typing import AsyncGenerator, Optional, Any
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings, settings
from app.core.database import get_db
from app.core.redis import redis_client
from app.core.logging import logger
from app.core.constants import HEADER_REQUEST_ID, HEADER_CORRELATION_ID


async def get_settings_dep() -> Settings:
    """Dependency injection providing application Settings."""
    return settings


async def get_db_session(session: AsyncSession = Depends(get_db)) -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection providing async SQLAlchemy session."""
    yield session


async def get_redis_client() -> Optional[Any]:
    """Dependency injection providing async Redis client."""
    return redis_client


async def get_correlation_id(
    request_id: Optional[str] = Header(None, alias=HEADER_REQUEST_ID),
    correlation_id: Optional[str] = Header(None, alias=HEADER_CORRELATION_ID),
) -> str:
    """Dependency extracting request or correlation ID."""
    return correlation_id or request_id or "ANONYMOUS"
