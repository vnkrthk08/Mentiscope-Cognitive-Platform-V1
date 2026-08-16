from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from modules.quantitative.database.base import Base


class StudentResponse(Base):
    """
    Stores every response submitted by the student along with
    behavioural telemetry for analytics.
    """

    __tablename__ = "student_responses"

    # ---------------------------------------------------------
    # Primary Key
    # ---------------------------------------------------------

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    # ---------------------------------------------------------
    # Session Information
    # ---------------------------------------------------------

    session_id: Mapped[str] = mapped_column(
        ForeignKey("assessment_sessions.id"),
        nullable=False,
        index=True,
    )

    question_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    module_name: Mapped[str] = mapped_column(
        String(50),
        default="GQ",
    )

    difficulty_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    # ---------------------------------------------------------
    # Student Answer
    # ---------------------------------------------------------

    response: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    hint_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    # ---------------------------------------------------------
    # Timing Metrics
    # ---------------------------------------------------------

    reaction_time_ms: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    hover_duration_ms: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    idle_time_ms: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    question_load_time_ms: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    total_pause_time_ms: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # ---------------------------------------------------------
    # Mouse Behaviour
    # ---------------------------------------------------------

    drag_distance: Mapped[float] = mapped_column(
        Float,
        default=0,
    )

    mouse_click_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # ---------------------------------------------------------
    # Interaction Behaviour
    # ---------------------------------------------------------

    answer_changes: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    confidence_score: Mapped[int] = mapped_column(
        Integer,
        default=3,
    )

    focus_lost_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    pause_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    keyboard_event_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # ---------------------------------------------------------
    # Future Telemetry
    # ---------------------------------------------------------

    extra_metrics: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    # ---------------------------------------------------------
    # Timestamp
    # ---------------------------------------------------------

    answered_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )