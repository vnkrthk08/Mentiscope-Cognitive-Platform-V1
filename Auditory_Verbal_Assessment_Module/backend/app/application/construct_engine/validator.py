from app.application.construct_engine.models import ConstructEvaluationSet
from app.domain.exceptions.construct_exceptions import EvaluationValidationFailure


class ConstructValidator:
    """Validates ConstructEvaluationSet completeness, supporting evidence references, and confidence thresholds."""

    def validate_evaluation_set(
        self, evaluation_set: ConstructEvaluationSet, min_confidence: float = 0.5
    ) -> bool:
        if not evaluation_set.construct_evaluations:
            raise EvaluationValidationFailure("SET", "ConstructEvaluationSet contains no evaluations.")

        for item in evaluation_set.construct_evaluations:
            if item.evaluation_confidence < min_confidence:
                raise EvaluationValidationFailure(
                    item.evaluation_id,
                    f"Evaluation confidence ({item.evaluation_confidence}) below threshold of {min_confidence}.",
                )
            if not item.behavioral_summary or not item.behavioral_summary.strip():
                raise EvaluationValidationFailure(item.evaluation_id, "Evaluation missing behavioral summary.")

        return True
