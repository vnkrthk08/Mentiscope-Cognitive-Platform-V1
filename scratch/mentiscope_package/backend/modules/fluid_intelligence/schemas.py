from pydantic import BaseModel, Field
from typing import Any

class StartRequest(BaseModel):
    session_id: str = Field(..., validation_alias="sessionId", alias="session_id")
    student_id: str | None = Field(None, validation_alias="studentId", alias="student_id")

    class Config:
        populate_by_name = True

class AnswerRequest(BaseModel):
    session_id: str = Field(..., validation_alias="sessionId", alias="session_id")
    question_id: str = Field(..., validation_alias="questionId", alias="question_id")
    answer: str
    duration_ms: int = Field(0, validation_alias="durationMs", alias="duration_ms")

    class Config:
        populate_by_name = True

class FinishRequest(BaseModel):
    session_id: str = Field(..., validation_alias="sessionId", alias="session_id")
    seed: str | int | None = None

    class Config:
        populate_by_name = True

