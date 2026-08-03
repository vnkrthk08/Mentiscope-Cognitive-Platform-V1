from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.modules.gv.config import MODULE_CONFIG, REQUIRED_EVENT_TYPES


class LaunchContext(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    student_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128)
    module_id: Literal["GV_VISUAL_PROCESSING_BATTERY"]
    module_name: str = MODULE_CONFIG.module_name
    construct: Literal["CHC_Gv_Visual_Processing"]
    difficulty: int = Field(ge=MODULE_CONFIG.min_difficulty, le=MODULE_CONFIG.max_difficulty)
    access_token: str | None = Field(default=None, exclude=True)


class ClientEvent(BaseModel):
    event_id: str = Field(min_length=1, max_length=128)
    student_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128)
    module_id: Literal["GV_VISUAL_PROCESSING_BATTERY"]
    subtest_id: str | None = Field(default=None, max_length=64)
    item_id: str | None = Field(default=None, max_length=128)
    event_type: str = Field(min_length=1, max_length=64)
    response: dict[str, Any] = Field(default_factory=dict)
    correct: bool | None = None
    time_taken: float = Field(default=0, ge=0)
    time_since_session_start: float = Field(default=0, ge=0)
    attempt_number: int = Field(default=1, ge=1, le=100)
    difficulty_level: int = Field(default=1, ge=1, le=5)
    timestamp: datetime

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        if value not in REQUIRED_EVENT_TYPES:
            raise ValueError(f"Unsupported Gv event type: {value}")
        return value


class StartRequest(LaunchContext):
    pass


class StartResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: Literal["new", "resumed", "completed"]
    student_id: str
    session_id: str
    module_id: str
    module_name: str
    construct: str
    version: str
    difficulty: int
    start_time: datetime
    current_item_index: int
    practice_items: list[dict[str, Any]]
    assessment_items: list[dict[str, Any]]
    completed_result: dict[str, Any] | None = None


class AnswerRequest(BaseModel):
    submission_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128)
    item_id: str = Field(min_length=1, max_length=128)
    response: dict[str, Any]
    practice: bool = False
    time_taken_ms: int = Field(default=0, ge=0, le=3_600_000)
    attempt_number: int = Field(default=1, ge=1, le=100)
    selection_changes: int = Field(default=0, ge=0, le=1000)
    rotation_attempts: int = Field(default=0, ge=0, le=1000)
    placement_attempts: int = Field(default=0, ge=0, le=1000)
    time_to_first_interaction_ms: int | None = Field(default=None, ge=0, le=3_600_000)
    device_metadata: dict[str, Any] = Field(default_factory=dict)
    events: list[ClientEvent] = Field(default_factory=list)


class PracticeFeedback(BaseModel):
    correct: bool
    message: str


class AnswerResponse(BaseModel):
    accepted: bool
    duplicate: bool = False
    practice_feedback: PracticeFeedback | None = None
    next_step: Literal["next_item", "finish", "already_completed"]
    current_item_index: int


class FinishRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    events: list[ClientEvent] = Field(default_factory=list)


class Metrics(BaseModel):
    raw_score: float
    accuracy: float
    visualization_vz: float | None
    spatial_relations_sr: float | None
    visual_closure_cs: float | None
    flexibility_of_closure_cf: float | None
    spatial_scanning_ss: float | None
    visual_memory_mv: float | None
    mental_rotation_accuracy: float | None
    paper_folding_accuracy: float | None
    hidden_figures_accuracy: float | None
    mystery_map_accuracy: float | None
    first_attempt_accuracy: float
    correction_count: int
    average_response_time: float
    distractor_selection_rate: float
    rotation_attempts_total: int
    mirror_confusion_rate: float | None
    strategy_error_control: float
    efficiency_score: float
    confidence_score: float


class FinalResult(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    student_id: str
    session_id: str
    module_id: str
    module_name: str
    construct: str
    status: Literal["Completed"]
    start_time: datetime
    end_time: datetime
    completion_time: float
    timestamp: datetime
    metrics: Metrics
