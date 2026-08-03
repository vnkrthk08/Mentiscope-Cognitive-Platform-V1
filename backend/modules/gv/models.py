from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class GvSession(Base):
    __tablename__ = "gv_sessions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ongoing','completed','abandoned','expired')",
            name="ck_gv_sessions_status",
        ),
    )

    session_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    student_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    module_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    module_name: Mapped[str] = mapped_column(String(128), nullable=False)
    construct: Mapped[str] = mapped_column(String(128), nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ongoing")
    current_item_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    end_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    item_order: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    session_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class GvAnswer(Base):
    __tablename__ = "gv_answers"
    __table_args__ = (
        UniqueConstraint("session_id", "item_id", "practice", name="uq_gv_answer_session_item_practice"),
        UniqueConstraint("submission_id", name="uq_gv_answer_submission"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    submission_id: Mapped[str] = mapped_column(String(128), nullable=False)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("gv_sessions.session_id", ondelete="CASCADE"), index=True, nullable=False
    )
    item_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    subtest_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    practice: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    response: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_taken_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    selection_changes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rotation_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    placement_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    time_to_first_interaction_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    distractor_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    score_detail: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    device_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class GvEvent(Base):
    __tablename__ = "gv_events"

    event_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    student_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("gv_sessions.session_id", ondelete="CASCADE"), index=True, nullable=False
    )
    module_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    subtest_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    item_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    response: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    time_taken: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    time_since_session_start: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    difficulty_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class GvResult(Base):
    __tablename__ = "gv_results"

    session_id: Mapped[str] = mapped_column(
        ForeignKey("gv_sessions.session_id", ondelete="CASCADE"), primary_key=True
    )
    student_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    module_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    score_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
