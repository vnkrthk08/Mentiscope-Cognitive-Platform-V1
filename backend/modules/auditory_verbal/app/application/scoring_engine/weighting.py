from typing import Dict, Tuple, List
from app.application.scoring_engine.models import CompositeScore


class WeightingEngine:
    """Applies canonical construct contributions and computes overall weighted composite score aggregates.
    Enforces exact 1.5, 1.0, 1.0, 1.0 construct aggregation and (SQ1+SQ2+SQ3)/3 mathematical parity.
    """

    # Canonical construct measurement representation weights across the 3 speaking questions
    CANONICAL_SPEAKING_WEIGHTS: Dict[str, float] = {
        "DECISION_MAKING": 1.5,  # SQ1 Primary (1.0) + SQ2 Secondary (0.5)
        "ADAPTABILITY": 1.0,     # SQ2 Primary (1.0)
        "REASONING": 1.0,        # SQ3 Primary (1.0)
        "COMMUNICATION": 1.0,    # SQ1 Secondary (0.5) + SQ3 Secondary (0.5)
    }

    DEFAULT_WEIGHTS: Dict[str, float] = {
        "DECISION_MAKING": 1.5,
        "ADAPTABILITY": 1.0,
        "REASONING": 1.0,
        "COMMUNICATION": 1.0,
        "WORKING_MEMORY": 0.8,
    }

    def aggregate_speaking_construct_scores(
        self,
        sq1_score: float,
        sq2_score: float,
        sq3_score: float,
    ) -> Tuple[Dict[str, float], float]:
        """Calculates normalized construct scores and the overall Final Speaking Score.
        Returns:
            Tuple[Dict[construct_name, score_0_to_100], final_speaking_score_0_to_100]
        """
        # 1. Decision Making: SQ1 (1.0) + SQ2 (0.5) / 1.5
        dm_score = round(((sq1_score * 1.0) + (sq2_score * 0.5)) / 1.5, 2)

        # 2. Adaptability: SQ2 (1.0) / 1.0
        adapt_score = round(sq2_score * 1.0 / 1.0, 2)

        # 3. Reasoning: SQ3 (1.0) / 1.0
        reason_score = round(sq3_score * 1.0 / 1.0, 2)

        # 4. Communication: SQ1 (0.5) + SQ3 (0.5) / 1.0
        comm_score = round(((sq1_score * 0.5) + (sq3_score * 0.5)) / 1.0, 2)

        construct_scores: Dict[str, float] = {
            "DECISION_MAKING": dm_score,
            "ADAPTABILITY": adapt_score,
            "REASONING": reason_score,
            "COMMUNICATION": comm_score,
        }

        # Final Speaking Score = (1.5*DM + 1.0*AD + 1.0*RE + 1.0*COM) / 4.5 == (SQ1+SQ2+SQ3)/3
        weighted_sum = (
            (1.5 * dm_score)
            + (1.0 * adapt_score)
            + (1.0 * reason_score)
            + (1.0 * comm_score)
        )
        final_speaking_score = round(weighted_sum / 4.5, 2)

        return construct_scores, final_speaking_score

    def compute_weighted_composite(
        self, calibrated_scores: Dict[str, float]
    ) -> Tuple[Dict[str, float], CompositeScore]:
        """Applies construct weights and computes composite score for legacy/general scoring flow."""
        weighted_scores: Dict[str, float] = {}
        total_weighted = 0.0
        total_weight = 0.0

        for c_name, score in calibrated_scores.items():
            w = self.DEFAULT_WEIGHTS.get(c_name.upper(), 1.0)
            weighted_val = score * w
            weighted_scores[c_name] = w
            total_weighted += weighted_val
            total_weight += w

        comp_score = round(total_weighted / total_weight, 1) if total_weight > 0 else 0.0

        composite = CompositeScore(
            composite_name="OVERALL_SPEAKING_COMPOSITE",
            score=comp_score,
            calculation_method="WEIGHTED_AVERAGE",
            supporting_constructs=list(calibrated_scores.keys()),
        )

        return weighted_scores, composite
