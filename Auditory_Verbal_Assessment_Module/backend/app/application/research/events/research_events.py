"""
PVCSF Application Events.

Domain events published by the research application services.
These are observation-only events and never trigger score modification.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ValidationDatasetBuilt:
    """Published when a ValidationDataset is successfully built from a completed assessment."""
    dataset_id: str
    candidate_id: str
    assessment_id: str
    scenario_id: str
    record_count: int = 1
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": "ValidationDatasetBuilt",
            "dataset_id": self.dataset_id,
            "candidate_id": self.candidate_id,
            "assessment_id": self.assessment_id,
            "scenario_id": self.scenario_id,
            "record_count": self.record_count,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True)
class ExpertReviewSubmitted:
    """Published when a psychologist submits a review."""
    review_id: str
    dataset_id: str
    reviewer_id: str
    decision: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": "ExpertReviewSubmitted",
            "review_id": self.review_id,
            "dataset_id": self.dataset_id,
            "reviewer_id": self.reviewer_id,
            "decision": self.decision,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True)
class CalibrationBatchCreated:
    """Published when a new calibration batch is opened."""
    batch_id: str
    batch_name: str
    policy_version: str
    calibration_round: int
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": "CalibrationBatchCreated",
            "batch_id": self.batch_id,
            "batch_name": self.batch_name,
            "policy_version": self.policy_version,
            "calibration_round": self.calibration_round,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True)
class CalibrationBatchCompleted:
    """Published when a calibration batch is marked complete."""
    batch_id: str
    total_discrepancies: int
    reviewed_count: int
    status: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": "CalibrationBatchCompleted",
            "batch_id": self.batch_id,
            "total_discrepancies": self.total_discrepancies,
            "reviewed_count": self.reviewed_count,
            "status": self.status,
            "occurred_at": self.occurred_at.isoformat(),
        }


@dataclass(frozen=True)
class ResearchExportCompleted:
    """Published when a dataset export job finishes."""
    export_id: str
    export_format: str
    record_count: int
    file_size_bytes: int
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": "ResearchExportCompleted",
            "export_id": self.export_id,
            "export_format": self.export_format,
            "record_count": self.record_count,
            "file_size_bytes": self.file_size_bytes,
            "occurred_at": self.occurred_at.isoformat(),
        }
