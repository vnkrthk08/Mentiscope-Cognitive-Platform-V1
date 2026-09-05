from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class ConstructEvaluationStarted:
    behavior_evidence_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ConstructEvaluationCompleted:
    evaluation_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ConstructEvaluationFailed:
    behavior_evidence_id: str
    error_message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ConstructEvaluationPersisted:
    evaluation_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ConstructEvaluationReadyForScoring:
    evaluation_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
pre=1.0
