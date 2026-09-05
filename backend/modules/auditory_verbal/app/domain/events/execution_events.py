from dataclasses import dataclass, field
from app.domain.events.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class ExecutionStarted(DomainEvent):
    session_id: str
    stage: str


@dataclass(frozen=True, kw_only=True)
class ExecutionPaused(DomainEvent):
    session_id: str
    stage: str
    reason: str


@dataclass(frozen=True, kw_only=True)
class ExecutionResumed(DomainEvent):
    session_id: str
    stage: str


@dataclass(frozen=True, kw_only=True)
class ExecutionTimedOut(DomainEvent):
    session_id: str
    item_id: str
    elapsed_seconds: float


@dataclass(frozen=True, kw_only=True)
class ExecutionCancelled(DomainEvent):
    session_id: str
    reason: str


@dataclass(frozen=True, kw_only=True)
class QuestionStarted(DomainEvent):
    session_id: str
    question_id: str
    question_index: int


@dataclass(frozen=True, kw_only=True)
class QuestionCompleted(DomainEvent):
    session_id: str
    question_id: str
    selected_option_index: int
    response_time_ms: int


@dataclass(frozen=True, kw_only=True)
class PromptStarted(DomainEvent):
    session_id: str
    prompt_id: str
    prompt_index: int


@dataclass(frozen=True, kw_only=True)
class PromptCompleted(DomainEvent):
    session_id: str
    prompt_id: str
    audio_file_url: str
    duration_seconds: float


@dataclass(frozen=True, kw_only=True)
class ReplayUsed(DomainEvent):
    session_id: str
    item_id: str
    replay_number: int
    max_replays: int


@dataclass(frozen=True, kw_only=True)
class CheckpointCreated(DomainEvent):
    session_id: str
    checkpoint_id: str
    stage: str


@dataclass(frozen=True, kw_only=True)
class ExecutionCompleted(DomainEvent):
    session_id: str
    stage: str
    duration_seconds: float
