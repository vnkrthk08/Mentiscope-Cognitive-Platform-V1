"""
==========================================================
Question Template Model
==========================================================
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class QuestionTemplate(Base):
    """
    Stores all assessment templates.

    One template can generate many question variants.
    """

    __tablename__ = "question_templates"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    template_id: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    module: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    family: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    difficulty: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    template_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )