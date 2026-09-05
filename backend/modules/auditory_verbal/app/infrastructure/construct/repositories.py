import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.construct.entities.construct_evaluation import ConstructEvaluation
from app.domain.construct.entities.construct_profile import ConstructProfile
from app.domain.construct.value_objects.construct_confidence import ConstructConfidence
from app.domain.construct.value_objects.construct_metadata import ConstructMetadata
from app.domain.construct.value_objects.evaluation_reference import EvaluationReference
from app.infrastructure.construct.orm_models import ConstructEvaluationORM, ConstructMetricORM


class ConstructMapper:
    @staticmethod
    def to_domain(orm: ConstructEvaluationORM) -> ConstructEvaluation:
        profiles = []
        for p in orm.construct_profiles:
            references = [
                EvaluationReference(reference_id=r["reference_id"], reference_type=r["reference_type"])
                for r in p["supporting_observations"]
            ]
            
            c = p["confidence"]
            conf = ConstructConfidence(
                confidence_score=c["confidence_score"],
                support_strength=c["support_strength"],
                evidence_count=c["evidence_count"],
            )

            profiles.append(
                ConstructProfile(
                    framework=p["framework"],
                    construct_name=p["construct_name"],
                    supporting_observations=references,
                    confidence=conf,
                    evaluation_summary=p["evaluation_summary"],
                )
            )

        m = orm.metadata_json
        meta = ConstructMetadata(
            framework_version=m["framework_version"],
            pipeline_version=m["pipeline_version"],
            generated_at=datetime.fromisoformat(m["generated_at"]) if isinstance(m["generated_at"], str) else m["generated_at"],
        )

        return ConstructEvaluation(
            evaluation_id=str(orm.id),
            behavior_evidence_id=str(orm.behavior_evidence_id),
            candidate_id=orm.candidate_id,
            assessment_id=str(orm.assessment_id),
            scenario_id=str(orm.scenario_id),
            construct_profiles=profiles,
            overall_evaluation_confidence=orm.overall_evaluation_confidence,
            metadata=meta,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(domain: ConstructEvaluation) -> ConstructEvaluationORM:
        profiles_payload = []
        for p in domain.construct_profiles:
            references = [
                {"reference_id": r.reference_id, "reference_type": r.reference_type}
                for r in p.supporting_observations
            ]
            
            profiles_payload.append(
                {
                    "framework": p.framework,
                    "construct_name": p.construct_name,
                    "supporting_observations": references,
                    "confidence": {
                        "confidence_score": p.confidence.confidence_score,
                        "support_strength": p.confidence.support_strength,
                        "evidence_count": p.confidence.evidence_count,
                    },
                    "evaluation_summary": p.evaluation_summary,
                }
            )

        meta_payload = {
            "framework_version": domain.metadata.framework_version,
            "pipeline_version": domain.metadata.pipeline_version,
            "generated_at": domain.metadata.generated_at.isoformat(),
        }

        return ConstructEvaluationORM(
            id=uuid.UUID(domain.evaluation_id),
            behavior_evidence_id=uuid.UUID(domain.behavior_evidence_id),
            candidate_id=domain.candidate_id,
            assessment_id=uuid.UUID(domain.assessment_id),
            scenario_id=uuid.UUID(domain.scenario_id),
            construct_profiles=profiles_payload,
            overall_evaluation_confidence=domain.overall_evaluation_confidence,
            metadata_json=meta_payload,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )


class ConstructRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, evaluation_id: str) -> Optional[ConstructEvaluation]:
        try:
            eid = uuid.UUID(evaluation_id)
        except ValueError:
            return None
        orm = await self.session.get(ConstructEvaluationORM, eid)
        return ConstructMapper.to_domain(orm) if orm else None

    async def get_by_evidence_id(self, evidence_id: str) -> List[ConstructEvaluation]:
        try:
            eid = uuid.UUID(evidence_id)
        except ValueError:
            return []
        result = await self.session.execute(
            select(ConstructEvaluationORM).where(ConstructEvaluationORM.behavior_evidence_id == eid)
        )
        return [ConstructMapper.to_domain(orm) for orm in result.scalars().all()]

    async def save(self, evaluation: ConstructEvaluation) -> ConstructEvaluation:
        orm = ConstructMapper.to_orm(evaluation)
        existing = await self.session.get(ConstructEvaluationORM, orm.id)
        if existing:
            existing.construct_profiles = orm.construct_profiles
            existing.overall_evaluation_confidence = orm.overall_evaluation_confidence
            existing.metadata_json = orm.metadata_json
            existing.updated_at = datetime.now(timezone.utc)
            orm = existing
        else:
            self.session.add(orm)
        await self.session.flush()
        return ConstructMapper.to_domain(orm)

    async def save_metric(self, metric_orm: ConstructMetricORM) -> None:
        self.session.add(metric_orm)
        await self.session.flush()
pre=1.0
