"""
==========================================================
Session Schemas
==========================================================
"""

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field


# ---------------------------------------------------------
# Incoming Request
# ---------------------------------------------------------

class SessionStartRequest(BaseModel):

    student_id: str = Field(...)

    session_id: str = Field(...)

    module_id: str = Field(...)

    construct: str = Field(...)

    difficulty: int = Field(default=1)


# ---------------------------------------------------------
# Response
# ---------------------------------------------------------



class QuestionResponse(BaseModel):

    question_id: str

    template_id: str

    module: str

    difficulty: int

    story: str

    question: str

    options: list

    correct_answer: str

    hint: str

    data: dict | None = None

class SessionStartResponse(BaseModel):

    assessment_id: str

    student_id: str

    session_id: str

    status: str

    started_at: datetime

    question: QuestionResponse