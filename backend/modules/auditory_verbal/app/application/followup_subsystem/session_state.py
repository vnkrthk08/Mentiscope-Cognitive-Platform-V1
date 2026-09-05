"""
Follow-up Session State models and manager for Adaptive Follow-up Planning Layer.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from app.application.followup_subsystem.config import (
    MISSING_THRESHOLD,
    WEAK_THRESHOLD,
    STATUS_MISSING,
    STATUS_WEAK,
    STATUS_SUFFICIENT,
)

logger = logging.getLogger(__name__)


@dataclass
class ConstructCoverageItem:
    confidence: float = 0.0
    status: str = STATUS_MISSING
    evidence_refs: List[str] = field(default_factory=list)

    def update_status(self) -> None:
        if self.confidence < MISSING_THRESHOLD:
            self.status = STATUS_MISSING
        elif self.confidence < WEAK_THRESHOLD:
            self.status = STATUS_WEAK
        else:
            self.status = STATUS_SUFFICIENT

    def to_dict(self) -> Dict[str, Any]:
        return {
            "confidence": round(self.confidence, 2),
            "status": self.status,
            "evidence_refs": self.evidence_refs,
        }


@dataclass
class EvidenceLogEntry:
    turn: int
    source: str  # e.g., 'initial_response', 'followup_1', 'followup_2'
    claims: List[str] = field(default_factory=list)
    reasoning_shown: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    hedges: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn": self.turn,
            "source": self.source,
            "claims": self.claims,
            "reasoning_shown": self.reasoning_shown,
            "assumptions": self.assumptions,
            "hedges": self.hedges,
            "contradictions": self.contradictions,
        }


@dataclass
class FollowUpSessionState:
    scenario_id: str
    candidate_id: str
    primary_constructs: List[str] = field(default_factory=list)
    secondary_constructs: List[str] = field(default_factory=list)
    construct_coverage: Dict[str, ConstructCoverageItem] = field(default_factory=dict)
    evidence_log: List[EvidenceLogEntry] = field(default_factory=list)
    followup_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def __post_init__(self):
        # Initialize construct coverage entries for all constructs
        all_constructs = list(dict.fromkeys(self.primary_constructs + self.secondary_constructs))
        for c in all_constructs:
            if c not in self.construct_coverage:
                item = ConstructCoverageItem()
                item.update_status()
                self.construct_coverage[c] = item

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "candidate_id": self.candidate_id,
            "primary_constructs": self.primary_constructs,
            "secondary_constructs": self.secondary_constructs,
            "construct_coverage": {k: v.to_dict() for k, v in self.construct_coverage.items()},
            "evidence_log": [e.to_dict() for e in self.evidence_log],
            "followup_history": self.followup_history,
        }


class FollowUpSessionStateManager:
    """In-memory session manager for shadow Follow-up Session State."""

    def __init__(self):
        self._states: Dict[str, FollowUpSessionState] = {}

    def get_or_generate_state(
        self,
        session_id: str,
        scenario_id: str = "SCEN-DEFAULT",
        candidate_id: str = "CANDIDATE-DEFAULT",
        primary_constructs: Optional[List[str]] = None,
        secondary_constructs: Optional[List[str]] = None,
    ) -> FollowUpSessionState:
        return self.get_or_create_state(session_id, scenario_id, candidate_id, primary_constructs, secondary_constructs)

    def get_or_create_state(
        self,
        session_id: str,
        scenario_id: str = "SCEN-DEFAULT",
        candidate_id: str = "CANDIDATE-DEFAULT",
        primary_constructs: Optional[List[str]] = None,
        secondary_constructs: Optional[List[str]] = None,
    ) -> FollowUpSessionState:
        if session_id not in self._states:
            prim = primary_constructs or ["DECISION_MAKING", "REASONING"]
            sec = secondary_constructs or ["COMMUNICATION", "ATTENTION"]
            state = FollowUpSessionState(
                scenario_id=scenario_id,
                candidate_id=candidate_id,
                primary_constructs=prim,
                secondary_constructs=sec,
            )
            self._states[session_id] = state
        else:
            state = self._states[session_id]
            # Update constructs if new ones provided
            if primary_constructs:
                state.primary_constructs = primary_constructs
            if secondary_constructs:
                state.secondary_constructs = secondary_constructs
            for c in list(dict.fromkeys(state.primary_constructs + state.secondary_constructs)):
                if c not in state.construct_coverage:
                    item = ConstructCoverageItem()
                    item.update_status()
                    state.construct_coverage[c] = item

        state.updated_at = time.time()
        return state

    def get_state(self, session_id: str) -> Optional[FollowUpSessionState]:
        return self._states.get(session_id)

    def clear_session(self, session_id: str) -> None:
        if session_id in self._states:
            del self._states[session_id]
            logger.info(f"[ADAPTIVE STATE MANAGER] Cleared session state for '{session_id}'")

    def clear_expired_sessions(self, max_age_seconds: float = 3600.0) -> int:
        now = time.time()
        expired = [sid for sid, s in self._states.items() if (now - s.updated_at) > max_age_seconds]
        for sid in expired:
            del self._states[sid]
        return len(expired)
