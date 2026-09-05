import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.persistence.database.base import Base


class BehaviorEvidenceORM(Base):
    __tablename__ = "behavior_evidences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transcript_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    prompt_execution_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    candidate_id: Mapped[str] = mapped_column(String(255), nullable=False)
    assessment_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    scenario_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)

    construct_candidates: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    behavior_observations: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    evidence_sources: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)

    overall_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class BehaviorMetricORM(Base):
    __tablename__ = "behavior_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transcript_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False)
    average_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    duplicate_rate: Mapped[float] = mapped_column(Float, nullable=False)
    validation_failures: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
