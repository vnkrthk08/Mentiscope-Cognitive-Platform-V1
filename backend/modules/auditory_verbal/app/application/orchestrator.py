from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.core.event_bus import event_bus
from app.core.logging import logger, log_audit_event
from app.domain.entities.assessment_session import AssessmentSession, CandidateProgress
from app.domain.exceptions.orchestrator_exceptions import (
    IllegalStateTransitionError,
    InvalidSessionStateError,
    SessionTimeoutError,
)
from app.domain.value_objects.enums import AssessmentStage, SessionStatus
from app.domain.events.assessment_events import (
    AssessmentStarted,
    StageEntered,
    StageCompleted,
    ListeningStarted,
    ListeningCompleted,
    SpeakingStarted,
    SpeakingCompleted,
    FollowUpStarted,
    EvidenceStarted,
    EvidenceCompleted,
    ScoringStarted,
    ScoringCompleted,
    AssessmentCompleted,
    AssessmentPaused,
    AssessmentRecovered,
)


# Strict Finite State Machine (FSM) Allowed Transitions Matrix
VALID_TRANSITIONS: Dict[str, List[str]] = {
    "CREATED": ["DEVICE_CHECK", "PAUSED", "FAILED"],
    "DEVICE_CHECK": ["INSTRUCTIONS", "PAUSED", "FAILED"],
    "INSTRUCTIONS": ["PRACTICE", "PAUSED", "FAILED"],
    "PRACTICE": ["SCENARIO_PRESENTATION", "PAUSED", "FAILED"],
    "SCENARIO_PRESENTATION": ["LISTENING", "PAUSED", "FAILED"],
    "LISTENING": ["SPEAKING", "PAUSED", "FAILED"],
    "SPEAKING": ["ADAPTIVE_FOLLOWUP", "EVIDENCE_PROCESSING", "PAUSED", "FAILED"],
    "ADAPTIVE_FOLLOWUP": ["EVIDENCE_PROCESSING", "PAUSED", "FAILED"],
    "EVIDENCE_PROCESSING": ["SCORING", "PAUSED", "FAILED"],
    "SCORING": ["REPORT_GENERATION", "PAUSED", "FAILED"],
    "REPORT_GENERATION": ["COMPLETED", "PAUSED", "FAILED"],
    "PAUSED": ["RECOVERING", "TIMED_OUT", "FAILED"],
    "RECOVERING": [
        "DEVICE_CHECK",
        "INSTRUCTIONS",
        "PRACTICE",
        "SCENARIO_PRESENTATION",
        "LISTENING",
        "SPEAKING",
        "ADAPTIVE_FOLLOWUP",
        "EVIDENCE_PROCESSING",
        "SCORING",
        "REPORT_GENERATION",
        "FAILED",
    ],
    "TIMED_OUT": ["RECOVERING", "FAILED"],
    "FAILED": ["RECOVERING"],
    "COMPLETED": [],
}


@dataclass
class TransitionAuditRecord:
    """Immutable audit record for every state transition in the Orchestrator."""

    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    previous_state: str = ""
    next_state: str = ""
    reason: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AssessmentOrchestrator:
    """Production-grade Assessment Orchestrator operating as a Finite State Machine (FSM).
    Coordinates the entire assessment lifecycle, transition validation, session context, auditability,
    and domain event publishing.
    """

    def __init__(
        self,
        max_inactivity_seconds: float = 600.0,  # 10 minutes timeout
    ):
        self.max_inactivity_seconds = max_inactivity_seconds
        self._audit_log: List[TransitionAuditRecord] = []
        self._last_heartbeat: Dict[str, datetime] = {}

    def create_assessment_session(
        self, candidate_id: str, scenario_id: str, session_id: Optional[str] = None
    ) -> AssessmentSession:
        """Initializes a new assessment session in CREATED state."""
        sid = session_id or f"SESS-{uuid.uuid4().hex[:8].upper()}"
        session = AssessmentSession(
            session_id=sid,
            candidate_id=candidate_id,
            scenario_id=scenario_id,
            status=SessionStatus.INITIALIZED,
        )
        session.metadata["current_fsm_state"] = "CREATED"
        self._last_heartbeat[sid] = datetime.now(timezone.utc)

        self._record_transition(sid, "NONE", "CREATED", "Assessment Session Created")
        logger.info(f"Initialized assessment session '{sid}' for candidate '{candidate_id}'")

        return session

    async def start_assessment(self, session: AssessmentSession) -> AssessmentSession:
        """Transitions session from CREATED to DEVICE_CHECK and emits AssessmentStarted event."""
        await self.transition_to(session, "DEVICE_CHECK", reason="Assessment Lifecycle Started")
        
        await event_bus.publish(
            "AssessmentStarted",
            AssessmentStarted(
                session_id=session.session_id,
                candidate_id=session.candidate_id,
                scenario_id=session.scenario_id,
            ),
        )
        return session

    async def transition_to(
        self, session: AssessmentSession, target_state: str, reason: str = ""
    ) -> AssessmentSession:
        """Core FSM transition method enforcing strict transition validation."""
        self._check_timeout(session)
        current_state = session.metadata.get("current_fsm_state", "CREATED")

        allowed_targets = VALID_TRANSITIONS.get(current_state, [])
        if target_state not in allowed_targets:
            logger.error(
                f"Illegal FSM transition attempted for session '{session.session_id}': "
                f"{current_state} -> {target_state}"
            )
            raise IllegalStateTransitionError(current_state, target_state, session.session_id)

        # Record transition audit log
        self._record_transition(session.session_id, current_state, target_state, reason)

        # Update Session domain model stage mapping
        session.metadata["current_fsm_state"] = target_state
        self._last_heartbeat[session.session_id] = datetime.now(timezone.utc)

        if target_state == "PAUSED":
            session.status = SessionStatus.PAUSED
            await event_bus.publish(
                "AssessmentPaused",
                AssessmentPaused(
                    session_id=session.session_id,
                    paused_at_stage=current_state,
                    reason=reason,
                ),
            )
        elif target_state == "COMPLETED":
            session.status = SessionStatus.COMPLETED
            session.completed_at = datetime.now(timezone.utc)
            elapsed = (session.completed_at - session.started_at).total_seconds()
            await event_bus.publish(
                "AssessmentCompleted",
                AssessmentCompleted(
                    session_id=session.session_id,
                    candidate_id=session.candidate_id,
                    total_duration_seconds=elapsed,
                ),
            )
        else:
            session.status = SessionStatus.IN_PROGRESS
            await event_bus.publish(
                "StageEntered",
                StageEntered(
                    session_id=session.session_id,
                    previous_stage=current_state,
                    current_stage=target_state,
                ),
            )

        logger.info(f"[FSM] Session '{session.session_id}': {current_state} -> {target_state} ({reason})")
        return session

    async def pause_assessment(self, session: AssessmentSession, reason: str = "User Inactivity") -> AssessmentSession:
        """Pauses active assessment session."""
        return await self.transition_to(session, "PAUSED", reason=reason)

    async def resume_assessment(self, session: AssessmentSession) -> AssessmentSession:
        """Resumes a paused assessment session by transitioning to RECOVERING then restoring stage."""
        if session.status not in [SessionStatus.PAUSED, SessionStatus.TIMED_OUT]:
            raise InvalidSessionStateError(session.session_id, session.status.value, "resume")

        last_active_stage = session.metadata.get("last_active_stage", "DEVICE_CHECK")
        await self.transition_to(session, "RECOVERING", reason="Session Recovery Initiated")
        
        await event_bus.publish(
            "AssessmentRecovered",
            AssessmentRecovered(
                session_id=session.session_id,
                restored_stage=last_active_stage,
            ),
        )

        return await self.transition_to(session, last_active_stage, reason="Restored Last Active Stage")

    def record_heartbeat(self, session_id: str):
        """Records candidate activity heartbeat timestamp."""
        self._last_heartbeat[session_id] = datetime.now(timezone.utc)

    def calculate_completion_percentage(self, session: AssessmentSession) -> float:
        """Calculates current assessment completion percentage from FSM stage."""
        state_order = list(VALID_TRANSITIONS.keys())
        current_state = session.metadata.get("current_fsm_state", "CREATED")
        
        if current_state == "COMPLETED":
            return 100.0
        if current_state not in state_order:
            return 0.0
        
        idx = state_order.index(current_state)
        # 12 primary stages
        return round((idx / 11.0) * 100.0, 1)

    def get_audit_trail(self, session_id: str) -> List[TransitionAuditRecord]:
        """Returns immutable state transition audit log for a given session."""
        return [r for r in self._audit_log if r.session_id == session_id]

    def _record_transition(self, session_id: str, prev_state: str, next_state: str, reason: str):
        record = TransitionAuditRecord(
            session_id=session_id,
            previous_state=prev_state,
            next_state=next_state,
            reason=reason,
        )
        self._audit_log.append(record)
        log_audit_event("FSM_STATE_TRANSITION", session_id, {
            "previous_state": prev_state,
            "next_state": next_state,
            "reason": reason,
        })

    def _check_timeout(self, session: AssessmentSession):
        last_hb = self._last_heartbeat.get(session.session_id)
        if last_hb:
            elapsed = (datetime.now(timezone.utc) - last_hb).total_seconds()
            if elapsed > self.max_inactivity_seconds:
                session.status = SessionStatus.TIMED_OUT
                session.metadata["current_fsm_state"] = "TIMED_OUT"
                logger.warning(f"Session '{session.session_id}' timed out after {elapsed:.1f}s inactivity")
                raise SessionTimeoutError(session.session_id, elapsed, self.max_inactivity_seconds)
