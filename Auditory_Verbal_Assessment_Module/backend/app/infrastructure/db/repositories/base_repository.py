from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces.repository import IRepository

T = TypeVar("T")
ID = TypeVar("ID")


class BaseRepository(IRepository[T, ID], Generic[T, ID]):
    """Base generic SQLAlchemy repository implementation for PostgreSQL persistence."""

    def __init__(self, model_cls: Type[T], session: AsyncSession):
        self.model_cls = model_cls
        self.session = session

    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        result = await self.session.execute(
            select(self.model_cls).where(getattr(self.model_cls, "id") == entity_id)
        )
        return result.scalars().first()

    async def list_all(self) -> List[T]:
        result = await self.session.execute(select(self.model_cls))
        return list(result.scalars().all())

    async def save(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity_id: ID) -> bool:
        entity = await self.get_by_id(entity_id)
        if entity:
            await self.session.delete(entity)
            await self.session.flush()
            return True
        return False
