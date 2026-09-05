"""MaintenanceWindow Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


@dataclass
class MaintenanceWindow:
    """Scheduled maintenance window for platform operations."""

    title: str
    scheduled_by: str
    start_time: datetime
    end_time: datetime
    reason: str = ""
    status: str = "SCHEDULED"  # SCHEDULED, ACTIVE, COMPLETED, CANCELLED
    affected_services: str = "ALL"
    window_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("MaintenanceWindow title cannot be empty.")
        if self.end_time <= self.start_time:
            raise ValueError("MaintenanceWindow end_time must be after start_time.")

    def activate(self) -> None:
        self.status = "ACTIVE"

    def complete(self) -> None:
        self.status = "COMPLETED"

    def cancel(self) -> None:
        self.status = "CANCELLED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "window_id": self.window_id,
            "title": self.title,
            "scheduled_by": self.scheduled_by,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "reason": self.reason,
            "status": self.status,
            "affected_services": self.affected_services,
            "created_at": self.created_at.isoformat(),
        }
