"""
Module 4: Conversation State & Manager (Interviewer Brain - AIIS v15.0.0).
Manages Interviewer State (already asked objectives, remaining objectives, turn number, refusal count)
and maps response statuses into deterministic interviewer actions via an explicit decision table.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum


class InterviewerAction(str, Enum):
    CONTINUE = "CONTINUE"
    CLARIFY = "CLARIFY"
    ELABORATE = "ELABORATE"
    REDIRECT = "REDIRECT"
    REALISTIC_ANSWER = "REALISTIC_ANSWER"
    REDUCE_DIFFICULTY = "REDUCE_DIFFICULTY"
    ENCOURAGE = "ENCOURAGE"
    TERMINATE = "TERMINATE"
    SWITCH_OBJECTIVE = "SWITCH_OBJECTIVE"
    VERIFY_CONSISTENCY = "VERIFY_CONSISTENCY"


from app.application.followup_subsystem.evidence_graph import BehavioralEvidenceGraph


@dataclass
class ConversationState:
    session_id: str
    turn_number: int = 1
    already_asked_objectives: List[str] = field(default_factory=list)
    remaining_objectives: List[str] = field(default_factory=lambda: [
        "ASK_REASON", "ASK_RISK", "ASK_STAKEHOLDER", "ASK_ALTERNATIVE", "ASK_TRADEOFF", "ASK_REFLECTION"
    ])
    refusal_count: int = 0
    current_action: InterviewerAction = InterviewerAction.CONTINUE
    is_completed: bool = False
    completion_reason: str = ""
    edapaf_stage: str = "INITIAL"
    challenge_level: int = 1
    cognitive_load: int = 1
    construct_confidence_matrix: Dict[str, float] = field(default_factory=dict)
    evidence_saturation: Dict[str, bool] = field(default_factory=dict)
    completed_objectives: List[str] = field(default_factory=list)
    asked_question_texts: List[str] = field(default_factory=list)
    asked_intent_history: List[str] = field(default_factory=list)
    evidence_graph: BehavioralEvidenceGraph = field(default_factory=lambda: BehavioralEvidenceGraph())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "already_asked_objectives": self.already_asked_objectives,
            "asked_question_texts": self.asked_question_texts,
            "asked_intent_history": self.asked_intent_history,
            "remaining_objectives": self.remaining_objectives,
            "refusal_count": self.refusal_count,
            "current_action": self.current_action.value,
            "is_completed": self.is_completed,
            "completion_reason": self.completion_reason,
            "edapaf_stage": self.edapaf_stage,
            "challenge_level": self.challenge_level,
            "cognitive_load": self.cognitive_load,
            "construct_confidence_matrix": self.construct_confidence_matrix,
            "evidence_saturation": self.evidence_saturation,
            "completed_objectives": self.completed_objectives,
        }


class ConversationManager:
    """Module 4: Interviewer Brain managing status-to-action decision table and interviewer state."""

    STATUS_ACTION_MAP: Dict[str, InterviewerAction] = {
        "VALID": InterviewerAction.CONTINUE,
        "PARTIALLY_VALID": InterviewerAction.CLARIFY,
        "TOO_SHORT": InterviewerAction.ELABORATE,
        "OFF_TOPIC": InterviewerAction.REDIRECT,
        "NONSENSICAL": InterviewerAction.REALISTIC_ANSWER,
        "UNCERTAIN": InterviewerAction.REDUCE_DIFFICULTY,
        "REFUSAL": InterviewerAction.ENCOURAGE,
        "REPETITIVE": InterviewerAction.SWITCH_OBJECTIVE,
        "CONTRADICTORY": InterviewerAction.VERIFY_CONSISTENCY,
    }

    def determine_action(self, status: str, state: ConversationState) -> InterviewerAction:
        action = self.STATUS_ACTION_MAP.get(status, InterviewerAction.CONTINUE)

        if status == "REFUSAL":
            state.refusal_count += 1
            if state.refusal_count >= 3:
                state.is_completed = True
                state.completion_reason = "Candidate repeated refusal threshold reached."
                return InterviewerAction.TERMINATE
            return InterviewerAction.ENCOURAGE
        else:
            state.refusal_count = 0

        state.current_action = action
        return action

    def update_interviewer_state(self, state: ConversationState, applied_objective: str):
        state.turn_number += 1
        if applied_objective not in state.already_asked_objectives:
            state.already_asked_objectives.append(applied_objective)
        if applied_objective in state.remaining_objectives:
            state.remaining_objectives.remove(applied_objective)
        if applied_objective not in state.completed_objectives:
            state.completed_objectives.append(applied_objective)

        if state.turn_number == 1:
            state.edapaf_stage = "INITIAL"
        elif state.turn_number in (2, 3):
            state.edapaf_stage = "ADAPTIVE_CHALLENGE"
        else:
            state.edapaf_stage = "REFLECTIVE_PROBE"


class ConversationStateManager:
    """Manages in-memory lifecycle of ConversationState."""

    _active_states: Dict[str, ConversationState] = {}

    @classmethod
    def get_or_create_state(cls, session_id: str = "default_session") -> ConversationState:
        if session_id not in cls._active_states:
            cls._active_states[session_id] = ConversationState(session_id=session_id)
        return cls._active_states[session_id]
