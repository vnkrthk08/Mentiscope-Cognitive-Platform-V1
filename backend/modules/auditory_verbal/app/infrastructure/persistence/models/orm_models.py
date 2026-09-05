import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.persistence.database.base import Base


class ORMBase:
    """Base mixin for all SQLAlchemy models with standard security, audit, and locking fields."""

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
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

    __mapper_args__ = {
        "version_id_col": version,
        "version_id_generator": lambda val: (val or 0) + 1,
    }


class AssessmentORM(ORMBase, Base):
    __tablename__ = "assessments"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    __mapper_args__ = {
        "version_id_col": ORMBase.version,
    }


class AssessmentSessionORM(ORMBase, Base):
    __tablename__ = "assessment_sessions"

    candidate_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    scenario_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="INITIALIZED")
    current_stage: Mapped[str] = mapped_column(String(50), nullable=False, default="DEVICE_CHECK")
    completed_stages: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __mapper_args__ = {
        "version_id_col": ORMBase.version,
    }


class ScenarioORM(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    narrative: Mapped[str] = mapped_column(String(4000), nullable=False)
    audio_asset: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    listening_questions: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    speaking_prompts: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    follow_up_definitions: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    construct_mappings: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    metadata_json: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict, nullable=False)

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
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

    __mapper_args__ = {
        "version_id_col": version,
    }


class TranscriptORM(ORMBase, Base):
    __tablename__ = "transcripts"

    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    prompt_id: Mapped[str] = mapped_column(String(255), nullable=False)
    transcript_text: Mapped[str] = mapped_column(String(4000), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    is_final: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __mapper_args__ = {
        "version_id_col": ORMBase.version,
    }


class BehavioralEvidenceORM(ORMBase, Base):
    __tablename__ = "behavioral_evidences"

    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    prompt_id: Mapped[str] = mapped_column(String(255), nullable=False)
    construct: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    quote: Mapped[str] = mapped_column(String(1000), nullable=False)
    indicator_description: Mapped[str] = mapped_column(String(1000), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.95)
    polarity: Mapped[str] = mapped_column(String(50), nullable=False, default="POSITIVE")
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False, default="VERBATIM_QUOTE")

    __mapper_args__ = {
        "version_id_col": ORMBase.version,
    }


class ConstructEvaluationORM(ORMBase, Base):
    __tablename__ = "construct_evaluations"

    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    construct_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    construct_description: Mapped[str] = mapped_column(String(500), nullable=False)
    behavioral_summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    supporting_evidence_ids: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    evaluation_narrative: Mapped[str] = mapped_column(String(4000), nullable=False)
    evaluation_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.95)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, default="gemini-1.5-pro")

    __mapper_args__ = {
        "version_id_col": ORMBase.version,
    }


class AssessmentScoreORM(ORMBase, Base):
    __tablename__ = "assessment_scores"

    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    scenario_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    construct_scores: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    composite_scores: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    reliability_summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    assessment_decision: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    scoring_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    pipeline_version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0.0")

    __mapper_args__ = {
        "version_id_col": ORMBase.version,
    }


class AssessmentReportORM(ORMBase, Base):
    __tablename__ = "assessment_reports"

    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    candidate_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    scenario_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    overall_cognitive_index: Mapped[float] = mapped_column(Float, nullable=False)
    listening_metrics: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    speaking_metrics: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    construct_scores: Mapped[Dict[str, float]] = mapped_column(JSON, default=dict, nullable=False)
    evidence_summary: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    recommendations: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    __mapper_args__ = {
        "version_id_col": ORMBase.version,
    }


class PromptAuditORM(ORMBase, Base):
    __tablename__ = "prompt_audits"

    prompt_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    template_text: Mapped[str] = mapped_column(String(4000), nullable=False)
    rendered_text: Mapped[str] = mapped_column(String(4000), nullable=False)
    prompt_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    model_parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    response_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __mapper_args__ = {
        "version_id_col": ORMBase.version,
    }


class ResearchSnapshotORM(ORMBase, Base):
    __tablename__ = "research_snapshots"

    research_metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    analytics_metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    validation_metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    monitoring_metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    experiment_results: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    platform_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __mapper_args__ = {
        "version_id_col": ORMBase.version,
    }


class PlatformEventORM(ORMBase, Base):
    __tablename__ = "platform_events"

    event_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    correlation_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __mapper_args__ = {
        "version_id_col": ORMBase.version,
    }
