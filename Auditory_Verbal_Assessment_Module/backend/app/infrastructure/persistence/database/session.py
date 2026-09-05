from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from app.infrastructure.persistence.database.engine import engine

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
