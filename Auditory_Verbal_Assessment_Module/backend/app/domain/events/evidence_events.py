from dataclasses import dataclass, field
from app.domain.events.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class EvidenceExtractionStarted(DomainEvent):
    session_id: str
    scenario_id: str


@dataclass(frozen=True, kw_only=True)
class TranscriptLoaded(DomainEvent):
    session_id: str
    transcript_text_len: int


@dataclass(frozen=True, kw_only=True)
class PromptRequested(DomainEvent):
    session_id: str
    prompt_id: str


@dataclass(frozen=True, kw_only=True)
class EvidenceValidated(DomainEvent):
    session_id: str
    evidence_count: int


@dataclass(frozen=True, kw_only=True)
class EvidenceStored(DomainEvent):
    session_id: str
    evidence_set_id: str


@dataclass(frozen=True, kw_only=True)
class EvidenceExtractionCompleted(DomainEvent):
    session_id: str
    evidence_count: int
    overall_confidence: float


@dataclass(frozen=True, kw_only=True)
class EvidenceExtractionFailed(DomainEvent):
    session_id: str
    reason: str
