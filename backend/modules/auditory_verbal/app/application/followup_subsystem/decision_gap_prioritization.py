"""
Module 5: Information Need & Belief Prioritization Engine (AIIS v18.0.0 Architecture).
Calculates Weighted Priority Score combining Dimension Importance, Evidence Deficit,
Belief Confidence Deficit, and Belief Verification Need.
Priority Score = 0.35 * Importance + 0.25 * SufficiencyDeficit + 0.20 * BeliefDeficit + 0.10 * Novelty + 0.10 * ConfidenceDeficit (+ Contradiction Bonus).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.evidence_sufficiency_engine import DimensionSufficiency, EvidenceLevel
from app.application.followup_subsystem.behavioral_belief_engine import BehaviorBelief, BeliefStatus
from app.application.followup_subsystem.conversation_manager import ConversationState


@dataclass(frozen=True)
class PrioritizedInformationNeed:
    objective: str             # ASK_REASON, ASK_RISK, ASK_STAKEHOLDER, ASK_ALTERNATIVE, ASK_TRADEOFF, ASK_REFLECTION, CONFIRM_BELIEF, VERIFY_CONTEXT
    priority_score: float      # Weighted Priority Score (0.0 to 1.0+)
    missing_dimension: str     # Reason, Risk, Stakeholders, Alternatives, Tradeoffs, Reflection
    sufficiency_level: str     # MISSING, WEAK, PARTIAL, STRONG, SATURATED
    rationale: str
    belief_hypothesis: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective": self.objective,
            "priority_score": round(self.priority_score, 2),
            "missing_dimension": self.missing_dimension,
            "sufficiency_level": self.sufficiency_level,
            "rationale": self.rationale,
            "belief_hypothesis": self.belief_hypothesis,
        }


class DecisionGapPrioritizationEngine:
    """Module 5: Weighted Multi-Factor Priority Ranking Engine."""

    IMPORTANCE: Dict[str, float] = {
        "Reason": 0.95,
        "Risk": 0.90,
        "Stakeholders": 0.85,
        "Alternatives": 0.78,
        "Tradeoffs": 0.72,
        "Reflection": 0.65,
    }

    OBJ_MAP: Dict[str, str] = {
        "Reason": "ASK_REASON",
        "Risk": "ASK_RISK",
        "Stakeholders": "ASK_STAKEHOLDER",
        "Alternatives": "ASK_ALTERNATIVE",
        "Tradeoffs": "ASK_TRADEOFF",
        "Reflection": "ASK_REFLECTION",
    }

    CONSTRUCT_DIMENSION_MAP: Dict[str, str] = {
        "DECISION_MAKING": "Reason",
        "SAFETY_AWARENESS": "Risk",
        "RISK_MITIGATION": "Risk",
        "COMMUNICATION": "Stakeholders",
        "STAKEHOLDER_ALIGNMENT": "Stakeholders",
        "TRADE_OFF_ANALYSIS": "Tradeoffs",
        "ETHICAL_REASONING": "Risk",
        "RESOURCE_MANAGEMENT": "Tradeoffs",
        "PRIORITIZATION": "Tradeoffs",
        "SELF_REFLECTION": "Reflection",
        "ADAPTABILITY": "Alternatives",
        "STRATEGIC_THINKING": "Alternatives",
        "LEADERSHIP": "Stakeholders",
    }

    def prioritize_gaps(
        self,
        sufficiency_matrix: Dict[str, DimensionSufficiency],
        beliefs_matrix: Dict[str, BehaviorBelief],
        state: ConversationState,
        target_construct: Optional[str] = None,
        target_constructs: Optional[List[str]] = None,
    ) -> List[PrioritizedInformationNeed]:

        needs: List[PrioritizedInformationNeed] = []
        already_asked = set(state.already_asked_objectives)

        target_dims = set()
        if target_construct:
            tc_upper = target_construct.upper()
            mapped = self.CONSTRUCT_DIMENSION_MAP.get(tc_upper, target_construct)
            target_dims.add(mapped)
        if target_constructs:
            for tc in target_constructs:
                tc_upper = tc.upper()
                mapped = self.CONSTRUCT_DIMENSION_MAP.get(tc_upper, tc)
                target_dims.add(mapped)

        for dim_name, importance in self.IMPORTANCE.items():
            suff = sufficiency_matrix.get(dim_name)
            belief = beliefs_matrix.get(dim_name)

            if not suff:
                continue

            # Calculate deficits
            suff_deficit = suff.deficit
            belief_deficit = (1.0 - belief.confidence) if belief else 0.80
            conf_deficit = (1.0 - suff.score)

            # Contradiction Bonus if belief needs verification
            contra_bonus = 0.25 if (belief and belief.needs_verification) else 0.0
            novelty = 1.0 if state.turn_number == 1 else 0.80

            # Weak reasoning deficit bonus (probing partially articulated reasoning is high priority)
            weak_bonus = 0.20 if (suff.level == EvidenceLevel.WEAK or (0.0 < suff.score < 0.60)) else 0.0

            # Target construct alignment bonus
            construct_bonus = 0.35 if dim_name in target_dims else 0.0

            # Weighted Formula: 0.35*Importance + 0.25*SuffDeficit + 0.20*BeliefDeficit + 0.10*Novelty + 0.10*ConfDeficit + ContraBonus + WeakBonus + ConstructBonus
            score = (
                0.35 * importance
                + 0.25 * suff_deficit
                + 0.20 * belief_deficit
                + 0.10 * novelty
                + 0.10 * conf_deficit
                + contra_bonus
                + weak_bonus
                + construct_bonus
            )

            # Objective selection: Preserve true primary objective for each dimension
            if belief and belief.needs_verification:
                obj_name = "VERIFY_CONTEXT"
                rat = f"Belief for '{dim_name}' is UNCERTAIN (contradiction/contextual shift detected). Verification priority."
                score += 0.20
            elif belief and belief.status in (BeliefStatus.LIKELY, BeliefStatus.VERIFIED) and state.turn_number >= 3 and dim_name == "Reason":
                obj_name = "CONFIRM_BELIEF"
                rat = f"Hypothesis for '{dim_name}' is mature ({belief.status.value}). Confirmation probe."
                score += 0.10
            else:
                obj_name = self.OBJ_MAP.get(dim_name, "ASK_REASON")
                rat = f"Dimension '{dim_name}' evidence sufficiency level is {suff.level.value} (score {suff.score}). Objective: {obj_name}."

            # Apply decay if already asked
            if obj_name in already_asked:
                score *= 0.35

            needs.append(PrioritizedInformationNeed(
                objective=obj_name,
                priority_score=round(score, 2),
                missing_dimension=dim_name,
                sufficiency_level=suff.level.value,
                rationale=rat,
                belief_hypothesis=belief.statement if belief else None,
            ))

        # Sort descending by priority score
        needs.sort(key=lambda x: x.priority_score, reverse=True)
        return needs
