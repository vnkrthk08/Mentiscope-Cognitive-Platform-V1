"""
==========================================================
Event Schemas
==========================================================
"""

from datetime import datetime
from pydantic import BaseModel


class EventCreate(BaseModel):

    student_id: str

    session_id: str

    construct: str

    task_id: str

    item_id: str

    event_type: str

    response: str

    correct: bool

    reaction_time_ms: int

    error_type: str | None = None

    difficulty_level: int

    hint_used: bool = False


class EventResponse(BaseModel):

    id: str

    timestamp: datetime

    event_type: str

    correct: bool