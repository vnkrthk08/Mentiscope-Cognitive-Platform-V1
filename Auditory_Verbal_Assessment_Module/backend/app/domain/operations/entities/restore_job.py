"""RestoreJob Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


@dataclass
class RestoreJob:
    """Represents a restore operation from a backup job."""

    backup_job_id: str
    restore_type: str  # DATABASE, RESEARCH_DATA, AUDIT_ARCHIVE, CONFIGURATION
    initiated_by: str
    status: str = "PENDING"  # PENDING, SIMULATING, RESTORING, COMPLETED, FAILED
    simulation_result: str = ""  # PASS, FAIL, SKIPPED
    error_message: str = ""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if not self.backup_job_id:
            raise ValueError("RestoreJob backup_job_id cannot be empty.")

    def simulate(self, passed: bool) -> None:
        self.status = "SIMULATING"
        self.simulation_result = "PASS" if passed else "FAIL"

    def start_restore(self) -> None:
        self.status = "RESTORING"

    def complete(self) -> None:
        self.status = "COMPLETED"
        self.completed_at = datetime.now(timezone.utc)

    def fail(self, error: str) -> None:
        self.status = "FAILED"
        self.error_message = error
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "backup_job_id": self.backup_job_id,
            "restore_type": self.restore_type,
            "initiated_by": self.initiated_by,
            "status": self.status,
            "simulation_result": self.simulation_result,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
