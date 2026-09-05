"""
SQLAlchemy ORM models for MGEP (Model Governance & Experimentation Platform).

Table prefix: mgep_
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from sqlalchemy import String, Integer, Float, DateTime, JSON, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.persistence.database.base import Base


class ModelRegistryORM(Base):
    """Registered AI model or pipeline component in governance registry."""

    __tablename__ = "mgep_model_registries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE", index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    configuration_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

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


class ConfigurationSnapshotORM(Base):
    """Immutable snapshot of pipeline model configuration."""

    __tablename__ = "mgep_configuration_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    snapshot_name: Mapped[str] = mapped_column(String(255), nullable=False)
    config_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    speech_model_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    prompt_template_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    llm_model_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    behavior_extractor_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    construct_policy_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    scoring_policy_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    full_config_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ExperimentORM(Base):
    """Offline experimentation container."""

    __tablename__ = "mgep_experiments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT", index=True)

    baseline_snapshot_id: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_snapshot_id: Mapped[str] = mapped_column(String(255), nullable=False)

    dataset_sample_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class ExperimentRunORM(Base):
    """Output record of a single snapshot run within an experiment."""

    __tablename__ = "mgep_experiment_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    run_type: Mapped[str] = mapped_column(String(50), nullable=False)  # BASELINE or CANDIDATE
    snapshot_id: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_id: Mapped[str] = mapped_column(String(255), nullable=False)

    transcript_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    behavior_evidence_output: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    construct_evaluation_output: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    assessment_scores_output: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    confidence_values: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)

    processing_latency_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    token_usage_json: Mapped[Dict[str, int]] = mapped_column(JSON, nullable=False, default=dict)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="COMPLETED")
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ComparisonReportORM(Base):
    """Generated diff report comparing baseline vs candidate runs."""

    __tablename__ = "mgep_comparison_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    baseline_run_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    candidate_run_id: Mapped[uuid.UUID] = mapped_column(nullable=False)

    prompt_diff_summary: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    evidence_diff_summary: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    evaluation_diff_summary: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    score_deltas: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)

    latency_delta_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cost_delta_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    overall_recommendation: Mapped[str] = mapped_column(String(255), nullable=False)

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class MGEPMetricORM(Base):
    """Operational telemetry logger for governance events."""

    __tablename__ = "mgep_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    value_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
