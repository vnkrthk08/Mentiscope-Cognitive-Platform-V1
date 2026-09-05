"""ExperimentRun Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


@dataclass
class ExperimentRun:
    """Execution output of an offline experiment run for a specific snapshot and dataset."""

    experiment_id: str
    run_type: str  # BASELINE vs CANDIDATE
    snapshot_id: str
    dataset_id: str
    transcript_output: str = ""
    behavior_evidence_output: Dict[str, Any] = field(default_factory=dict)
    construct_evaluation_output: Dict[str, Any] = field(default_factory=dict)
    assessment_scores_output: Dict[str, Any] = field(default_factory=dict)
    confidence_values: Dict[str, float] = field(default_factory=dict)
    processing_latency_ms: float = 0.0
    token_usage: Dict[str, int] = field(default_factory=dict)
    estimated_cost_usd: float = 0.0
    status: str = "COMPLETED"
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.run_type not in ("BASELINE", "CANDIDATE"):
            raise ValueError(f"Invalid run_type '{self.run_type}'. Must be BASELINE or CANDIDATE.")
        if not self.experiment_id:
            raise ValueError("ExperimentRun experiment_id cannot be empty.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "experiment_id": self.experiment_id,
            "run_type": self.run_type,
            "snapshot_id": self.snapshot_id,
            "dataset_id": self.dataset_id,
            "transcript_output": self.transcript_output,
            "behavior_evidence_output": self.behavior_evidence_output,
            "construct_evaluation_output": self.construct_evaluation_output,
            "assessment_scores_output": self.assessment_scores_output,
            "confidence_values": self.confidence_values,
            "processing_latency_ms": self.processing_latency_ms,
            "token_usage": self.token_usage,
            "estimated_cost_usd": self.estimated_cost_usd,
            "status": self.status,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }
