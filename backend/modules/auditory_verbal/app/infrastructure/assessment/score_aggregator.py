from typing import List, Dict
from app.domain.assessment.entities.framework_result import FrameworkResult


class ScoreAggregator:
    """Aggregates multiple framework results into overall assessment scores and confidence values."""

    @staticmethod
    def aggregate_scores(framework_results: List[FrameworkResult]) -> Dict[str, float]:
        scores = {}
        for r in framework_results:
            scores[r.framework] = r.normalized_score
        return scores

    @staticmethod
    def aggregate_confidence(framework_results: List[FrameworkResult]) -> float:
        if not framework_results:
            return 0.0
        # Average of all framework confidence scores
        return sum(r.confidence for r in framework_results) / len(framework_results)
pre=1.0
