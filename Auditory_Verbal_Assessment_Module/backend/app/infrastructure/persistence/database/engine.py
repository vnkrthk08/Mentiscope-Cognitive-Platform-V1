from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool
from app.core.config import settings

is_postgres = "postgresql" in settings.async_database_url

kwargs = {
    "echo": settings.DB_ECHO,
    "future": True,
}

if is_postgres:
    kwargs["pool_size"] = settings.DB_POOL_SIZE
    kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
elif "sqlite" in settings.async_database_url:
    kwargs["poolclass"] = StaticPool

engine = create_async_engine(settings.async_database_url, **kwargs)
