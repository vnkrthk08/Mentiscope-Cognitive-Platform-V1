"""
==========================================================
Analytics Model
==========================================================
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from modules.quantitative.database.base import Base


class Analytics(Base):

    __tablename__ = "analytics"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    session_id: Mapped[str] = mapped_column(
        ForeignKey("assessment_sessions.id"),
        nullable=False,
        unique=True,
    )

    accuracy: Mapped[float] = mapped_column(Float)

    average_response_time: Mapped[float] = mapped_column(Float)

    hint_dependency: Mapped[float] = mapped_column(Float)

    persistence_score: Mapped[float] = mapped_column(Float)

    learning_curve: Mapped[dict] = mapped_column(JSON)

    numerical_reasoning_profile: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )