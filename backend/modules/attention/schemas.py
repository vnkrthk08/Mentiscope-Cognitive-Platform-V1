from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class AttentionStartRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    studentId: Optional[str] = None
    student_id: Optional[str] = None

class AttentionStartResponse(BaseModel):
    status: str
    sessionId: str
    moduleId: str = "attention"
    moduleName: str = "Adaptive Shape Attention Task (ASAT)"
    construct: str = "Attention & Executive Control"
    submodules: List[str] = ["sustained", "selective", "divided", "executive"]
    totalTrials: int = 112

class AttentionAnswerRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    submodule: str  # sustained, selective, divided, executive
    trialIndex: int
    stimulus: Optional[str] = ""
    response: Optional[str] = ""
    isCorrect: bool
    reactionTimeMs: float

class AttentionAnswerResponse(BaseModel):
    status: str
    recorded: bool

class AttentionFinishRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    studentId: Optional[str] = None
    student_id: Optional[str] = None
    submoduleScores: Optional[Dict[str, float]] = None
    moduleResults: Optional[Dict[str, Any]] = None

class AttentionFinishResponse(BaseModel):
    status: str
    sessionId: str
    scorePercentage: float
    percentile: float
    metrics: Dict[str, Any]
