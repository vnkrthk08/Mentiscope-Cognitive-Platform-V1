"""
Module 3: Interview Memory (Evidence Repository - AIIS v15.0.0).
Tracks Candidate Facts across turns (what the candidate explicitly stated: decisions, reasons, risks, stakeholders, alternatives, tradeoffs).
Maintains an immutable evidence repository of candidate statements.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.interview_understanding import CandidateDecisionData


@dataclass
class InterviewMemory:
    session_id: str
    candidate_decisions: List[str] = field(default_factory=list)
    stated_reasons: List[str] = field(default_factory=list)
    stated_risks: List[str] = field(default_factory=list)
    mentioned_stakeholders: List[str] = field(default_factory=list)
    proposed_alternatives: List[str] = field(default_factory=list)
    stated_tradeoffs: List[str] = field(default_factory=list)
    raw_statements: List[str] = field(default_factory=list)
    behavior_principles: List[str] = field(default_factory=list)

    def record_behavior_principle(self, principle: str):
        if principle and principle not in self.behavior_principles:
            self.behavior_principles.append(principle)

    def record_candidate_facts(self, transcript_text: str, decision_data: CandidateDecisionData, turn_number: int):
        clean_text = (transcript_text or "").strip()
        if len(clean_text) < 3:
            return

        self.raw_statements.append(clean_text)

        if decision_data.action and decision_data.action not in self.candidate_decisions:
            self.candidate_decisions.append(decision_data.action)

        if decision_data.reason and decision_data.reason not in self.stated_reasons:
            self.stated_reasons.append(decision_data.reason)

        for r in (decision_data.risks or []):
            if r not in self.stated_risks:
                self.stated_risks.append(r)

        for s in (decision_data.stakeholders or []):
            if s not in self.mentioned_stakeholders:
                self.mentioned_stakeholders.append(s)

        for a in (decision_data.alternatives or []):
            if a not in self.proposed_alternatives:
                self.proposed_alternatives.append(a)

        for t in (decision_data.tradeoffs or []):
            if t not in self.stated_tradeoffs:
                self.stated_tradeoffs.append(t)

    def detect_contradiction(self, current_action: Optional[str]) -> Optional[Dict[str, str]]:
        """Compares current action against prior candidate decisions to identify contradiction."""
        if not current_action or not self.candidate_decisions:
            return None

        clean_curr = current_action.lower()
        if "instead" in clean_curr or "changed my mind" in clean_curr or "actually no" in clean_curr:
            prior = self.candidate_decisions[-1]
            return {
                "prior_decision": prior,
                "current_decision": current_action,
                "memory_quote": f"Earlier you mentioned '{prior[:50]}', but now you've said '{current_action[:50]}'.",
            }
        return None

    def extract_memory_reference(self) -> str:
        if not self.candidate_decisions:
            return "Reflecting on your overall approach so far."

        latest = self.candidate_decisions[-1]
        lower = latest.lower()

        if any(w in lower for w in ["select", "choose", "pick", "chose"]):
            action_frame = "your selection criteria"
        elif any(w in lower for w in ["stop", "halt", "pause", "shut"]):
            action_frame = "your decision to intervene"
        elif any(w in lower for w in ["inform", "tell", "notify", "communicate"]):
            action_frame = "your communication approach"
        elif any(w in lower for w in ["delay", "wait", "postpone"]):
            action_frame = "your decision to hold off"
        elif any(w in lower for w in ["prioritize", "focus", "emphasize"]):
            action_frame = "the priority you set"
        else:
            action_frame = "the approach you described"

        from app.application.followup_subsystem.dialogue_editor import DialogueEditor
        details = DialogueEditor.extract_details_from_text(latest)

        if details:
            formatted = [DialogueEditor.format_detail(d) for d in details]
            detail_str = " and ".join(formatted)
            return f"Thinking about {action_frame} — particularly {detail_str}."
        else:
            return f"Thinking about {action_frame}."

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "candidate_decisions": self.candidate_decisions,
            "stated_reasons": self.stated_reasons,
            "stated_risks": self.stated_risks,
            "mentioned_stakeholders": self.mentioned_stakeholders,
            "proposed_alternatives": self.proposed_alternatives,
            "stated_tradeoffs": self.stated_tradeoffs,
            "raw_statements": self.raw_statements,
        }


class InterviewMemoryManager:
    """Manages session-level storage of InterviewMemory objects."""

    _memories: Dict[str, InterviewMemory] = {}

    @classmethod
    def get_or_create_memory(cls, session_id: str = "default_session") -> InterviewMemory:
        if session_id not in cls._memories:
            cls._memories[session_id] = InterviewMemory(session_id=session_id)
        return cls._memories[session_id]
