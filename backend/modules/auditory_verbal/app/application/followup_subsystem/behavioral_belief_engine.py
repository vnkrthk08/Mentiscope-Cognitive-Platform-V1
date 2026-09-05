"""
Module 3.7: Behavioral Belief Engine (AIIS v18.0.0 Architecture).
Maintains explicit Behavioral Belief Hypotheses about candidate decision-making principles.
Tracks belief status progression (UNKNOWN -> EMERGING -> LIKELY -> VERIFIED -> UNCERTAIN)
and flags beliefs needing confirmation or contradiction verification.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.behavioral_consistency_engine import BehaviorObservation, BehaviorState
from app.application.followup_subsystem.interview_understanding import CandidateDecisionData


class BeliefStatus(str, Enum):
    UNKNOWN = "UNKNOWN"         # Confidence < 0.30 — No hypothesis formed
    EMERGING = "EMERGING"       # Confidence 0.30-0.49 — Initial pattern forming (1-2 items)
    LIKELY = "LIKELY"           # Confidence 0.50-0.74 — 3+ consistent evidence items
    VERIFIED = "VERIFIED"       # Confidence >= 0.75 — 4+ consistent items, zero contradictions
    UNCERTAIN = "UNCERTAIN"     # Contradiction detected, needs verification


@dataclass
class BehaviorBelief:
    id: str
    dimension: str
    statement: str
    confidence: float = 0.20
    supporting_evidence_count: int = 0
    contradicting_evidence_count: int = 0
    status: BeliefStatus = BeliefStatus.UNKNOWN
    needs_verification: bool = False
    last_updated_turn: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "dimension": self.dimension,
            "statement": self.statement,
            "confidence": round(self.confidence, 2),
            "supporting_evidence_count": self.supporting_evidence_count,
            "contradicting_evidence_count": self.contradicting_evidence_count,
            "status": self.status.value,
            "needs_verification": self.needs_verification,
            "last_updated_turn": self.last_updated_turn,
        }


class BehavioralBeliefEngine:
    """Module 3.7: Maintains active belief hypotheses and Bayesian-style belief confidence updates."""

    _DEFAULT_STATEMENTS: Dict[str, str] = {
        "Reason": "Candidate prioritizes human safety and risk reduction over speed.",
        "Risk": "Candidate systematically evaluates operational failure modes before taking action.",
        "Stakeholders": "Candidate prefers collaborative consultation with teammates when time permits.",
        "Alternatives": "Candidate explores strategic alternatives under resource constraints.",
        "Tradeoffs": "Candidate consciously evaluates speed versus safety compromises.",
        "Reflection": "Candidate demonstrates self-reflective metacognition on decision rationale.",
    }

    def evaluate_beliefs(
        self,
        observations: Dict[str, BehaviorObservation],
        existing_beliefs: Dict[str, BehaviorBelief],
        turn_number: int,
    ) -> Dict[str, BehaviorBelief]:

        results: Dict[str, BehaviorBelief] = dict(existing_beliefs)

        for dim_name, obs in observations.items():
            belief = results.get(dim_name)
            if not belief:
                stmt = f"Candidate principle for {dim_name}: {obs.behavior_principle}"
                belief = BehaviorBelief(
                    id=f"belief_{dim_name.lower()}",
                    dimension=dim_name,
                    statement=stmt,
                    confidence=0.25,
                    supporting_evidence_count=0,
                    contradicting_evidence_count=0,
                    status=BeliefStatus.UNKNOWN,
                    needs_verification=False,
                    last_updated_turn=turn_number,
                )

            # Update belief state based on BehaviorObservation state
            if obs.behavior_state == BehaviorState.CONSISTENT:
                belief.supporting_evidence_count += 1
                belief.confidence = round(min(belief.confidence + 0.18, 0.95), 2)
                belief.needs_verification = False
            elif obs.behavior_state == BehaviorState.CONTEXTUAL_SHIFT:
                belief.supporting_evidence_count += 1
                belief.confidence = round(min(belief.confidence + 0.10, 0.90), 2)
                # Contextual shift is valid adaptation, no contradiction flag needed
                belief.needs_verification = False
            elif obs.behavior_state == BehaviorState.CONTRADICTION:
                belief.contradicting_evidence_count += 1
                belief.confidence = round(max(belief.confidence - 0.25, 0.15), 2)
                belief.status = BeliefStatus.UNCERTAIN
                belief.needs_verification = True

            # Update status category
            if belief.status != BeliefStatus.UNCERTAIN:
                if belief.confidence >= 0.75 and belief.supporting_evidence_count >= 3:
                    belief.status = BeliefStatus.VERIFIED
                elif belief.confidence >= 0.50:
                    belief.status = BeliefStatus.LIKELY
                elif belief.confidence >= 0.30:
                    belief.status = BeliefStatus.EMERGING
                else:
                    belief.status = BeliefStatus.UNKNOWN

            belief.last_updated_turn = turn_number
            results[dim_name] = belief

        return results
