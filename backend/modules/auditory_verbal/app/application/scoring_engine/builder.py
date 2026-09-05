from typing import Dict
from app.application.scoring_engine.models import (
    AssessmentScoreSet,
    ConstructScore,
    CompositeScore,
    AssessmentDecision,
    ReliabilitySummary,
)


class AssessmentScoreBuilder:
    """Transforms individual construct scores and decision objects into immutable AssessmentScoreSet aggregates."""

    def build_score_set(
        self,
        session_id: str,
        scenario_id: str,
        construct_scores: Dict[str, ConstructScore],
        composite: CompositeScore,
        decision: AssessmentDecision,
        reliability: ReliabilitySummary,
    ) -> AssessmentScoreSet:
        return AssessmentScoreSet(
            session_id=session_id,
            scenario_id=scenario_id,
            construct_scores=construct_scores,
            composite_scores={"OVERALL": composite, composite.composite_name: composite},
            assessment_decision=decision,
            reliability_summary=reliability,

            scoring_metadata={
                "scoring_pipeline": "PSDE_V1",
                "calibration_version": "1.0.0",
                "norm_version": "1.0.0",
            },
        )
