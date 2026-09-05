from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class BehaviorExtractionStarted:
    execution_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class BehaviorExtractionCompleted:
    evidence_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class BehaviorExtractionFailed:
    execution_id: str
    error_message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class BehaviorEvidencePersisted:
    evidence_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class BehaviorEvidenceReadyForEvaluation:
    evidence_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
