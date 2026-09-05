from typing import Dict, List, Tuple, Optional, Any
from app.application.construct_engine.models import ConstructEvaluationSet


class ConstructScoreCalculator:
    """Calculates deterministic scores for questions, rubrics, and construct evaluation sets.
    Enforces canonical 70/30 question formula and 18.4 maximum weighted indicator score.
    """

    MAX_WEIGHTED_INDICATOR_SCORE: float = 18.4
    RUBRIC_WEIGHT: float = 0.70
    FLUENCY_WEIGHT: float = 0.30

    def calculate_rubric_score(self, indicator_scores: List[Tuple[int, float]]) -> float:
        """Calculates canonical RubricScore from (score, weight) pairs.
        RubricScore = (Sum(score_i * weight_i) / 18.4) * 100
        """
        weighted_sum = sum(score * weight for score, weight in indicator_scores)
        raw_pct = (weighted_sum / self.MAX_WEIGHTED_INDICATOR_SCORE) * 100.0
        return round(min(100.0, max(0.0, raw_pct)), 2)

    def calculate_question_score(self, rubric_score: float, fluency_score: float) -> float:
        """Calculates canonical QuestionScore from 70% RubricScore + 30% FluencyScore.
        QuestionScore = 0.70 * RubricScore + 0.30 * FluencyScore
        """
        q_score = (self.RUBRIC_WEIGHT * rubric_score) + (self.FLUENCY_WEIGHT * fluency_score)
        return round(min(100.0, max(0.0, q_score)), 2)

    def calculate_raw_scores(self, evaluation_set: ConstructEvaluationSet) -> Dict[str, float]:
        """Calculates deterministic raw scores from ConstructEvaluationSet confidence & items."""
        raw_scores: Dict[str, float] = {}

        for item in evaluation_set.construct_evaluations:
            c_name = item.construct_name.upper()
            base_raw = item.evaluation_confidence * 100.0
            raw_scores[c_name] = round(min(100.0, max(0.0, base_raw)), 2)

        return raw_scores
