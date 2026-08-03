"""
==========================================================
Assessment Result Model
==========================================================
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base


class AssessmentResult(Base):

    __tablename__ = "assessment_results"

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

    raw_score: Mapped[float] = mapped_column(Float)

    normalized_score: Mapped[float] = mapped_column(Float)

    percentile: Mapped[float] = mapped_column(Float)

    confidence_score: Mapped[float] = mapped_column(Float)

    sub_scores: Mapped[dict] = mapped_column(JSON)

    recommendations: Mapped[dict] = mapped_column(JSON)

    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )