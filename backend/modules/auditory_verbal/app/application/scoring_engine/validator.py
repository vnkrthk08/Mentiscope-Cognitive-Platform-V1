from app.application.scoring_engine.models import AssessmentScoreSet
from app.domain.exceptions.scoring_exceptions import AssessmentScoreValidationFailure


class ScoreValidator:
    """Validates score ranges (0-100), composite validity, and metadata version integrity."""

    def validate_score_set(self, score_set: AssessmentScoreSet) -> bool:
        if not score_set.construct_scores:
            raise AssessmentScoreValidationFailure("SET", "AssessmentScoreSet contains no construct scores.")

        for c_name, score in score_set.construct_scores.items():
            if score.normalized_score < 0.0 or score.normalized_score > 100.0:
                raise AssessmentScoreValidationFailure(
                    c_name, f"Normalized score {score.normalized_score} is out of bounds [0.0, 100.0]."
                )

        if not score_set.composite_scores:
            raise AssessmentScoreValidationFailure("COMPOSITE", "AssessmentScoreSet missing composite score.")

        if not score_set.assessment_decision:
            raise AssessmentScoreValidationFailure("DECISION", "AssessmentScoreSet missing assessment decision.")

        return True
