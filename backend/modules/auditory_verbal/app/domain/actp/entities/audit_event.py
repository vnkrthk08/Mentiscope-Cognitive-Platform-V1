"""AuditEvent Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid

from app.domain.actp.value_objects.audit_metadata import AuditMetadata
from app.domain.actp.value_objects.pipeline_invocation import PipelineInvocation


@dataclass
class AuditEvent:
    """Single immutable audit event record in the pipeline lifecycle."""

    session_id: str
    assessment_id: str
    event_type: str  # ASSESSMENT_CREATED, AUDIO_UPLOADED, SPEECH_PROCESSED, PROMPT_EXECUTED, EVIDENCE_EXTRACTED, CONSTRUCT_EVALUATED, ASSESSMENT_SCORED, REPORT_GENERATED, RESEARCH_DATASET_CREATED, EXPERT_REVIEW, EXPERIMENT_COMPARISON
    step_order: int
    stage_name: str
    payload: Dict[str, Any] = field(default_factory=dict)
    invocation: Optional[PipelineInvocation] = None
    metadata: Optional[AuditMetadata] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.session_id:
            raise ValueError("AuditEvent session_id cannot be empty.")
        if not self.assessment_id:
            raise ValueError("AuditEvent assessment_id cannot be empty.")
        if not self.event_type:
            raise ValueError("AuditEvent event_type cannot be empty.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "assessment_id": self.assessment_id,
            "event_type": self.event_type,
            "step_order": self.step_order,
            "stage_name": self.stage_name,
            "payload": self.payload,
            "invocation": self.invocation.to_dict() if self.invocation else None,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
