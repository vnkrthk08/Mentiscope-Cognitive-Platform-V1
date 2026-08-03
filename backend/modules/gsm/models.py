"""
ASAT â€“ Pydantic Request/Response Models

These models define the API contracts for all endpoints.
They are derived from the existing Express request/response bodies
to ensure backward compatibility.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  AUTH MODELS (from routes/auth.js)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class FacultyRegisterRequest(BaseModel):
    fullName: str
    email: str
    username: str
    password: str


class FacultyLoginRequest(BaseModel):
    username: str
    password: str


class FacultyOut(BaseModel):
    facultyId: int
    username: str
    fullName: Optional[str] = None
    email: Optional[str] = None


class FacultyLoginResponse(BaseModel):
    message: str
    faculty: FacultyOut


class FacultyRegisterResponse(BaseModel):
    message: str
    facultyId: int


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  STUDENT MODELS (from routes/students.js)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class StudentCreateRequest(BaseModel):
    fullName: str
    studentId: str
    age: Optional[int] = None
    grade: Optional[str] = None
    school: Optional[str] = None


class StudentCreateResponse(BaseModel):
    studentId: int
    message: str


class StudentListItem(BaseModel):
    studentId: int
    fullName: str
    studentIdNumber: Optional[str] = None
    grade: Optional[str] = None
    age: Optional[int] = None
    school: Optional[str] = None
    createdAt: Optional[datetime] = None
    overall: Optional[float] = None
    completedAt: Optional[datetime] = None


class StudentListResponse(BaseModel):
    students: List[StudentListItem]


class StudentScores(BaseModel):
    sustainedScore: Optional[float] = None
    selectiveScore: Optional[float] = None
    dividedScore: Optional[float] = None
    executiveScore: Optional[float] = None
    overallScore: Optional[float] = None
    percentile: Optional[int] = None
    completedAt: Optional[datetime] = None


class StudentDetailResponse(BaseModel):
    student: Dict[str, Any]
    scores: Dict[str, Any]
    moduleResults: Dict[str, Any]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  SESSION MODELS (from routes/sessions.js)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class SessionCreateRequest(BaseModel):
    studentId: int


class SessionCreateResponse(BaseModel):
    sessionId: int
    sessionUuid: str


class ScoresPayload(BaseModel):
    sustained: Optional[float] = None
    selective: Optional[float] = None
    divided: Optional[float] = None
    executive: Optional[float] = None
    overall: Optional[float] = None
    percentile: Optional[int] = None


class SessionUpdateRequest(BaseModel):
    studentId: int
    scores: Optional[ScoresPayload] = None
    moduleResults: Optional[Dict[str, Any]] = None


class EventItem(BaseModel):
    """Single trial event â€” matches the JS event object shape."""
    construct: Optional[str] = "Attention"
    taskId: Optional[str] = "ASAT"
    itemId: Optional[int] = 0
    stimulus: Optional[str] = ""
    eventType: Optional[str] = "TRIAL"
    response: Optional[str] = ""
    correct: Optional[bool] = False
    reactionTimeMs: Optional[int] = 0
    errorType: Optional[str] = ""
    difficultyLevel: Optional[int] = 1


class EventsBatchRequest(BaseModel):
    studentId: int
    events: List[EventItem]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  MENTISCOPE STANDARD MODELS
#  (from official Technical Development Instructions)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class AssessmentStartRequest(BaseModel):
    """
    Input from MentiScope platform to start an assessment.
    Fields as specified in Section 4 of the instructions.
    """
    student_id: str
    session_id: str
    module_id: Optional[str] = None
    construct: Optional[str] = "Attention"
    difficulty: Optional[str] = "standard"


class AssessmentStartResponse(BaseModel):
    status: str
    session_id: str
    module_id: str
    module_name: str
    construct: str
    total_trials: int = 112  # 28 per module Ã— 4 modules
    modules: List[str] = ["Sustained", "Selective", "Divided", "Executive"]
    start_time: str


class AssessmentAnswerRequest(BaseModel):
    """Log a single trial event via MentiScope standard endpoint."""
    session_id: str
    student_id: str
    item_id: int
    task_id: Optional[str] = None
    stimulus: Optional[str] = None
    response: Optional[str] = None
    correct: Optional[bool] = None
    reaction_time_ms: Optional[int] = None
    event_type: Optional[str] = "TRIAL"
    error_type: Optional[str] = None
    difficulty_level: Optional[int] = 1


class AssessmentAnswerResponse(BaseModel):
    status: str = "recorded"
    item_id: int


class AssessmentFinishRequest(BaseModel):
    """Submit final scores via MentiScope standard endpoint."""
    session_id: str
    student_id: str
    scores: Optional[ScoresPayload] = None
    module_results: Optional[Dict[str, Any]] = None


class AssessmentMetrics(BaseModel):
    """
    Module-specific metrics returned inside the 'metrics' object.
    As specified in Section 5 & 6 of the instructions.
    """
    sustained_score: Optional[float] = None
    selective_score: Optional[float] = None
    divided_score: Optional[float] = None
    executive_score: Optional[float] = None
    overall_score: Optional[float] = None
    percentile: Optional[int] = None
    rt_variability: Optional[float] = None
    fatigue_slope: Optional[float] = None
    adaptation_speed: Optional[float] = None
    impulsivity_index: Optional[float] = None
    attention_stability: Optional[float] = None
    recovery_after_errors: Optional[float] = None


class AssessmentResultResponse(BaseModel):
    """
    MentiScope standard output format.
    Mandatory metadata + module-specific metrics object.
    As specified in Sections 5 & 6 of the instructions.
    """
    student_id: str
    session_id: str
    module_id: str
    module_name: str
    construct: str
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    completion_time: Optional[int] = None  # seconds
    timestamp: Optional[str] = None
    metrics: AssessmentMetrics


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  GENERIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str
