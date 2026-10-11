from pydantic import BaseModel, Field
from typing import Optional, List, Any

class FinishRequest(BaseModel):
    session_id: Optional[str] = Field(None, validation_alias="sessionId", alias="session_id")
    student_id: Optional[str] = Field(None, validation_alias="studentId", alias="student_id")
    answers: Optional[List[Any]] = None

    class Config:
        populate_by_name = True
        extra = "ignore"