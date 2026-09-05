from dataclasses import dataclass, field
from app.domain.events.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class ConstructEvaluationStarted(DomainEvent):
    session_id: str
    scenario_id: str


@dataclass(frozen=True, kw_only=True)
class EvidenceLoaded(DomainEvent):
    session_id: str
    evidence_count: int


@dataclass(frozen=True, kw_only=True)
class EvaluationPromptRequested(DomainEvent):
    session_id: str
    prompt_id: str


@dataclass(frozen=True, kw_only=True)
class EvaluationPromptCompleted(DomainEvent):
    session_id: str
    prompt_id: str
    latency_ms: int


@dataclass(frozen=True, kw_only=True)
class ConstructValidated(DomainEvent):
    session_id: str
    construct_count: int


@dataclass(frozen=True, kw_only=True)
class EvaluationStored(DomainEvent):
    session_id: str
    evaluation_set_id: str


@dataclass(frozen=True, kw_only=True)
class ConstructEvaluationCompleted(DomainEvent):
    session_id: str
    evaluations_count: int
    overall_confidence: float


@dataclass(frozen=True, kw_only=True)
class ConstructEvaluationFailed(DomainEvent):
    session_id: str
    reason: str
