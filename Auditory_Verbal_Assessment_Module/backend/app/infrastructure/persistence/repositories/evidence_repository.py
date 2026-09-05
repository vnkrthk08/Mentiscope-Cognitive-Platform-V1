from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.evidence import Evidence
from app.infrastructure.persistence.models.orm_models import BehavioralEvidenceORM
from app.infrastructure.persistence.mappers.evidence_mapper import EvidenceMapper


class EvidenceRepository:
    """SQLAlchemy repository for persisting and listing Evidence entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, evidence: Evidence) -> Evidence:
        orm = EvidenceMapper.to_orm(evidence)
        existing = await self.session.get(BehavioralEvidenceORM, orm.id)
        if existing:
            existing.session_id = orm.session_id
            existing.prompt_id = orm.prompt_id
            existing.construct = orm.construct
            existing.quote = orm.quote
            existing.indicator_description = orm.indicator_description
            existing.confidence = orm.confidence
            existing.polarity = orm.polarity
            existing.evidence_type = orm.evidence_type
            existing.version += 1
            orm = existing
        else:
            self.session.add(orm)

        await self.session.flush()
        return EvidenceMapper.to_domain(orm)

    async def get_by_session_id(self, session_id: str) -> List[Evidence]:
        result = await self.session.execute(
            select(BehavioralEvidenceORM).where(
                BehavioralEvidenceORM.session_id == session_id, BehavioralEvidenceORM.is_deleted == False
            )
        )
        return [EvidenceMapper.to_domain(orm) for orm in result.scalars().all()]

    async def list_all(self) -> List[Evidence]:
        result = await self.session.execute(
            select(BehavioralEvidenceORM).where(BehavioralEvidenceORM.is_deleted == False)
        )
        return [EvidenceMapper.to_domain(orm) for orm in result.scalars().all()]
