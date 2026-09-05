from dataclasses import dataclass, field
from app.domain.events.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class AudioStarted(DomainEvent):
    session_id: str
    audio_url: str
    duration_seconds: float


@dataclass(frozen=True, kw_only=True)
class ReplayRequested(DomainEvent):
    session_id: str
    item_id: str
    requested_replay_number: int


@dataclass(frozen=True, kw_only=True)
class ReplayCompleted(DomainEvent):
    session_id: str
    item_id: str
    remaining_replays: int


@dataclass(frozen=True, kw_only=True)
class QuestionPresented(DomainEvent):
    session_id: str
    question_id: str
    question_index: int
    total_questions: int


@dataclass(frozen=True, kw_only=True)
class AnswerSubmitted(DomainEvent):
    session_id: str
    question_id: str
    selected_option_index: int
    is_correct: bool
    response_time_ms: int


@dataclass(frozen=True, kw_only=True)
class ListeningCancelled(DomainEvent):
    session_id: str
    reason: str


@dataclass(frozen=True, kw_only=True)
class ListeningFailed(DomainEvent):
    session_id: str
    reason: str
