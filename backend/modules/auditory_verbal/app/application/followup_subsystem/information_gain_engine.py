"""
Module 4.5: Information Gain Engine (AIIS v20.1 Architecture).
Active-learning system that computes Expected Uncertainty Reduction (ΔU) across dimensions
(Reason, Risk, Stakeholders, Alternatives, Tradeoffs, Reflection).
Rule: Every follow-up question must measurably reduce uncertainty about the candidate's behavioral model.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.world_model import InterviewWorldModel


@dataclass(frozen=True)
class InformationGainResult:
    expected_gain_matrix: Dict[str, float] # Dimension -> Expected ΔU Score (0.0 to 1.0)
    recommended_dimension: str
    highest_gain_score: float
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expected_gain_matrix": {k: round(v, 2) for k, v in self.expected_gain_matrix.items()},
            "recommended_dimension": self.recommended_dimension,
            "highest_gain_score": round(self.highest_gain_score, 2),
            "rationale": self.rationale,
        }


class InformationGainEngine:
    """Module 4.5: Active Learning Expected Information Gain Engine."""

    IMPORTANCE_WEIGHTS: Dict[str, float] = {
        "Reason": 0.95,
        "Risk": 0.90,
        "Stakeholders": 0.85,
        "Alternatives": 0.78,
        "Tradeoffs": 0.72,
        "Reflection": 0.65,
    }

    def compute_information_gain(self, world_model: InterviewWorldModel) -> InformationGainResult:
        uncertainties = world_model.remaining_uncertainty
        gains: Dict[str, float] = {}

        already_asked = set(world_model.conversation_state.already_asked_objectives)

        for dim, uncertainty in uncertainties.items():
            importance = self.IMPORTANCE_WEIGHTS.get(dim, 0.70)

            # Check belief verification need for contradiction boost
            belief = world_model.beliefs_matrix.get(dim)
            belief_boost = 0.25 if (isinstance(belief, dict) and belief.get("needs_verification")) else 0.0

            # ΔU = Uncertainty * Importance + BeliefBoost
            delta_u = (uncertainty * importance) + belief_boost

            # Decay if already asked recently
            if dim in already_asked or f"ASK_{dim.upper()}" in already_asked:
                delta_u *= 0.40

            gains[dim] = round(delta_u, 3)

        # Find dimension with highest expected information gain
        top_dim = max(gains, key=gains.get) if gains else "Reason"
        top_score = gains.get(top_dim, 0.50)

        rat = f"Dimension '{top_dim}' yields maximum expected uncertainty reduction (ΔU = {top_score})."

        return InformationGainResult(
            expected_gain_matrix=gains,
            recommended_dimension=top_dim,
            highest_gain_score=top_score,
            rationale=rat,
        )
