"""BackupJob Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


@dataclass
class BackupJob:
    """Represents a backup operation for database, research data, audit, or configuration."""

    backup_type: str  # DATABASE, RESEARCH_DATA, AUDIT_ARCHIVE, CONFIGURATION
    initiated_by: str
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED, VERIFIED
    target_path: str = ""
    size_bytes: int = 0
    checksum: str = ""
    error_message: str = ""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if not self.backup_type:
            raise ValueError("BackupJob backup_type cannot be empty.")
        if self.backup_type not in ("DATABASE", "RESEARCH_DATA", "AUDIT_ARCHIVE", "CONFIGURATION"):
            raise ValueError(f"Invalid backup_type: {self.backup_type}")

    def start(self) -> None:
        self.status = "RUNNING"

    def complete(self, target_path: str, size_bytes: int, checksum: str) -> None:
        self.status = "COMPLETED"
        self.target_path = target_path
        self.size_bytes = size_bytes
        self.checksum = checksum
        self.completed_at = datetime.now(timezone.utc)

    def verify(self) -> None:
        self.status = "VERIFIED"

    def fail(self, error: str) -> None:
        self.status = "FAILED"
        self.error_message = error
        self.completed_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "backup_type": self.backup_type,
            "initiated_by": self.initiated_by,
            "status": self.status,
            "target_path": self.target_path,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
