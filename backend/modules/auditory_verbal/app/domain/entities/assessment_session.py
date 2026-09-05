from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.domain.entities.candidate_response import CandidateResponse
from app.domain.entities.evidence import Evidence
from app.domain.value_objects.enums import AssessmentStage, SessionStatus


# Stage progression order definition
STAGE_ORDER = [
    AssessmentStage.DEVICE_CHECK,
    AssessmentStage.INSTRUCTIONS,
    AssessmentStage.PRACTICE,
    AssessmentStage.SCENARIO_PRESENTATION,
    AssessmentStage.LISTENING_ASSESSMENT,
    AssessmentStage.SPEAKING_ASSESSMENT,
    AssessmentStage.ADAPTIVE_FOLLOWUP,
    AssessmentStage.EVIDENCE_EXTRACTION,
    AssessmentStage.CONSTRUCT_EVALUATION,
    AssessmentStage.DETERMINISTIC_SCORING,
    AssessmentStage.REPORT_GENERATION,
    AssessmentStage.COMPLETED,
]


@dataclass
class CandidateProgress:
    """Value object tracking current step, completed steps, and elapsed time."""

    current_stage: AssessmentStage = AssessmentStage.DEVICE_CHECK
    completed_stages: List[AssessmentStage] = field(default_factory=list)
    active_step_index: int = 0
    total_steps: int = 12


@dataclass
class AssessmentSession:
    """Aggregate Root representing a complete candidate assessment session lifecycle."""

    session_id: str
    candidate_id: str
    scenario_id: str
    status: SessionStatus = SessionStatus.INITIALIZED
    progress: CandidateProgress = field(default_factory=CandidateProgress)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    responses: List[CandidateResponse] = field(default_factory=list)
    extracted_evidence: List[Evidence] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.session_id or not self.session_id.strip():
            raise ValueError("AssessmentSession session_id cannot be empty.")
        if not self.candidate_id or not self.candidate_id.strip():
            raise ValueError("AssessmentSession candidate_id cannot be empty.")
        if not self.scenario_id or not self.scenario_id.strip():
            raise ValueError("AssessmentSession scenario_id cannot be empty.")

    def transition_to_stage(self, new_stage: AssessmentStage):
        """Enforces invariant: Session cannot move backwards illegally in assessment stage progression."""
        current_idx = STAGE_ORDER.index(self.progress.current_stage)
        new_idx = STAGE_ORDER.index(new_stage)

        if new_idx < current_idx:
            raise ValueError(
                f"Illegal stage transition invariant violation: Cannot move backwards from '{self.progress.current_stage}' to '{new_stage}'."
            )

        if self.progress.current_stage not in self.progress.completed_stages:
            self.progress.completed_stages.append(self.progress.current_stage)

        self.progress.current_stage = new_stage
        self.progress.active_step_index = new_idx

        if new_stage == AssessmentStage.COMPLETED:
            self.status = SessionStatus.COMPLETED
            self.completed_at = datetime.now(timezone.utc)
        elif self.status == SessionStatus.INITIALIZED:
            self.status = SessionStatus.IN_PROGRESS

    def add_response(self, response: CandidateResponse):
        self.responses.append(response)

    def add_evidence(self, evidence_item: Evidence):
        self.extracted_evidence.append(evidence_item)
