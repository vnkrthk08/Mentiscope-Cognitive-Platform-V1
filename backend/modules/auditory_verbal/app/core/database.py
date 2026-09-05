from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.persistence.database.base import Base
from app.infrastructure.persistence.database.engine import engine
from app.infrastructure.persistence.database.session import AsyncSessionLocal
from app.core.logging import logger


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency producing async SQLAlchemy session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_health() -> bool:
    """Verifies database connectivity with SELECT 1 ping."""
    try:
        from sqlalchemy import text

        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.warning(f"[DB HEALTH CHECK] Database health check failed: {str(e)}")
        return False
