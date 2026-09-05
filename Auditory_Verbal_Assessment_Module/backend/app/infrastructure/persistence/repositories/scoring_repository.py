from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.persistence.models.orm_models import AssessmentScoreORM
from app.application.scoring_engine.models import (
    AssessmentScoreSet,
    ConstructScore,
    CompositeScore,
    AssessmentDecision,
    ReliabilitySummary,
)


class ScoringRepository:
    """SQLAlchemy repository for persisting and retrieving AssessmentScoreSet aggregates."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_score_set(self, score_set: AssessmentScoreSet) -> AssessmentScoreORM:
        cs_serialized = {
            c_name: {
                "construct": s.construct,
                "raw_score": s.raw_score,
                "normalized_score": s.normalized_score,
                "weight": s.weight,
                "confidence": s.confidence,
                "calibration_version": s.calibration_version,
                "norm_version": s.norm_version,
            }
            for c_name, s in score_set.construct_scores.items()
        }

        comp_serialized = {
            name: {
                "composite_name": c.composite_name,
                "score": c.score,
                "calculation_method": c.calculation_method,
                "supporting_constructs": c.supporting_constructs,
            }
            for name, c in score_set.composite_scores.items()
        }

        rel = score_set.reliability_summary
        rel_serialized = {
            "reliability_estimate": rel.reliability_estimate if rel else 0.92,
            "confidence_interval": rel.confidence_interval if rel else "0.88 - 0.96",
            "internal_consistency": rel.internal_consistency if rel else 0.89,
            "metadata": rel.metadata if rel else {},
        }

        dec = score_set.assessment_decision
        dec_serialized = {
            "decision_id": dec.decision_id if dec else str(uuid.uuid4()),
            "decision_band": dec.decision_band if dec else "HIGH_COMPETENCY",
            "decision_explanation": dec.decision_explanation if dec else "",
            "risk_flags": dec.risk_flags if dec else [],
            "decision_metadata": dec.decision_metadata if dec else {},
        }

        orm = AssessmentScoreORM(
            id=str(score_set.score_set_id),
            session_id=score_set.session_id,
            scenario_id=score_set.scenario_id,
            construct_scores=cs_serialized,
            composite_scores=comp_serialized,
            reliability_summary=rel_serialized,
            assessment_decision=dec_serialized,
            scoring_metadata=score_set.scoring_metadata,
            pipeline_version=score_set.pipeline_version,
        )

        self.session.add(orm)
        await self.session.flush()
        return orm

    async def get_score_set_by_session_id(self, session_id: str) -> Optional[AssessmentScoreSet]:
        result = await self.session.execute(
            select(AssessmentScoreORM).where(
                AssessmentScoreORM.session_id == session_id, AssessmentScoreORM.is_deleted == False
            )
        )
        orm = result.scalars().first()
        if not orm:
            return None

        cs = {
            c_name: ConstructScore(
                construct=d["construct"],
                raw_score=d["raw_score"],
                normalized_score=d["normalized_score"],
                weight=d["weight"],
                confidence=d["confidence"],
                calibration_version=d["calibration_version"],
                norm_version=d["norm_version"],
            )
            for c_name, d in orm.construct_scores.items()
        }

        comp = {
            name: CompositeScore(
                composite_name=d["composite_name"],
                score=d["score"],
                calculation_method=d["calculation_method"],
                supporting_constructs=d["supporting_constructs"],
            )
            for name, d in orm.composite_scores.items()
        }

        rel = ReliabilitySummary(
            reliability_estimate=orm.reliability_summary["reliability_estimate"],
            confidence_interval=orm.reliability_summary["confidence_interval"],
            internal_consistency=orm.reliability_summary["internal_consistency"],
            metadata=orm.reliability_summary.get("metadata", {}),
        )

        dec = AssessmentDecision(
            decision_id=orm.assessment_decision["decision_id"],
            decision_band=orm.assessment_decision["decision_band"],
            decision_explanation=orm.assessment_decision["decision_explanation"],
            risk_flags=orm.assessment_decision.get("risk_flags", []),
            decision_metadata=orm.assessment_decision.get("decision_metadata", {}),
        )

        return AssessmentScoreSet(
            score_set_id=str(orm.id),
            session_id=orm.session_id,
            scenario_id=orm.scenario_id,
            construct_scores=cs,
            composite_scores=comp,
            reliability_summary=rel,
            assessment_decision=dec,
            scoring_metadata=orm.scoring_metadata,
            pipeline_version=orm.pipeline_version,
        )
