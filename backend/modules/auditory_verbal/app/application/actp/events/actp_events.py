"""ACTP Domain Events."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict
import uuid


@dataclass
class ACTPEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditSessionCreatedEvent(ACTPEvent):
    def __post_init__(self):
        self.event_type = "AUDIT_SESSION_CREATED"


@dataclass
class DecisionRecordedEvent(ACTPEvent):
    def __post_init__(self):
        self.event_type = "DECISION_RECORDED"
