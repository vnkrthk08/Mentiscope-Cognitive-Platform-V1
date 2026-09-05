from dataclasses import dataclass, field
from typing import Dict, Any
from app.domain.events.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class PromptPresented(DomainEvent):
    session_id: str
    prompt_id: str
    prompt_index: int
    total_prompts: int


@dataclass(frozen=True, kw_only=True)
class RecordingStarted(DomainEvent):
    session_id: str
    prompt_id: str
    max_seconds: float


@dataclass(frozen=True, kw_only=True)
class RecordingPaused(DomainEvent):
    session_id: str
    prompt_id: str


@dataclass(frozen=True, kw_only=True)
class RecordingResumed(DomainEvent):
    session_id: str
    prompt_id: str


@dataclass(frozen=True, kw_only=True)
class RecordingStopped(DomainEvent):
    session_id: str
    prompt_id: str
    duration_seconds: float


@dataclass(frozen=True, kw_only=True)
class RecordingDiscarded(DomainEvent):
    session_id: str
    prompt_id: str
    reason: str


@dataclass(frozen=True, kw_only=True)
class ResponseCaptured(DomainEvent):
    session_id: str
    prompt_id: str
    audio_file_url: str
    duration_seconds: float
    metadata: Dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class PromptCompleted(DomainEvent):
    session_id: str
    prompt_id: str


@dataclass(frozen=True, kw_only=True)
class SpeakingCancelled(DomainEvent):
    session_id: str
    reason: str


@dataclass(frozen=True, kw_only=True)
class SpeakingFailed(DomainEvent):
    session_id: str
    reason: str
