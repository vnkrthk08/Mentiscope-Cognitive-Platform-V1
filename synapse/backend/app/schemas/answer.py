"""
==========================================================
Answer Schemas
==========================================================
"""

from pydantic import BaseModel
from pydantic import Field


# ---------------------------------------------------------
# Telemetry Metrics
# ---------------------------------------------------------

class QuestionMetrics(BaseModel):

    reaction_time_ms: int

    hover_duration_ms: int = 0

    idle_time_ms: int = 0

    drag_distance: float = 0

    answer_changes: int = 0

    confidence_score: int = Field(default=3, ge=1, le=5)

    attempt_number: int = 1

    difficulty_level: int = 1

    module_name: str = "GQ"

    hint_used: bool = False


# ---------------------------------------------------------
# Incoming Request
# ---------------------------------------------------------

class AnswerRequest(BaseModel):

    session_id: str

    question_id: str

    response: str

    metrics: QuestionMetrics


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

    correct: bool

    next_level: int

    next_question: NextQuestion