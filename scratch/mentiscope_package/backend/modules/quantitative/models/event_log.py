from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import DateTime

from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped

from modules.quantitative.database.base import Base


class EventLog(Base):

    __tablename__ = "event_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    student_id: Mapped[str] = mapped_column(String(50))

    session_id: Mapped[str] = mapped_column(String(50))

    construct: Mapped[str] = mapped_column(String(30))

    task_id: Mapped[str] = mapped_column(String(30))

    item_id: Mapped[str] = mapped_column(String(50))

    event_type: Mapped[str] = mapped_column(String(30))

    response: Mapped[str] = mapped_column(String(100))

    correct: Mapped[bool]

    reaction_time_ms: Mapped[int]

    error_type: Mapped[str | None] = mapped_column(String(100),nullable=True,)
    difficulty_level: Mapped[int]

    event_metadata: Mapped[dict] = mapped_column(JSON)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )