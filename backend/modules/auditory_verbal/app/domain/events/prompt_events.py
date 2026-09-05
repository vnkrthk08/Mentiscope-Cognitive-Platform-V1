from dataclasses import dataclass, field
from app.domain.events.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class PromptLoaded(DomainEvent):
    prompt_id: str
    version: str


@dataclass(frozen=True, kw_only=True)
class PromptRendered(DomainEvent):
    prompt_id: str
    rendered_hash: str
    char_count: int


@dataclass(frozen=True, kw_only=True)
class PromptValidated(DomainEvent):
    prompt_id: str
    status: str


@dataclass(frozen=True, kw_only=True)
class ModelSelected(DomainEvent):
    prompt_id: str
    provider_name: str
    model_name: str


@dataclass(frozen=True, kw_only=True)
class GenerationStarted(DomainEvent):
    prompt_id: str
    model_name: str


@dataclass(frozen=True, kw_only=True)
class GenerationCompleted(DomainEvent):
    prompt_id: str
    model_name: str
    latency_ms: int


@dataclass(frozen=True, kw_only=True)
class ValidationSucceeded(DomainEvent):
    prompt_id: str
    schema_version: str


@dataclass(frozen=True, kw_only=True)
class ValidationFailed(DomainEvent):
    prompt_id: str
    reason: str


@dataclass(frozen=True, kw_only=True)
class PromptCompleted(DomainEvent):
    prompt_id: str
    latency_ms: int


@dataclass(frozen=True, kw_only=True)
class PromptFailed(DomainEvent):
    prompt_id: str
    reason: str
