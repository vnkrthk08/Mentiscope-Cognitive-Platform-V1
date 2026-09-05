"""AlertEvent Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


@dataclass
class AlertEvent:
    """Immutable record of a triggered alert."""

    rule_id: str
    rule_name: str
    metric_name: str
    metric_value: float
    threshold: float
    severity: str
    status: str = "OPEN"  # OPEN, ACKNOWLEDGED, RESOLVED
    resolution_note: str = ""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    triggered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

    def acknowledge(self) -> None:
        self.status = "ACKNOWLEDGED"

    def resolve(self, note: str = "") -> None:
        self.status = "RESOLVED"
        self.resolution_note = note
        self.resolved_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "severity": self.severity,
            "status": self.status,
            "resolution_note": self.resolution_note,
            "triggered_at": self.triggered_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }
