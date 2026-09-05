from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.assessment_report import AssessmentReport
from app.infrastructure.persistence.models.orm_models import AssessmentReportORM
from app.infrastructure.persistence.mappers.report_mapper import ReportMapper


class ReportRepository:
    """SQLAlchemy repository for persisting and retrieving AssessmentReport aggregates."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, report: AssessmentReport) -> AssessmentReport:
        orm = ReportMapper.to_orm(report)
        existing = await self.session.get(AssessmentReportORM, orm.id)
        if existing:
            existing.session_id = orm.session_id
            existing.candidate_id = orm.candidate_id
            existing.scenario_id = orm.scenario_id
            existing.overall_cognitive_index = orm.overall_cognitive_index
            existing.listening_metrics = orm.listening_metrics
            existing.speaking_metrics = orm.speaking_metrics
            existing.construct_scores = orm.construct_scores
            existing.evidence_summary = orm.evidence_summary
            existing.recommendations = orm.recommendations
            existing.version += 1
            orm = existing
        else:
            self.session.add(orm)

        await self.session.flush()
        return ReportMapper.to_domain(orm)

    async def get_by_session_id(self, session_id: str) -> Optional[AssessmentReport]:
        result = await self.session.execute(
            select(AssessmentReportORM).where(
                AssessmentReportORM.session_id == session_id, AssessmentReportORM.is_deleted == False
            )
        )
        orm = result.scalars().first()
        return ReportMapper.to_domain(orm) if orm else None
