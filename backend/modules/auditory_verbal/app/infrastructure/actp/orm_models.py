"""
SQLAlchemy ORM models for ACTP (Audit, Compliance & Traceability Platform).

Table prefix: actp_
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from sqlalchemy import String, Integer, Float, DateTime, JSON, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.persistence.database.base import Base


class AuditSessionORM(Base):
    """Audit Session container model."""

    __tablename__ = "actp_audit_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    candidate_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    scenario_id: Mapped[str] = mapped_column(String(255), nullable=False)
    session_status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")
    total_events: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditEventORM(Base):
    """Immutable Audit Event record."""

    __tablename__ = "actp_audit_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    assessment_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    stage_name: Mapped[str] = mapped_column(String(100), nullable=False)

    invocation_details: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    payload_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class DecisionRecordORM(Base):
    """Reproducible Decision Record model."""

    __tablename__ = "actp_decision_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    decision_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    assessment_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    decision_type: Mapped[str] = mapped_column(String(100), nullable=False)

    input_data_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    output_decision_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    score_explanations_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    evidence_references_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    pipeline_invocation_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    reproducible_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class ACTPMetricORM(Base):
    """Audit operational metrics log."""

    __tablename__ = "actp_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    value_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
