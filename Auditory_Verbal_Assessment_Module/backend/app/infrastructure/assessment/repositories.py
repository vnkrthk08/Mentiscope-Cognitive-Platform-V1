import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.assessment.entities.scoring_policy import ScoringPolicy
from app.domain.assessment.entities.assessment_result import AssessmentResult
from app.domain.assessment.entities.assessment_report import AssessmentReport
from app.domain.assessment.entities.framework_result import FrameworkResult
from app.domain.assessment.entities.score_breakdown import ScoreBreakdown
from app.domain.assessment.entities.assessment_summary import AssessmentSummary
from app.domain.assessment.value_objects.scoring_metadata import ScoringMetadata
from app.domain.assessment.value_objects.report_metadata import ReportMetadata
from app.domain.assessment.value_objects.score_reference import ScoreReference
from app.infrastructure.assessment.orm_models import AssessmentResultORM, AssessmentReportORM, ScoringPolicyORM, AssessmentMetricORM


class AssessmentMapper:
    @staticmethod
    def to_result_domain(orm: AssessmentResultORM) -> AssessmentResult:
        fw_results = []
        for f in orm.framework_results:
            breakdowns = []
            for cb in f["construct_results"]:
                refs = [
                    ScoreReference(
                        construct_evaluation_id=r["construct_evaluation_id"],
                        behavior_evidence_id=r["behavior_evidence_id"],
                        prompt_execution_id=r["prompt_execution_id"],
                        transcript_id=r["transcript_id"],
                    )
                    for r in cb["references"]
                ]
                breakdowns.append(
                    ScoreBreakdown(
                        construct=cb["construct"],
                        raw_score=cb["raw_score"],
                        normalized_score=cb["normalized_score"],
                        confidence=cb["confidence"],
                        support_strength=cb["support_strength"],
                        evidence_count=cb["evidence_count"],
                        references=refs,
                    )
                )

            fw_results.append(
                FrameworkResult(
                    framework=f["framework"],
                    raw_score=f["raw_score"],
                    normalized_score=f["normalized_score"],
                    confidence=f["confidence"],
                    construct_results=breakdowns,
                    supporting_evidence_count=f["supporting_evidence_count"],
                    policy_version=f["policy_version"],
                    summary=f["summary"],
                )
            )

        sm = orm.scoring_metadata
        meta = ScoringMetadata(
            framework_version=sm["framework_version"],
            scoring_policy_version=sm["scoring_policy_version"],
            pipeline_version=sm["pipeline_version"],
            engine_version=sm["engine_version"],
            generated_at=datetime.fromisoformat(sm["generated_at"]) if isinstance(sm["generated_at"], str) else sm["generated_at"],
        )

        return AssessmentResult(
            result_id=str(orm.id),
            candidate_id=orm.candidate_id,
            assessment_id=str(orm.assessment_id),
            construct_evaluation_id=str(orm.construct_evaluation_id),
            framework_results=fw_results,
            overall_scores=orm.overall_scores,
            overall_confidence=orm.overall_confidence,
            scoring_metadata=meta,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_result_orm(domain: AssessmentResult) -> AssessmentResultORM:
        fw_payload = []
        for f in domain.framework_results:
            breakdowns = []
            for cb in f.construct_results:
                refs = [
                    {
                        "construct_evaluation_id": r.construct_evaluation_id,
                        "behavior_evidence_id": r.behavior_evidence_id,
                        "prompt_execution_id": r.prompt_execution_id,
                        "transcript_id": r.transcript_id,
                    }
                    for r in cb.references
                ]
                breakdowns.append(
                    {
                        "construct": cb.construct,
                        "raw_score": cb.raw_score,
                        "normalized_score": cb.normalized_score,
                        "confidence": cb.confidence,
                        "support_strength": cb.support_strength,
                        "evidence_count": cb.evidence_count,
                        "references": refs,
                    }
                )

            fw_payload.append(
                {
                    "framework": f.framework,
                    "raw_score": f.raw_score,
                    "normalized_score": f.normalized_score,
                    "confidence": f.confidence,
                    "construct_results": breakdowns,
                    "supporting_evidence_count": f.supporting_evidence_count,
                    "policy_version": f.policy_version,
                    "summary": f.summary,
                }
            )

        meta_payload = {
            "framework_version": domain.scoring_metadata.framework_version,
            "scoring_policy_version": domain.scoring_metadata.scoring_policy_version,
            "pipeline_version": domain.scoring_metadata.pipeline_version,
            "engine_version": domain.scoring_metadata.engine_version,
            "generated_at": domain.scoring_metadata.generated_at.isoformat(),
        }

        return AssessmentResultORM(
            id=uuid.UUID(domain.result_id),
            candidate_id=domain.candidate_id,
            assessment_id=uuid.UUID(domain.assessment_id),
            construct_evaluation_id=uuid.UUID(domain.construct_evaluation_id),
            framework_results=fw_payload,
            overall_scores=domain.overall_scores,
            overall_confidence=domain.overall_confidence,
            scoring_metadata=meta_payload,
            created_at=domain.created_at,
        )

    @staticmethod
    def to_report_domain(orm: AssessmentReportORM) -> AssessmentReport:
        fw_results = []
        for f in orm.framework_results:
            breakdowns = []
            for cb in f["construct_results"]:
                refs = [
                    ScoreReference(
                        construct_evaluation_id=r["construct_evaluation_id"],
                        behavior_evidence_id=r["behavior_evidence_id"],
                        prompt_execution_id=r["prompt_execution_id"],
                        transcript_id=r["transcript_id"],
                    )
                    for r in cb["references"]
                ]
                breakdowns.append(
                    ScoreBreakdown(
                        construct=cb["construct"],
                        raw_score=cb["raw_score"],
                        normalized_score=cb["normalized_score"],
                        confidence=cb["confidence"],
                        support_strength=cb["support_strength"],
                        evidence_count=cb["evidence_count"],
                        references=refs,
                    )
                )

            fw_results.append(
                FrameworkResult(
                    framework=f["framework"],
                    raw_score=f["raw_score"],
                    normalized_score=f["normalized_score"],
                    confidence=f["confidence"],
                    construct_results=breakdowns,
                    supporting_evidence_count=f["supporting_evidence_count"],
                    policy_version=f["policy_version"],
                    summary=f["summary"],
                )
            )

        sm = orm.assessment_summary
        summary = AssessmentSummary(
            framework_overview=sm["framework_overview"],
            strengths=sm["strengths"],
            areas_for_improvement=sm["areas_for_improvement"],
            confidence_summary=sm["confidence_summary"],
            overall_observations=sm["overall_observations"],
        )

        rm = orm.report_metadata
        meta = ReportMetadata(
            generated_by=rm["generated_by"],
            pipeline_version=rm["pipeline_version"],
            engine_version=rm["engine_version"],
            report_version=rm["report_version"],
            language=rm["language"],
            generated_at=datetime.fromisoformat(rm["generated_at"]) if isinstance(rm["generated_at"], str) else rm["generated_at"],
        )

        return AssessmentReport(
            report_id=str(orm.id),
            assessment_result_id=str(orm.assessment_result_id),
            candidate_id=orm.candidate_id,
            assessment_id=str(orm.assessment_id),
            assessment_summary=summary,
            framework_results=fw_results,
            report_metadata=meta,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_report_orm(domain: AssessmentReport) -> AssessmentReportORM:
        fw_payload = []
        for f in domain.framework_results:
            breakdowns = []
            for cb in f.construct_results:
                refs = [
                    {
                        "construct_evaluation_id": r.construct_evaluation_id,
                        "behavior_evidence_id": r.behavior_evidence_id,
                        "prompt_execution_id": r.prompt_execution_id,
                        "transcript_id": r.transcript_id,
                    }
                    for r in cb.references
                ]
                breakdowns.append(
                    {
                        "construct": cb.construct,
                        "raw_score": cb.raw_score,
                        "normalized_score": cb.normalized_score,
                        "confidence": cb.confidence,
                        "support_strength": cb.support_strength,
                        "evidence_count": cb.evidence_count,
                        "references": refs,
                    }
                )

            fw_payload.append(
                {
                    "framework": f.framework,
                    "raw_score": f.raw_score,
                    "normalized_score": f.normalized_score,
                    "confidence": f.confidence,
                    "construct_results": breakdowns,
                    "supporting_evidence_count": f.supporting_evidence_count,
                    "policy_version": f.policy_version,
                    "summary": f.summary,
                }
            )

        sm = domain.assessment_summary
        summary_payload = {
            "framework_overview": sm.framework_overview,
            "strengths": sm.strengths,
            "areas_for_improvement": sm.areas_for_improvement,
            "confidence_summary": sm.confidence_summary,
            "overall_observations": sm.overall_observations,
        }

        meta_payload = {
            "generated_by": domain.report_metadata.generated_by,
            "pipeline_version": domain.report_metadata.pipeline_version,
            "engine_version": domain.report_metadata.engine_version,
            "report_version": domain.report_metadata.report_version,
            "language": domain.report_metadata.language,
            "generated_at": domain.report_metadata.generated_at.isoformat(),
        }

        return AssessmentReportORM(
            id=uuid.UUID(domain.report_id),
            assessment_result_id=uuid.UUID(domain.assessment_result_id),
            candidate_id=domain.candidate_id,
            assessment_id=uuid.UUID(domain.assessment_id),
            assessment_summary=summary_payload,
            framework_results=fw_payload,
            report_metadata=meta_payload,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )


class AssessmentReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_result_by_id(self, result_id: str) -> Optional[AssessmentResult]:
        try:
            rid = uuid.UUID(result_id)
        except ValueError:
            return None
        orm = await self.session.get(AssessmentResultORM, rid)
        return AssessmentMapper.to_result_domain(orm) if orm else None

    async def get_report_by_id(self, report_id: str) -> Optional[AssessmentReport]:
        try:
            rid = uuid.UUID(report_id)
        except ValueError:
            return None
        orm = await self.session.get(AssessmentReportORM, rid)
        return AssessmentMapper.to_report_domain(orm) if orm else None

    async def get_reports_by_candidate(self, candidate_id: str) -> List[AssessmentReport]:
        result = await self.session.execute(
            select(AssessmentReportORM).where(AssessmentReportORM.candidate_id == candidate_id)
        )
        return [AssessmentMapper.to_report_domain(orm) for orm in result.scalars().all()]

    async def save_result(self, res: AssessmentResult) -> AssessmentResult:
        orm = AssessmentMapper.to_result_orm(res)
        existing = await self.session.get(AssessmentResultORM, orm.id)
        if not existing:
            self.session.add(orm)
        await self.session.flush()
        return AssessmentMapper.to_result_domain(orm)

    async def save_report(self, rep: AssessmentReport) -> AssessmentReport:
        orm = AssessmentMapper.to_report_orm(rep)
        existing = await self.session.get(AssessmentReportORM, orm.id)
        if existing:
            existing.assessment_summary = orm.assessment_summary
            existing.framework_results = orm.framework_results
            existing.report_metadata = orm.report_metadata
            existing.updated_at = datetime.now(timezone.utc)
            orm = existing
        else:
            self.session.add(orm)
        await self.session.flush()
        return AssessmentMapper.to_report_domain(orm)

    async def save_metric(self, metric_orm: AssessmentMetricORM) -> None:
        self.session.add(metric_orm)
        await self.session.flush()

    # Scoring Policy Helpers
    async def get_policy_by_framework(self, framework: str) -> Optional[ScoringPolicy]:
        res = await self.session.execute(
            select(ScoringPolicyORM)
            .where(ScoringPolicyORM.framework == framework.upper())
            .where(ScoringPolicyORM.is_active == True)
        )
        orm = res.scalars().first()
        if not orm:
            return None
        return ScoringPolicy(
            policy_id=orm.id,
            framework=orm.framework,
            policy_name=orm.policy_name,
            version=orm.version,
            weight_configuration=orm.weight_configuration,
            normalization_method=orm.normalization_method,
            confidence_method=orm.confidence_method,
            is_active=orm.is_active,
            created_at=orm.created_at,
        )

    async def save_policy(self, policy: ScoringPolicy) -> None:
        orm = ScoringPolicyORM(
            id=policy.policy_id,
            framework=policy.framework.upper(),
            policy_name=policy.policy_name,
            version=policy.version,
            weight_configuration=policy.weight_configuration,
            normalization_method=policy.normalization_method,
            confidence_method=policy.confidence_method,
            is_active=policy.is_active,
            created_at=policy.created_at,
        )
        existing = await self.session.get(ScoringPolicyORM, orm.id)
        if not existing:
            self.session.add(orm)
            await self.session.flush()
pre=1.0
