"""
CalibrationMetadata Value Object.

Records provenance for a calibration batch — which scoring policy
version it targets, the round number, the adjustment rationale, and
operator details. Does NOT modify scores automatically.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class CalibrationMetadata:
    """Immutable tag attached to every CalibrationBatch."""

    target_policy_version: str
    calibration_round: int
    initiated_by: str
    rationale: str
    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: Optional[datetime] = None
    calibration_tool: str = "PVCSF-Calibration/1.0"
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.target_policy_version:
            raise ValueError("CalibrationMetadata: target_policy_version is required.")
        if self.calibration_round < 1:
            raise ValueError("CalibrationMetadata: calibration_round must be >= 1.")
        if not self.initiated_by:
            raise ValueError("CalibrationMetadata: initiated_by is required.")
        if not self.rationale:
            raise ValueError("CalibrationMetadata: rationale is required.")

    def to_dict(self) -> dict:
        return {
            "target_policy_version": self.target_policy_version,
            "calibration_round": self.calibration_round,
            "initiated_by": self.initiated_by,
            "rationale": self.rationale,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "calibration_tool": self.calibration_tool,
            "notes": self.notes,
        }
