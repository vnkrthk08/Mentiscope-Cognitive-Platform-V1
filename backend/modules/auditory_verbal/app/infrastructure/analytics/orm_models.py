"""
SQLAlchemy ORM models for RAIP (Research Analytics & Insights Platform).

Table prefix: raip_
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import String, Integer, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.persistence.database.base import Base


class AnalyticsSnapshotORM(Base):
    """Cached analytics snapshot model."""

    __tablename__ = "raip_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    snapshot_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    time_window: Mapped[str] = mapped_column(String(50), nullable=False, default="all_time")

    assessments_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    frameworks_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    evidence_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    research_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    platform_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class AnalyticsTrendORM(Base):
    """Time-series metrics history points."""

    __tablename__ = "raip_trends"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    metric_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # assessment, framework, platform
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    date_bucket: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
