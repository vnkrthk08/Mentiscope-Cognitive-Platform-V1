import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.persistence.database.base import Base


class AssessmentResultORM(Base):
    __tablename__ = "asr_assessment_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    candidate_id: Mapped[str] = mapped_column(String(255), nullable=False)
    assessment_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    construct_evaluation_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)

    framework_results: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    overall_scores: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    overall_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    scoring_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class AssessmentReportORM(Base):
    __tablename__ = "asr_assessment_reports"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    assessment_result_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    candidate_id: Mapped[str] = mapped_column(String(255), nullable=False)
    assessment_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)

    assessment_summary: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    framework_results: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    report_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ScoringPolicyORM(Base):
    __tablename__ = "asr_scoring_policies"

    id: Mapped[str] = mapped_column(primary_key=True)
    framework: Mapped[str] = mapped_column(String(50), nullable=False)
    policy_name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    weight_configuration: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False)
    normalization_method: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_method: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class AssessmentMetricORM(Base):
    __tablename__ = "asr_assessment_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    scoring_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    report_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    framework_coverage: Mapped[int] = mapped_column(Integer, nullable=False)
    average_score: Mapped[float] = mapped_column(Float, nullable=False)
    average_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_utilization: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
pre=1.0
