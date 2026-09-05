"""
Module 1: Conversation State Management.
Persists multi-turn conversation state, construct confidence trends, cognitive load, and evidence saturation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.evidence_extractor import EvidenceItem
from app.application.followup_subsystem.evidence_graph import BehavioralEvidenceGraph, GraphNode, GraphEdge, NodeType, EdgeType


@dataclass
class ConversationState:
    session_id: str
    turn_number: int = 1
    edapaf_stage: str = "INITIAL"  # INITIAL, ADAPTIVE_CHALLENGE, REFLECTIVE_PROBE
    completed_objectives: List[str] = field(default_factory=list)
    explored_topics: List[str] = field(default_factory=list)
    construct_confidence_matrix: Dict[str, float] = field(default_factory=dict)
    construct_saturation_matrix: Dict[str, Any] = field(default_factory=dict) # NEW v5
    completion_percentage: float = 0.0                                          # NEW v5
    estimated_remaining_turns: int = 3                                         # NEW v5
    response_quality_history: List[str] = field(default_factory=list)          # NEW v7
    invalid_attempt_count: int = 0                                             # NEW v7
    last_validation_result: Optional[Dict[str, Any]] = None                    # NEW v7
    clarification_attempts: int = 0                                            # NEW v7
    response_quality_trend: List[str] = field(default_factory=list)           # NEW v7
    response_assessments: List[Dict[str, Any]] = field(default_factory=list)   # NEW v8
    evidence_gain_history: List[float] = field(default_factory=list)         # NEW v8
    repeated_information_counter: int = 0                                      # NEW v8
    strategy_switch_history: List[Dict[str, Any]] = field(default_factory=list)# NEW v8
    construct_probe_count: Dict[str, int] = field(default_factory=dict)        # NEW v8
    last_objective_change_reason: str = ""                                     # NEW v8
    extracted_decisions: List[Dict[str, Any]] = field(default_factory=list)    # NEW v11
    decision_coverage_matrix: Dict[str, Any] = field(default_factory=dict)     # NEW v11
    decision_probing_history: List[Dict[str, Any]] = field(default_factory=list)# NEW v11
    decision_knowledge_gaps: List[str] = field(default_factory=list)          # NEW v11
    evidence_saturation: Dict[str, bool] = field(default_factory=dict)
    contradictions_detected: List[Dict[str, Any]] = field(default_factory=list)
    clarification_history: List[int] = field(default_factory=list)
    candidate_confidence_trend: List[float] = field(default_factory=list)
    reasoning_depth_trend: List[str] = field(default_factory=list)
    communication_clarity_trend: List[float] = field(default_factory=list)
    challenge_level: int = 1  # 1 to 5
    cognitive_load: int = 1   # 1 to 5
    previous_followups: List[str] = field(default_factory=list)
    previous_interviewer_goals: List[str] = field(default_factory=list)
    evidence_graph: BehavioralEvidenceGraph = field(default_factory=lambda: BehavioralEvidenceGraph()) # NEW v5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "edapaf_stage": self.edapaf_stage,
            "completed_objectives": self.completed_objectives,
            "explored_topics": self.explored_topics,
            "construct_confidence_matrix": self.construct_confidence_matrix,
            "construct_saturation_matrix": self.construct_saturation_matrix,
            "completion_percentage": self.completion_percentage,
            "estimated_remaining_turns": self.estimated_remaining_turns,
            "response_quality_history": self.response_quality_history,
            "invalid_attempt_count": self.invalid_attempt_count,
            "last_validation_result": self.last_validation_result,
            "clarification_attempts": self.clarification_attempts,
            "response_quality_trend": self.response_quality_trend,
            "response_assessments": self.response_assessments,
            "evidence_gain_history": self.evidence_gain_history,
            "repeated_information_counter": self.repeated_information_counter,
            "strategy_switch_history": self.strategy_switch_history,
            "construct_probe_count": self.construct_probe_count,
            "last_objective_change_reason": self.last_objective_change_reason,
            "extracted_decisions": self.extracted_decisions,
            "decision_coverage_matrix": self.decision_coverage_matrix,
            "decision_probing_history": self.decision_probing_history,
            "decision_knowledge_gaps": self.decision_knowledge_gaps,
            "evidence_saturation": self.evidence_saturation,
            "contradictions_detected": self.contradictions_detected,
            "clarification_history": self.clarification_history,
            "candidate_confidence_trend": self.candidate_confidence_trend,
            "reasoning_depth_trend": self.reasoning_depth_trend,
            "communication_clarity_trend": self.communication_clarity_trend,
            "challenge_level": self.challenge_level,
            "cognitive_load": self.cognitive_load,
            "previous_followups": self.previous_followups,
            "previous_interviewer_goals": self.previous_interviewer_goals,
            "evidence_graph": self.evidence_graph.to_dict(),
        }


class ConversationStateManager:
    """Manages the in-memory or session-based lifecycle of ConversationState."""

    _active_states: Dict[str, ConversationState] = {}

    @classmethod
    def get_or_create_state(cls, session_id: str = "default_session") -> ConversationState:
        if session_id not in cls._active_states:
            cls._active_states[session_id] = ConversationState(session_id=session_id)
        return cls._active_states[session_id]

    @classmethod
    def update_state(
        cls,
        state: ConversationState,
        evidence_items: List[EvidenceItem],
        transcript_text: str,
        target_constructs: List[str],
        objective_applied: str,
    ) -> ConversationState:
        clean_text = (transcript_text or "").strip()
        state.turn_number += 1

        if objective_applied not in state.completed_objectives:
            state.completed_objectives.append(objective_applied)
        state.previous_interviewer_goals.append(objective_applied)

        # Update construct confidence matrix & saturation
        for item in evidence_items:
            c = item.construct
            curr = state.construct_confidence_matrix.get(c, 0.0)
            new_val = round(min(curr + item.confidence * 0.4, 1.0), 2)
            state.construct_confidence_matrix[c] = new_val
            state.evidence_saturation[c] = new_val >= 0.75

        # Detect contradictions (e.g. if candidate switches choices)
        lowered = clean_text.lower()
        if "instead" in lowered or "changed my mind" in lowered or "actually no" in lowered:
            state.contradictions_detected.append(
                {"turn": state.turn_number, "quote": clean_text[:100], "signal": "Explicit position shift"}
            )

        # Track trends
        words = len(clean_text.split())
        state.communication_clarity_trend.append(round(min(words / 40.0, 1.0), 2))

        if any(w in lowered for w in ["because", "therefore", "reason", "logic"]):
            state.reasoning_depth_trend.append("DEEP")
        elif any(w in lowered for w in ["so", "then", "think"]):
            state.reasoning_depth_trend.append("MODERATE")
        else:
            state.reasoning_depth_trend.append("SURFACE")

        # Dynamic Stage Transitioning
        if state.turn_number == 1:
            state.edapaf_stage = "INITIAL"
        elif state.turn_number in [2, 3]:
            state.edapaf_stage = "ADAPTIVE_CHALLENGE"
            state.challenge_level = min(state.challenge_level + 1, 5)
            state.cognitive_load = min(state.cognitive_load + 1, 5)
        else:
            state.edapaf_stage = "REFLECTIVE_PROBE"

        return state
