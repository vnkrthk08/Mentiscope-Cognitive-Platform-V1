from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class SpeechProcessingStarted:
    job_id: str
    asset_id: str
    provider_name: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class SpeechProcessingCompleted:
    job_id: str
    asset_id: str
    transcript_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class SpeechProcessingFailed:
    job_id: str
    asset_id: str
    error_message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class TranscriptCreated:
    transcript_id: str
    asset_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class TranscriptPersisted:
    transcript_id: str
    asset_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class TranscriptReadyForAnalysis:
    transcript_id: str
    session_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
