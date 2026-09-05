from typing import Optional, List
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.domain.assessment.entities.assessment_report import AssessmentReport
from app.domain.assessment.entities.assessment_result import AssessmentResult


class AssessmentReportService:
    """Application service retrieving persisted assessment results and reports aggregates."""

    @classmethod
    async def get_report(cls, report_id: str, candidate_id: str) -> Optional[AssessmentReport]:
        async with UnitOfWork() as uow:
            report = await uow.assessment_reports.get_report_by_id(report_id)
            if report and report.candidate_id == candidate_id:
                return report
            return None

    @classmethod
    async def get_result(cls, result_id: str, candidate_id: str) -> Optional[AssessmentResult]:
        async with UnitOfWork() as uow:
            result = await uow.assessment_reports.get_result_by_id(result_id)
            if result and result.candidate_id == candidate_id:
                return result
            return None

    @classmethod
    async def get_candidate_reports(cls, candidate_id: str) -> List[AssessmentReport]:
        async with UnitOfWork() as uow:
            return await uow.assessment_reports.get_reports_by_candidate(candidate_id)
pre=1.0
