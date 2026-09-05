"""
ValidationDataset Entity.

Aggregate root representing a complete, exportable research record
constructed from a finished assessment pipeline run. Preserves
full traceability from raw transcript through behavioral evidence,
construct evaluations, and final scores.

This entity does NOT perform any psychometric validation.
It structures the data so external researchers can do so.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.domain.research.value_objects.research_metadata import ResearchMetadata


@dataclass
class ValidationDataset:
    """
    Aggregate root for a single assessment validation record.

    Collects all pipeline artifacts for one completed assessment,
    making them available for export and expert review.
    """

    # Identity
    dataset_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Assessment traceability keys
    candidate_id: str = ""
    assessment_id: str = ""
    scenario_id: str = ""
    session_id: str = ""

    # Pipeline artifacts — raw data collected from each sprint
    transcript_text: str = ""
    transcript_confidence: float = 0.0
    audio_asset_id: Optional[str] = None
    audio_duration_seconds: Optional[float] = None

    # Behavioral evidence summary (from Sprint 8)
    behavior_evidence: List[Dict[str, Any]] = field(default_factory=list)
    behavior_confidence: float = 0.0
    observation_count: int = 0

    # Construct evaluation summary (from Sprint 9)
    construct_evaluations: List[Dict[str, Any]] = field(default_factory=list)
    construct_confidence_scores: Dict[str, float] = field(default_factory=dict)
    frameworks_evaluated: List[str] = field(default_factory=list)

    # Assessment scores (from Sprint 10)
    ai_framework_scores: Dict[str, float] = field(default_factory=dict)
    ai_composite_score: float = 0.0
    score_confidence: float = 0.0
    normalization_method: str = ""

    # Evidence traceability
    evidence_references: List[Dict[str, Any]] = field(default_factory=list)
    prompt_execution_id: Optional[str] = None
    construct_mapping_ids: List[str] = field(default_factory=list)

    # Expert review state
    expert_ratings: Dict[str, float] = field(default_factory=dict)
    reviewer_notes: str = ""
    review_status: str = "PENDING"   # PENDING | UNDER_REVIEW | REVIEWED | APPROVED | REJECTED

    # Provenance
    metadata: Optional[ResearchMetadata] = None
    status: str = "DRAFT"    # DRAFT | READY | EXPORTED | ARCHIVED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # ---------------------------------------------------------------------------
    # Business rules
    # ---------------------------------------------------------------------------

    def validate_completeness(self) -> List[str]:
        """Return list of missing fields needed for a valid exportable record."""
        missing: List[str] = []
        if not self.candidate_id:
            missing.append("candidate_id")
        if not self.assessment_id:
            missing.append("assessment_id")
        if not self.scenario_id:
            missing.append("scenario_id")
        if not self.transcript_text:
            missing.append("transcript_text")
        if not self.behavior_evidence:
            missing.append("behavior_evidence")
        if not self.construct_evaluations:
            missing.append("construct_evaluations")
        if not self.ai_framework_scores:
            missing.append("ai_framework_scores")
        return missing

    def mark_ready(self) -> None:
        """Transition to READY once all required fields are present."""
        missing = self.validate_completeness()
        if missing:
            raise ValueError(
                f"ValidationDataset cannot be marked READY. Missing: {missing}"
            )
        self.status = "READY"
        self.updated_at = datetime.now(timezone.utc)

    def mark_exported(self) -> None:
        """Record that this dataset has been exported."""
        if self.status not in ("READY", "EXPORTED"):
            raise ValueError(
                f"ValidationDataset must be in READY state to export, not '{self.status}'."
            )
        self.status = "EXPORTED"
        self.updated_at = datetime.now(timezone.utc)

    def apply_expert_review(
        self,
        reviewer_id: str,
        expert_scores: Dict[str, float],
        notes: str,
        approved: bool,
    ) -> None:
        """Apply an expert reviewer's scores and decision."""
        if self.review_status == "APPROVED":
            raise ValueError(
                "ValidationDataset has already been approved and cannot be re-reviewed."
            )
        self.expert_ratings = expert_scores
        self.reviewer_notes = notes
        self.review_status = "APPROVED" if approved else "REJECTED"
        self.updated_at = datetime.now(timezone.utc)

    def to_flat_dict(self) -> Dict[str, Any]:
        """
        Produce a flat dictionary suitable for CSV / Excel row export.
        All nested structures are JSON-serialised into string columns.
        """
        import json

        return {
            "dataset_id": self.dataset_id,
            "candidate_id": self.candidate_id,
            "assessment_id": self.assessment_id,
            "scenario_id": self.scenario_id,
            "session_id": self.session_id,
            "transcript_text": self.transcript_text,
            "transcript_confidence": self.transcript_confidence,
            "audio_asset_id": self.audio_asset_id or "",
            "audio_duration_seconds": self.audio_duration_seconds or 0.0,
            "observation_count": self.observation_count,
            "behavior_confidence": self.behavior_confidence,
            "behavior_evidence_json": json.dumps(self.behavior_evidence),
            "construct_evaluations_json": json.dumps(self.construct_evaluations),
            "construct_confidence_json": json.dumps(self.construct_confidence_scores),
            "frameworks_evaluated": "|".join(self.frameworks_evaluated),
            "ai_composite_score": self.ai_composite_score,
            "score_confidence": self.score_confidence,
            "normalization_method": self.normalization_method,
            "ai_framework_scores_json": json.dumps(self.ai_framework_scores),
            "evidence_references_json": json.dumps(self.evidence_references),
            "prompt_execution_id": self.prompt_execution_id or "",
            "expert_ratings_json": json.dumps(self.expert_ratings),
            "reviewer_notes": self.reviewer_notes,
            "review_status": self.review_status,
            "dataset_status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            # Metadata fields
            "pipeline_version": self.metadata.pipeline_version if self.metadata else "",
            "model_version": self.metadata.model_version if self.metadata else "",
            "prompt_version": self.metadata.prompt_version if self.metadata else "",
            "scoring_policy_version": self.metadata.scoring_policy_version if self.metadata else "",
        }
