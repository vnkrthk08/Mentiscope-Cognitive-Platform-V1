import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.persistence.database.base import Base


class ConstructEvaluationORM(Base):
    __tablename__ = "cee_construct_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    behavior_evidence_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    candidate_id: Mapped[str] = mapped_column(String(255), nullable=False)
    assessment_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    scenario_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)

    construct_profiles: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    overall_evaluation_confidence: Mapped[float] = mapped_column(Float, nullable=False)
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


class ConstructMetricORM(Base):
    __tablename__ = "construct_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    evaluation_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    construct_coverage: Mapped[int] = mapped_column(Integer, nullable=False)
    evidence_utilization: Mapped[float] = mapped_column(Float, nullable=False)
    average_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    mapping_conflicts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
pre=1.0
