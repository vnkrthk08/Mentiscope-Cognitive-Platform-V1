"""
==========================================================
Answer Schemas for Quantitative Ability (Gq)
==========================================================
"""

from typing import Optional, Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Telemetry Metrics
# ---------------------------------------------------------

class QuestionMetrics(BaseModel):
    reaction_time_ms: int = 1500
    hover_duration_ms: int = 0
    idle_time_ms: int = 0
    drag_distance: float = 0
    answer_changes: int = 0
    confidence_score: int = Field(default=3, ge=1, le=5)
    attempt_number: int = 1
    difficulty_level: int = 1
    module_name: str = "GQ"
    hint_used: bool = False

    class Config:
        populate_by_name = True
        extra = "ignore"


# ---------------------------------------------------------
# Incoming Request
# ---------------------------------------------------------

class AnswerRequest(BaseModel):
    session_id: str = Field(..., validation_alias="sessionId", alias="session_id")
    question_id: str = Field(..., validation_alias="questionId", alias="question_id")
    response: Optional[str] = Field(None, validation_alias="answer", alias="response")
    duration_ms: Optional[int] = Field(0, validation_alias="durationMs", alias="duration_ms")
    metrics: Optional[QuestionMetrics] = None

    class Config:
        populate_by_name = True
        extra = "ignore"


# ---------------------------------------------------------
# Next Question
# ---------------------------------------------------------

class NextQuestion(BaseModel):
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


# ---------------------------------------------------------
# Response
# ---------------------------------------------------------

class AnswerResponse(BaseModel):
    correct: bool = True
    isCorrect: bool = True
    status: str = "success"
    feedback: str = "Response recorded."
    next_level: int = 1
    next_question: Optional[Any] = None
    nextQuestion: Optional[Any] = None

    class Config:
        populate_by_name = True
        extra = "ignore"