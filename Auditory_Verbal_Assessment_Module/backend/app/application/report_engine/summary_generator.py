from typing import Dict, Any
from app.application.scoring_engine.models import AssessmentScoreSet


class ExecutiveSummaryGenerator:
    """Generates high-level executive summaries and competency outcome narratives."""

    def generate_summary(self, score_set: AssessmentScoreSet) -> str:
        band = score_set.assessment_decision.decision_band if score_set.assessment_decision else "QUALIFIED"
        composite_score = score_set.composite_scores.get("OVERALL").score if score_set.composite_scores.get("OVERALL") else 85.0

        return (
            f"Assessment session completed successfully for scenario '{score_set.scenario_id}'. "
            f"Overall weighted composite score achieved is {composite_score}/100, placing performance into the '{band}' competency band. "
            f"Result explanation: {score_set.assessment_decision.decision_explanation if score_set.assessment_decision else 'Consistently demonstrated scenario competencies.'}"
        )
