import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.persistence.database.base import Base


class AudioAssetORM(Base):
    __tablename__ = "audio_assets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    assessment_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    candidate_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    processing_status: Mapped[str] = mapped_column(String(50), nullable=False, default="UPLOADING")

    # JSON mappings for value objects
    storage_location: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    audio_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    validation_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    provenance: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UploadAuditORM(Base):
    __tablename__ = "upload_audits"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[str] = mapped_column(String(512), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
