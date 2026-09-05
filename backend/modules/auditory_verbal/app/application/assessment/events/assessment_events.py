from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class AssessmentScoringStarted:
    construct_evaluation_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class AssessmentScoringCompleted:
    result_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class AssessmentScoringFailed:
    construct_evaluation_id: str
    error_message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class AssessmentReportPersisted:
    report_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class AssessmentCompleted:
    report_id: str
    candidate_id: str
    assessment_id: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
pre=1.0
