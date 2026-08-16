"""
ASAT â€“ Database Setup (SQLAlchemy Async + PostgreSQL)

Translated from: backend/db.js (MySQL mysql2/promise pool)

Same responsibilities:
  - Initialize connection pool
  - Create tables if they don't exist
  - Provide session factory for request-scoped DB access
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from modules.gsm.config import settings

logger = logging.getLogger("asat.database")


# â”€â”€ SQLAlchemy Base â”€â”€
class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# â”€â”€ Engine & Session Factory â”€â”€
engine = create_async_engine(
    settings.database_url,
    echo=False,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """
    Create all tables if they don't exist.
    Translated from db.js initDB() which runs CREATE TABLE IF NOT EXISTS
    for each table sequentially.
    """
    # Import schemas so Base.metadata knows about all tables
    import modules.gsm.schemas  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("[DB] PostgreSQL database initialized â€” all tables ensured.")


async def get_db():
    """
    FastAPI dependency: yields an async DB session per request.
    Equivalent to the original db.js run/get/all helpers but using
    SQLAlchemy's session pattern.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def shutdown_db():
    """Dispose of the engine connection pool on app shutdown."""
    await engine.dispose()
    logger.info("[DB] Connection pool disposed.")
