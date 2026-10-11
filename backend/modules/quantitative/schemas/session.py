"""
==========================================================
Session Schemas
==========================================================
"""

from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel
from pydantic import Field


# ---------------------------------------------------------
# Incoming Request
# ---------------------------------------------------------

class SessionStartRequest(BaseModel):
    student_id: str = Field(default="stud_candidate", validation_alias="studentId", alias="student_id")
    session_id: str = Field(..., validation_alias="sessionId", alias="session_id")
    module_id: str = Field(default="gq", validation_alias="moduleId", alias="module_id")
    construct: str = Field(default="Quantitative Reasoning", validation_alias="construct", alias="construct")
    difficulty: int = Field(default=1)

    class Config:
        populate_by_name = True
        extra = "ignore"


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

class SessionStartResponse(BaseModel):
    status: str = "success"
    assessment_id: Optional[str] = None
    student_id: Optional[str] = Field(None, validation_alias="studentId", alias="student_id")
    session_id: Optional[str] = Field(None, validation_alias="sessionId", alias="session_id")
    started_at: Optional[datetime] = None
    totalQuestions: Optional[int] = Field(None, validation_alias="totalQuestions", alias="total_questions")
    questions: Optional[list] = None
    question: Optional[Any] = None

    class Config:
        populate_by_name = True
        extra = "ignore"