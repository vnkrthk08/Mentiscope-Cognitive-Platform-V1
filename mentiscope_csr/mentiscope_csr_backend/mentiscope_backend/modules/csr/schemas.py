from pydantic import BaseModel, Field


class StartRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    student_id: str | None = Field(default=None, max_length=64)


class AnswerRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    question_id: str
    answer: str
    duration_ms: int = Field(ge=0)


class FinishRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    # Answers are already recorded by POST /answer. Accepted here only to preserve
    # the shared AssessmentRunner contract without duplicating response rows.
    answers: list[dict] = Field(default_factory=list)
