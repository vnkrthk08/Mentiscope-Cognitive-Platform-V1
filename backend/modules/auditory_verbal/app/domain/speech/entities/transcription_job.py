from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class TranscriptionJob:
    """Domain Entity representing the state of an asynchronous background transcription process."""

    job_id: str
    asset_id: str
    provider: str
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
    retry_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.job_id or not self.job_id.strip():
            raise ValueError("TranscriptionJob job_id cannot be empty.")
        if not self.asset_id or not self.asset_id.strip():
            raise ValueError("TranscriptionJob asset_id cannot be empty.")
        if not self.provider or not self.provider.strip():
            raise ValueError("TranscriptionJob provider cannot be empty.")
        if self.status not in {"PENDING", "RUNNING", "COMPLETED", "FAILED"}:
            raise ValueError(f"TranscriptionJob status '{self.status}' is invalid.")

    def start(self):
        self.status = "RUNNING"
        self.started_at = datetime.now(timezone.utc)

    def complete(self):
        self.status = "COMPLETED"
        self.completed_at = datetime.now(timezone.utc)

    def fail(self):
        self.status = "FAILED"
        self.completed_at = datetime.now(timezone.utc)
