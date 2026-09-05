"""AuditSession Aggregate Root Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.domain.actp.entities.audit_event import AuditEvent
from app.domain.actp.value_objects.audit_metadata import AuditMetadata


@dataclass
class AuditSession:
    """AuditSession aggregate root representing complete audit record for an assessment."""

    assessment_id: str
    candidate_id: str
    scenario_id: str
    session_status: str = "ACTIVE"  # ACTIVE, COMPLETED, AUDITED, ARCHIVED
    metadata: Optional[AuditMetadata] = None
    events: List[AuditEvent] = field(default_factory=list)
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if not self.assessment_id:
            raise ValueError("AuditSession assessment_id cannot be empty.")
        if not self.candidate_id:
            raise ValueError("AuditSession candidate_id cannot be empty.")

    def add_event(self, event: AuditEvent) -> None:
        self.events.append(event)

    def complete(self) -> None:
        self.session_status = "COMPLETED"
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "assessment_id": self.assessment_id,
            "candidate_id": self.candidate_id,
            "scenario_id": self.scenario_id,
            "session_status": self.session_status,
            "total_events": len(self.events),
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "events": [e.to_dict() for e in self.events],
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
