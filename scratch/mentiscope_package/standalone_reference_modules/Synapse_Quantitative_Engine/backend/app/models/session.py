"""
==========================================================
Assessment Session Model
==========================================================
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.enums import AssessmentStatus
from app.database.base import Base


class AssessmentSession(Base):
    """
    Stores one assessment session.

    Every assessment attempt creates exactly one session.
    """

    __tablename__ = "assessment_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    student_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    session_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    module_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    construct: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    current_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    status: Mapped[AssessmentStatus] = mapped_column(
        SqlEnum(AssessmentStatus),
        default=AssessmentStatus.PENDING,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )