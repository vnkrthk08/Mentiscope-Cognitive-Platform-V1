"""
PVCSF Infrastructure ORM Models.

SQLAlchemy 2.x mapped classes for the Psychometric Validation &
Calibration Support Framework tables.

Table prefix: pvcsf_ (prevents collisions with existing sprint tables).
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.database.base import Base


class ValidationDatasetORM(Base):
    """Persisted ValidationDataset records."""

    __tablename__ = "pvcsf_validation_datasets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    assessment_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    scenario_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Pipeline artifacts
    transcript_text: Mapped[str] = mapped_column(String(8000), nullable=False, default="")
    transcript_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    audio_asset_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    audio_duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Evidence
    behavior_evidence: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    behavior_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    observation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Constructs
    construct_evaluations: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    construct_confidence_scores: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    frameworks_evaluated: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # AI Scores
    ai_framework_scores: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    ai_composite_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    score_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    normalization_method: Mapped[str] = mapped_column(String(50), nullable=False, default="LINEAR")

    # Evidence traceability
    evidence_references: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    prompt_execution_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    construct_mapping_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    # Expert review
    expert_ratings: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    reviewer_notes: Mapped[str] = mapped_column(String(4000), nullable=False, default="")
    review_status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")

    # Provenance metadata
    research_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    # Lifecycle
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ExpertReviewORM(Base):
    """Persisted ExpertReview records."""

    __tablename__ = "pvcsf_expert_reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    reviewer_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    reviewer_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    reviewer_credentials: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    expert_construct_scores: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    comments: Mapped[str] = mapped_column(String(4000), nullable=False, default="")
    strengths: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    concerns: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    recommendations: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)

    decision: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    revision_notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    annotation_tags: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    review_round: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    review_duration_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finalised_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class CalibrationBatchORM(Base):
    """Persisted CalibrationBatch records."""

    __tablename__ = "pvcsf_calibration_batches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    batch_name: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    dataset_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    reviewed_dataset_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    agreement_records: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    recommended_adjustments: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    policy_version_before: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    policy_version_after: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    adjustment_applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    total_discrepancies: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    constructs_with_discrepancy: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    mean_absolute_delta_per_construct: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="OPEN")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class ResearchExportORM(Base):
    """Persisted ResearchExport job records."""

    __tablename__ = "pvcsf_research_exports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    export_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    calibration_batch_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    export_format: Mapped[str] = mapped_column(String(20), nullable=False, default="CSV")
    include_evidence: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    include_transcripts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    include_expert_reviews: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    include_construct_mappings: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    checksum_sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    requested_by: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    export_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class PVCSFMetricORM(Base):
    """Operational metrics for the PVCSF module."""

    __tablename__ = "pvcsf_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
