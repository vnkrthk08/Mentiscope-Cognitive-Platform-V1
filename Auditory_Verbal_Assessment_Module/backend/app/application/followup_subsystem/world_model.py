"""
Module 3: Interview World Model (AIIS v20.1 Architecture).
Consolidates all system state: candidate facts, evidence graph, belief hypotheses, intent perception,
conversation state, remaining uncertainty, active policy, and dialogue memory into a single unified object.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.memory import InterviewMemory
from app.application.followup_subsystem.conversation_manager import ConversationState


@dataclass
class DialogueMemoryState:
    already_acknowledged: bool = False
    already_challenged: bool = False
    already_reflected: bool = False
    already_summarized: bool = False
    used_opening_templates: List[str] = field(default_factory=list)
    recent_interview_moves: List[str] = field(default_factory=list)
    acknowledgement_count: int = 0
    repetition_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "already_acknowledged": self.already_acknowledged,
            "already_challenged": self.already_challenged,
            "already_reflected": self.already_reflected,
            "already_summarized": self.already_summarized,
            "used_opening_templates": self.used_opening_templates[-5:],
            "recent_interview_moves": self.recent_interview_moves[-5:],
            "acknowledgement_count": self.acknowledgement_count,
            "repetition_score": round(self.repetition_score, 2),
        }


@dataclass
class InterviewWorldModel:
    session_id: str
    scenario_title: str
    turn_number: int = 1
    memory: InterviewMemory = field(default_factory=lambda: InterviewMemory(session_id=""))
    conversation_state: ConversationState = field(default_factory=lambda: ConversationState(session_id=""))
    beliefs_matrix: Dict[str, Any] = field(default_factory=dict)
    sufficiency_matrix: Dict[str, Any] = field(default_factory=dict)
    intent_result: Dict[str, Any] = field(default_factory=dict)
    remaining_uncertainty: Dict[str, float] = field(default_factory=lambda: {
        "Reason": 0.85,
        "Risk": 0.95,
        "Stakeholders": 0.90,
        "Alternatives": 0.95,
        "Tradeoffs": 0.95,
        "Reflection": 0.95,
    })
    active_policy: Optional[Dict[str, Any]] = None
    information_gain_scores: Dict[str, float] = field(default_factory=dict)
    dialogue_memory: DialogueMemoryState = field(default_factory=DialogueMemoryState)

    def calculate_overall_uncertainty(self) -> float:
        if not self.remaining_uncertainty:
            return 0.50
        values = list(self.remaining_uncertainty.values())
        return round(sum(values) / len(values), 3)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "scenario_title": self.scenario_title,
            "turn_number": self.turn_number,
            "overall_uncertainty": self.calculate_overall_uncertainty(),
            "remaining_uncertainty": {k: round(v, 2) for k, v in self.remaining_uncertainty.items()},
            "beliefs_matrix": self.beliefs_matrix,
            "sufficiency_matrix": self.sufficiency_matrix,
            "intent_result": self.intent_result,
            "active_policy": self.active_policy,
            "information_gain_scores": {k: round(v, 2) for k, v in self.information_gain_scores.items()},
            "dialogue_memory": self.dialogue_memory.to_dict(),
        }
