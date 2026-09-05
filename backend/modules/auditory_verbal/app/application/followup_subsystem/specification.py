"""
Follow-up Specification Dataclass (v4 - Style & Memory Extended).
Defines the deterministic strategic output of the Adaptive Follow-up Planner & Style Engine.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class FollowUpSpecification:
    intent: str                        # E.g., PROBE_MISSING_CONSTRUCT, CHALLENGE_REASONING, CLARIFY_AMBIGUITY
    target_construct: str              # E.g., "RISK_AWARENESS"
    reason: str                        # Strategic rationale for follow-up
    context_snippet: str               # Verbatim snippet from candidate response to reference
    cognitive_depth: str               # E.g., REASONING_DEPTH, TRADE_OFF_DEFENSE
    conversation_stage: str           # EDAPAF Stage (INITIAL, ADAPTIVE_CHALLENGE, REFLECTIVE_PROBE)
    turn_number: int                   # Current follow-up turn
    style_profile: Dict[str, Any]      # NEW v4: Complete StyleProfile dictionary
    interviewer_memory_reference: str # NEW v4: Natural memory reference to prior turn claims
    questioning_style: str            # NEW v4: E.g., GUIDED_REFLECTION, COUNTERFACTUAL
    tone: str                         # NEW v4: E.g., SUPPORTIVE, ANALYTICAL, CHALLENGING
    pressure_level: str               # NEW v4: LOW, MODERATE, HIGH
    empathy_level: str                # NEW v4: LOW, MODERATE, HIGH
    remaining_constructs: List[str] = field(default_factory=list) # NEW v5
    saturation_scores: Dict[str, float] = field(default_factory=dict) # NEW v5
    closure_probability: float = 0.0  # NEW v5
    estimated_remaining_turns: int = 1# NEW v5
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "target_construct": self.target_construct,
            "reason": self.reason,
            "context_snippet": self.context_snippet,
            "cognitive_depth": self.cognitive_depth,
            "conversation_stage": self.conversation_stage,
            "turn_number": self.turn_number,
            "style_profile": self.style_profile,
            "interviewer_memory_reference": self.interviewer_memory_reference,
            "questioning_style": self.questioning_style,
            "tone": self.tone,
            "pressure_level": self.pressure_level,
            "empathy_level": self.empathy_level,
            "remaining_constructs": self.remaining_constructs,
            "saturation_scores": self.saturation_scores,
            "closure_probability": self.closure_probability,
            "estimated_remaining_turns": self.estimated_remaining_turns,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FollowUpSpecification":
        return cls(
            intent=data.get("intent", "PROBE_MISSING_CONSTRUCT"),
            target_construct=data.get("target_construct", "COMMUNICATION"),
            reason=data.get("reason", "Gather additional construct evidence"),
            context_snippet=data.get("context_snippet", ""),
            cognitive_depth=data.get("cognitive_depth", "REASONING_DEPTH"),
            conversation_stage=data.get("conversation_stage", "ADAPTIVE_FOLLOWUP"),
            turn_number=data.get("turn_number", 1),
            style_profile=data.get("style_profile", {}),
            interviewer_memory_reference=data.get("interviewer_memory_reference", ""),
            questioning_style=data.get("questioning_style", "GUIDED_REFLECTION"),
            tone=data.get("tone", "NEUTRAL"),
            pressure_level=data.get("pressure_level", "MODERATE"),
            empathy_level=data.get("empathy_level", "MODERATE"),
            metadata=data.get("metadata", {}),
        )
