from dataclasses import dataclass, field
from app.domain.events.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class SpeechProcessingStarted(DomainEvent):
    session_id: str
    prompt_id: str
    audio_url: str


@dataclass(frozen=True, kw_only=True)
class AudioValidated(DomainEvent):
    session_id: str
    audio_url: str
    duration_seconds: float


@dataclass(frozen=True, kw_only=True)
class AudioPreprocessed(DomainEvent):
    session_id: str
    audio_url: str
    sample_rate: int
    channels: int


@dataclass(frozen=True, kw_only=True)
class ProviderSelected(DomainEvent):
    session_id: str
    provider_name: str


@dataclass(frozen=True, kw_only=True)
class TranscriptionStarted(DomainEvent):
    session_id: str
    provider_name: str


@dataclass(frozen=True, kw_only=True)
class TranscriptionCompleted(DomainEvent):
    session_id: str
    provider_name: str
    confidence: float
    text_length: int


@dataclass(frozen=True, kw_only=True)
class RetryAttempted(DomainEvent):
    session_id: str
    provider_name: str
    attempt: int
    reason: str


@dataclass(frozen=True, kw_only=True)
class ProcessingCompleted(DomainEvent):
    session_id: str
    prompt_id: str
    overall_confidence: float
    duration_seconds: float


@dataclass(frozen=True, kw_only=True)
class ProcessingFailed(DomainEvent):
    session_id: str
    reason: str
