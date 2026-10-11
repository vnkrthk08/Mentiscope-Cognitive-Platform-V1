from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class GcStartRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    studentId: Optional[str] = None
    student_id: Optional[str] = None

class GcStartResponse(BaseModel):
    status: str
    sessionId: str
    moduleId: str = "gc"
    moduleName: str = "Crystallized Intelligence (Gc)"
    construct: str = "Knowledge Application & Domain Synthesis"
    totalQuestions: int
    questions: List[Dict[str, Any]]

class GcAnswerRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    questionId: Optional[str] = None
    question_id: Optional[str] = None
    answer: str
    durationMs: Optional[int] = 0
    duration_ms: Optional[int] = 0

class GcAnswerResponse(BaseModel):
    status: str
    isCorrect: bool
    feedback: str

class GcFinishRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    studentId: Optional[str] = None
    student_id: Optional[str] = None
    answers: Optional[List[Dict[str, Any]]] = None

class GcFinishResponse(BaseModel):
    status: str
    sessionId: str
    scorePercentage: float
    metrics: Dict[str, Any]
