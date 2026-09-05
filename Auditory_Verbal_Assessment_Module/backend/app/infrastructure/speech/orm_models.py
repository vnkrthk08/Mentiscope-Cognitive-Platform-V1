import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.persistence.database.base import Base


class TranscriptORM(Base):
    __tablename__ = "speech_transcripts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True, unique=True)
    session_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    assessment_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    candidate_id: Mapped[str] = mapped_column(String(255), nullable=False)

    provider_result: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    language: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    confidence_score: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    transcript_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    transcript_text: Mapped[str] = mapped_column(String(16000), nullable=False)
    
    word_timestamps: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    speaker_segments: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    
    processing_duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class TranscriptionJobORM(Base):
    __tablename__ = "transcription_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class SpeechMetricORM(Base):
    __tablename__ = "speech_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    provider_name: Mapped[str] = mapped_column(String(50), nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    success: Mapped[bool] = mapped_column(nullable=False)
    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    words_count: Mapped[int] = mapped_column(Integer, nullable=False)
    words_per_second: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
