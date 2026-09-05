"""
SQLAlchemy ORM models for POSRP (Platform Operations & Site Reliability Platform).

Table prefix: posrp_
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import String, Integer, Float, DateTime, JSON, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.database.base import Base


class ConfigurationProfileORM(Base):
    """Environment configuration profile model."""

    __tablename__ = "posrp_configuration_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    profile_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    config_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    config_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class BackupJobORM(Base):
    """Backup job record model."""

    __tablename__ = "posrp_backup_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    backup_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    initiated_by: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    target_path: Mapped[str] = mapped_column(String(500), nullable=True, default="")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    checksum: Mapped[str] = mapped_column(String(64), nullable=True, default="")
    error_message: Mapped[str] = mapped_column(Text, nullable=True, default="")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class RestoreJobORM(Base):
    """Restore job record model."""

    __tablename__ = "posrp_restore_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    backup_job_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    restore_type: Mapped[str] = mapped_column(String(50), nullable=False)
    initiated_by: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    simulation_result: Mapped[str] = mapped_column(String(50), nullable=True, default="")
    error_message: Mapped[str] = mapped_column(Text, nullable=True, default="")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class AlertRuleORM(Base):
    """Operational alert rule definition model."""

    __tablename__ = "posrp_alert_rules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    condition: Mapped[str] = mapped_column(String(20), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="WARNING")
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=300)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class AlertEventORM(Base):
    """Triggered alert event model."""

    __tablename__ = "posrp_alert_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    rule_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="OPEN", index=True)
    resolution_note: Mapped[str] = mapped_column(Text, nullable=True, default="")
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class MaintenanceWindowORM(Base):
    """Scheduled maintenance window model."""

    __tablename__ = "posrp_maintenance_windows"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    scheduled_by: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=True, default="")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="SCHEDULED")
    affected_services: Mapped[str] = mapped_column(String(255), nullable=False, default="ALL")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class POSRPMetricORM(Base):
    """POSRP operational metrics log."""

    __tablename__ = "posrp_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    metric_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    value_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
