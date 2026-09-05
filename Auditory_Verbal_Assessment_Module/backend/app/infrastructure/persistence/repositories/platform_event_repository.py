from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.persistence.models.orm_models import PlatformEventORM


class PlatformEventRepository:
    """SQLAlchemy repository for auditing and persisting platform and domain events."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_event(self, event_name: str, correlation_id: str, payload: Dict[str, Any]) -> PlatformEventORM:
        orm = PlatformEventORM(
            event_name=event_name,
            correlation_id=correlation_id,
            payload=payload,
        )
        self.session.add(orm)
        await self.session.flush()
        return orm

    async def get_by_correlation_id(self, correlation_id: str) -> List[PlatformEventORM]:
        result = await self.session.execute(
            select(PlatformEventORM).where(
                PlatformEventORM.correlation_id == correlation_id, PlatformEventORM.is_deleted == False
            )
        )
        return list(result.scalars().all())
