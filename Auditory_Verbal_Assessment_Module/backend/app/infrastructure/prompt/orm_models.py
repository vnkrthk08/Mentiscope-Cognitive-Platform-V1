import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.persistence.database.base import Base


class PromptExecutionORM(Base):
    __tablename__ = "prompt_executions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transcript_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    prompt_template: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), nullable=False)
    assembled_context: Mapped[str] = mapped_column(String(8000), nullable=False)

    provider_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    token_usage: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    execution_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class PromptTemplateORM(Base):
    __tablename__ = "prompt_templates"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_text: Mapped[str] = mapped_column(String(4000), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    required_variables: Mapped[str] = mapped_column(String(500), nullable=False)  # Comma separated


class PromptResponseORM(Base):
    __tablename__ = "prompt_responses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    execution_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True, unique=True)
    content_raw: Mapped[str] = mapped_column(String(16000), nullable=False)
    content_normalized: Mapped[str] = mapped_column(String(16000), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class PromptMetricORM(Base):
    __tablename__ = "prompt_metrics"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    provider_name: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    success: Mapped[bool] = mapped_column(nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
