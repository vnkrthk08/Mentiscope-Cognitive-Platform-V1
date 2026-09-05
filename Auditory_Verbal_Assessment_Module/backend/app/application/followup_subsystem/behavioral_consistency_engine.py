"""
Module 3.6: Behavioral Consistency Engine (AIIS v18.0.0 Architecture).
Classifies candidate behavioral observations into CONSISTENT, CONTEXTUAL_SHIFT, or CONTRADICTION
by analyzing decision principles and scenario context.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.interview_understanding import CandidateDecisionData
from app.application.followup_subsystem.memory import InterviewMemory


class BehaviorState(str, Enum):
    CONSISTENT = "CONSISTENT"           # Follows same behavioral principle
    CONTEXTUAL_SHIFT = "CONTEXTUAL_SHIFT" # Legitimate adaptation due to scenario context
    CONTRADICTION = "CONTRADICTION"     # Position shift without situational justification


@dataclass(frozen=True)
class BehaviorObservation:
    dimension: str
    behavior_principle: str
    scenario_context: str
    candidate_quote: str
    explanation: Optional[str]
    quality_score: float
    confidence_score: float
    behavior_state: BehaviorState
    turn_number: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "behavior_principle": self.behavior_principle,
            "scenario_context": self.scenario_context,
            "candidate_quote": self.candidate_quote,
            "explanation": self.explanation,
            "quality_score": round(self.quality_score, 2),
            "confidence_score": round(self.confidence_score, 2),
            "behavior_state": self.behavior_state.value,
            "turn_number": self.turn_number,
        }


@dataclass
class BehavioralConsistencyProfile:
    dimension: str
    quality_score: float = 0.0
    confidence_score: float = 0.0
    consistency_score: float = 0.80
    behavior_state: BehaviorState = BehaviorState.CONSISTENT
    observation_count: int = 0
    context_count: int = 1
    needs_verification: bool = False
    active_principle: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "quality_score": round(self.quality_score, 2),
            "confidence_score": round(self.confidence_score, 2),
            "consistency_score": round(self.consistency_score, 2),
            "behavior_state": self.behavior_state.value,
            "observation_count": self.observation_count,
            "context_count": self.context_count,
            "needs_verification": self.needs_verification,
            "active_principle": self.active_principle,
        }


class BehavioralConsistencyEngine:
    """Module 3.6: Behavioral Consistency Engine parsing principles and classifying observations."""

    def extract_principle(self, decision: CandidateDecisionData, transcript_text: str) -> str:
        clean_text = (transcript_text or "").strip()
        lower_text = clean_text.lower()

        if any(w in lower_text for w in ["safety", "danger", "harm", "explode", "risk"]):
            return "Safety before speed or deadlines"
        elif any(w in lower_text for w in ["team", "teammate", "inform", "discuss", "principal", "teacher"]):
            return "Collaborative consultation when time permits"
        elif any(w in lower_text for w in ["delay", "pause", "stop"]):
            return "Cautious risk mitigation"
        elif any(w in lower_text for w in ["alone", "myself", "immediately", "quick"]):
            return "Independent decisive action under pressure"
        else:
            return f"Action: {clean_text[:40]}"

    def evaluate_consistency(
        self,
        dimension: str,
        decision: CandidateDecisionData,
        memory: InterviewMemory,
        scenario_title: str,
        transcript_text: str,
        turn_number: int,
    ) -> BehaviorObservation:

        clean_text = (transcript_text or "").strip()
        lower_text = clean_text.lower()
        principle = self.extract_principle(decision, clean_text)

        # Check against memory history
        prior_principles = memory.behavior_principles
        state = BehaviorState.CONSISTENT
        explanation = None

        if prior_principles:
            latest_principle = prior_principles[-1]
            if "instead" in lower_text or "changed my mind" in lower_text:
                if any(w in lower_text for w in ["because time", "due to deadline", "only 10 seconds", "urgent"]):
                    state = BehaviorState.CONTEXTUAL_SHIFT
                    explanation = "Adapted strategy due to time constraint or situational urgency"
                else:
                    state = BehaviorState.CONTRADICTION
                    explanation = "Position shift without explicit situational rationale"
            elif latest_principle != principle and ("deadline" in lower_text or "urgent" in lower_text):
                state = BehaviorState.CONTEXTUAL_SHIFT
                explanation = "Contextual adaptation under operational pressure"

        return BehaviorObservation(
            dimension=dimension,
            behavior_principle=principle,
            scenario_context=scenario_title,
            candidate_quote=clean_text[:100],
            explanation=explanation,
            quality_score=0.85 if len(clean_text.split()) > 10 else 0.55,
            confidence_score=0.92,
            behavior_state=state,
            turn_number=turn_number,
        )
