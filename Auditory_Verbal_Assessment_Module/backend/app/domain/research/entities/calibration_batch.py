"""
CalibrationBatch Entity.

Aggregate root for a calibration workflow run. Groups a set of
ValidationDatasets reviewed by experts in a single calibration
round, records score adjustment recommendations (NOT auto-applied),
and tracks policy version history.

No automatic score modification occurs. All adjustments are
recommendations for psychologists and system operators to apply
manually to the ScoringPolicy after validation.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.domain.research.value_objects.calibration_metadata import CalibrationMetadata
from app.domain.research.value_objects.agreement_metrics import AgreementMetrics


@dataclass
class CalibrationBatch:
    """
    Aggregate root for a single calibration round.

    Tracks which datasets were included, what the expert vs AI
    score discrepancies were, and what adjustments are recommended.
    """

    # Identity
    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    batch_name: str = ""

    # Metadata
    metadata: Optional[CalibrationMetadata] = None

    # Dataset references
    dataset_ids: List[str] = field(default_factory=list)
    reviewed_dataset_count: int = 0

    # Agreement data collected from all ExpertReviews in this batch
    agreement_records: List[AgreementMetrics] = field(default_factory=list)

    # Score adjustment recommendations (NOT auto-applied)
    recommended_adjustments: Dict[str, Any] = field(default_factory=dict)
    """
    Structure:
    {
      "CHC": {"fluid_reasoning": +2.5, "working_memory": -1.0},
      "RIASEC": {"investigative": +1.2},
      ...
    }
    """

    # Policy version history
    policy_version_before: str = ""
    policy_version_after: Optional[str] = None
    adjustment_applied: bool = False

    # Summary statistics (populated by CalibrationService — raw counts only)
    total_discrepancies: int = 0
    constructs_with_discrepancy: List[str] = field(default_factory=list)
    mean_absolute_delta_per_construct: Dict[str, float] = field(default_factory=dict)

    # Lifecycle
    status: str = "OPEN"   # OPEN | IN_PROGRESS | COMPLETED | CLOSED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    # ---------------------------------------------------------------------------
    # Business rules
    # ---------------------------------------------------------------------------

    def add_dataset(self, dataset_id: str) -> None:
        """Register a dataset for inclusion in this calibration batch."""
        if self.status != "OPEN":
            raise ValueError(
                f"Cannot add datasets to a batch in '{self.status}' status."
            )
        if dataset_id not in self.dataset_ids:
            self.dataset_ids.append(dataset_id)

    def record_agreement(self, metrics: AgreementMetrics) -> None:
        """Add an AgreementMetrics record from an expert review."""
        self.agreement_records.append(metrics)

    def add_recommendation(self, framework: str, construct: str, delta: float) -> None:
        """
        Record a score adjustment recommendation.

        Positive delta = recommend increasing AI score for this construct.
        Negative delta = recommend decreasing it.
        No actual score modification occurs here.
        """
        if framework not in self.recommended_adjustments:
            self.recommended_adjustments[framework] = {}
        self.recommended_adjustments[framework][construct] = round(delta, 4)

    def compute_summary(self) -> None:
        """
        Compute raw discrepancy summary from agreement records.
        Statistical significance testing is left to external researchers.
        """
        if not self.agreement_records:
            return

        delta_accumulator: Dict[str, List[float]] = {}
        for record in self.agreement_records:
            deltas = record.compute_deltas()
            for construct, delta in deltas.items():
                if construct not in delta_accumulator:
                    delta_accumulator[construct] = []
                delta_accumulator[construct].append(abs(delta))

        self.mean_absolute_delta_per_construct = {
            construct: round(sum(deltas) / len(deltas), 4)
            for construct, deltas in delta_accumulator.items()
        }
        threshold = 5.0  # Points; external analysts will use their own threshold
        self.constructs_with_discrepancy = [
            c for c, mean_delta in self.mean_absolute_delta_per_construct.items()
            if mean_delta > threshold
        ]
        self.total_discrepancies = len(self.constructs_with_discrepancy)

    def complete(self) -> None:
        """Mark this calibration batch as completed."""
        if self.status not in ("OPEN", "IN_PROGRESS"):
            raise ValueError(
                f"Batch must be OPEN or IN_PROGRESS to complete, not '{self.status}'."
            )
        self.compute_summary()
        self.status = "COMPLETED"
        self.completed_at = datetime.now(timezone.utc)
        self.reviewed_dataset_count = len(self.dataset_ids)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "batch_name": self.batch_name,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "dataset_ids": self.dataset_ids,
            "reviewed_dataset_count": self.reviewed_dataset_count,
            "recommended_adjustments": self.recommended_adjustments,
            "policy_version_before": self.policy_version_before,
            "policy_version_after": self.policy_version_after,
            "adjustment_applied": self.adjustment_applied,
            "total_discrepancies": self.total_discrepancies,
            "constructs_with_discrepancy": self.constructs_with_discrepancy,
            "mean_absolute_delta_per_construct": self.mean_absolute_delta_per_construct,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
