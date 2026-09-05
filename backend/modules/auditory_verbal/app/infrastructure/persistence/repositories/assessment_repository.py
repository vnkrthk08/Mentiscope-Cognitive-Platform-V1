import uuid
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.assessment_session import AssessmentSession
from app.infrastructure.persistence.models.orm_models import AssessmentSessionORM
from app.infrastructure.persistence.mappers.session_mapper import SessionMapper


class AssessmentRepository:
    """SQLAlchemy repository for persisting and retrieving AssessmentSession aggregates."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, entity_id: str) -> Optional[AssessmentSession]:
        result = await self.session.execute(
            select(AssessmentSessionORM).where(
                AssessmentSessionORM.id == entity_id, AssessmentSessionORM.is_deleted == False
            )
        )
        orm = result.scalars().first()
        return SessionMapper.to_domain(orm) if orm else None

    async def save(self, entity: AssessmentSession) -> AssessmentSession:
        orm = SessionMapper.to_orm(entity)
        existing = await self.session.get(AssessmentSessionORM, orm.id)
        if existing:
            existing.candidate_id = orm.candidate_id
            existing.scenario_id = orm.scenario_id
            existing.status = orm.status
            existing.current_stage = orm.current_stage
            existing.completed_stages = orm.completed_stages
            existing.metadata_json = orm.metadata_json
            existing.version += 1
            orm = existing
        else:
            self.session.add(orm)

        await self.session.flush()
        return SessionMapper.to_domain(orm)

    async def list_all(self) -> List[AssessmentSession]:
        result = await self.session.execute(
            select(AssessmentSessionORM).where(AssessmentSessionORM.is_deleted == False)
        )
        return [SessionMapper.to_domain(orm) for orm in result.scalars().all()]
