from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class PromptExecutionStarted:
    execution_id: str
    transcript_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class PromptExecutionCompleted:
    execution_id: str
    transcript_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class PromptExecutionFailed:
    execution_id: str
    transcript_id: str
    error_message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class PromptResponsePersisted:
    response_id: str
    execution_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class PromptCompleted:
    execution_id: str
    transcript_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
