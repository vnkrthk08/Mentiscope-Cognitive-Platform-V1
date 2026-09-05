"""
Module: Evidence Gain Estimator (v8).
Predicts whether continuing to probe the current target construct will yield meaningful new behavioral evidence.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.response_intelligence import ResponseAssessment
from app.application.followup_subsystem.closure_engine import ConstructSaturationMetrics
from app.application.followup_subsystem.conversation_state import ConversationState


@dataclass(frozen=True)
class EvidenceGainPrediction:
    expected_gain: float                 # 0.0 to 1.0
    target_construct: str
    should_switch_construct: bool
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expected_gain": self.expected_gain,
            "target_construct": self.target_construct,
            "should_switch_construct": self.should_switch_construct,
            "reason": self.reason,
        }


class EvidenceGainEstimator:
    """Predicts expected evidence gain per follow-up question and triggers construct switching when yield diminishes."""

    def predict_gain(
        self,
        assessment: ResponseAssessment,
        target_construct: str,
        construct_list: List[str],
        saturation_metrics: Optional[ConstructSaturationMetrics],
        state: ConversationState,
    ) -> EvidenceGainPrediction:

        current_probe_count = state.construct_probe_count.get(target_construct, 0)
        sat_score = saturation_metrics.saturation_score if saturation_metrics else 0.0

        # Base Gain Calculation
        base_gain = assessment.evidence_gain_score

        # Penalty for high probe count on same construct
        if current_probe_count >= 2:
            base_gain *= 0.40
        elif current_probe_count == 1:
            base_gain *= 0.75

        # Penalty for high saturation
        if sat_score >= 0.75:
            base_gain *= 0.20
        elif sat_score >= 0.50:
            base_gain *= 0.60

        expected_gain = round(base_gain, 2)

        # Threshold Rule: Switch construct if expected gain < 0.25 and alternative constructs exist
        should_switch = False
        next_construct = target_construct
        reason = f"Expected evidence gain is {expected_gain * 100:.0f}% for '{target_construct}'."

        if expected_gain < 0.25 and len(construct_list) > 1:
            alternatives = [c for c in construct_list if c != target_construct]
            if alternatives:
                should_switch = True
                next_construct = alternatives[0]
                reason = (
                    f"Evidence gain for '{target_construct}' diminished ({expected_gain * 100:.0f}%). "
                    f"Automatically switching target construct to '{next_construct}'."
                )

        return EvidenceGainPrediction(
            expected_gain=expected_gain,
            target_construct=next_construct,
            should_switch_construct=should_switch,
            reason=reason,
        )
