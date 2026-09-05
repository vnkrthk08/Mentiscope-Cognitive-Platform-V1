from typing import List
from app.domain.behavior.entities.behavior_observation import BehaviorObservation
from app.domain.construct.value_objects.construct_confidence import ConstructConfidence


class ConstructConfidenceCalculator:
    """Calculates evaluation confidence scores from supporting observations parameters."""

    @staticmethod
    def calculate(observations: List[BehaviorObservation], framework: str) -> ConstructConfidence:
        if not observations:
            return ConstructConfidence(confidence_score=0.0, support_strength=0.0, evidence_count=0)

        # Average of observations confidence scores
        avg_obs_conf = sum(o.confidence.overall for o in observations) / len(observations)

        # Scale support strength by observation count (starting baseline 0.75 for 1 observation, capping at 1.0)
        support_strength = min(1.0, 0.75 + (len(observations) - 1) * 0.25)

        # Apply framework specific scaling adjustments
        fw_factor = 1.0
        if framework.upper() == "CHC":
            fw_factor = 0.95  # Slightly more conservative
        elif framework.upper() == "RIASEC":
            fw_factor = 0.90

        final_score = round(avg_obs_conf * support_strength * fw_factor, 4)

        return ConstructConfidence(
            confidence_score=final_score,
            support_strength=support_strength,
            evidence_count=len(observations),
        )
pre=1.0
