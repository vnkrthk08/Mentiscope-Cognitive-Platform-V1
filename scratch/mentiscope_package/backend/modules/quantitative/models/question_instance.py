"""
==========================================================
Question Instance Model
==========================================================
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from modules.quantitative.database.base import Base


class QuestionInstance(Base):

    __tablename__ = "question_instances"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("assessment_sessions.id"),
        nullable=False,
        index=True,
    )

    # NEW
    question_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    template_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    module: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    difficulty: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    question_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    correct_answer: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    presented_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )