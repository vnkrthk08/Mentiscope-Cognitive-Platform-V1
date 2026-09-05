"""Experiment Aggregate Root Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.domain.governance.value_objects.experiment_status import ExperimentStatus


@dataclass
class Experiment:
    """Experiment aggregate root managing offline evaluation lifecycle."""

    title: str
    owner: str
    baseline_snapshot_id: str
    candidate_snapshot_id: str
    description: str = ""
    dataset_sample_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: ExperimentStatus = ExperimentStatus.DRAFT
    experiment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("Experiment title cannot be empty.")
        if not self.owner or not self.owner.strip():
            raise ValueError("Experiment owner cannot be empty.")
        if not self.baseline_snapshot_id:
            raise ValueError("Experiment baseline_snapshot_id cannot be empty.")
        if not self.candidate_snapshot_id:
            raise ValueError("Experiment candidate_snapshot_id cannot be empty.")

    def start(self) -> None:
        if self.status != ExperimentStatus.DRAFT:
            raise ValueError(f"Cannot start experiment in status '{self.status}'. Must be DRAFT.")
        self.status = ExperimentStatus.RUNNING

    def complete(self) -> None:
        if self.status != ExperimentStatus.RUNNING:
            raise ValueError(f"Cannot complete experiment in status '{self.status}'. Must be RUNNING.")
        self.status = ExperimentStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)

    def archive(self) -> None:
        self.status = ExperimentStatus.ARCHIVED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "title": self.title,
            "description": self.description,
            "owner": self.owner,
            "status": self.status.value if isinstance(self.status, ExperimentStatus) else str(self.status),
            "baseline_snapshot_id": self.baseline_snapshot_id,
            "candidate_snapshot_id": self.candidate_snapshot_id,
            "dataset_sample_ids": self.dataset_sample_ids,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
