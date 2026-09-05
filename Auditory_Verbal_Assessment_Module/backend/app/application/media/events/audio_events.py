from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class UploadStarted:
    asset_id: str
    session_id: str
    assessment_id: str
    candidate_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class UploadCompleted:
    asset_id: str
    session_id: str
    checksum: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ValidationSucceeded:
    asset_id: str
    session_id: str
    duration_seconds: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ValidationFailed:
    asset_id: str
    session_id: str
    reason: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class AudioQueued:
    asset_id: str
    session_id: str
    storage_path: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class AudioDeleted:
    asset_id: str
    session_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
