from dataclasses import dataclass, field
from app.domain.events.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class ReportGenerationStarted(DomainEvent):
    session_id: str
    scenario_id: str


@dataclass(frozen=True, kw_only=True)
class ExecutiveSummaryGenerated(DomainEvent):
    session_id: str
    decision_band: str


@dataclass(frozen=True, kw_only=True)
class ConstructSectionsGenerated(DomainEvent):
    session_id: str
    sections_count: int


@dataclass(frozen=True, kw_only=True)
class TraceabilityBuilt(DomainEvent):
    session_id: str
    trace_links_count: int


@dataclass(frozen=True, kw_only=True)
class ReliabilitySectionGenerated(DomainEvent):
    session_id: str
    reliability_coefficient: float


@dataclass(frozen=True, kw_only=True)
class ReportValidated(DomainEvent):
    session_id: str
    status: str


@dataclass(frozen=True, kw_only=True)
class ReportCompleted(DomainEvent):
    session_id: str
    report_id: str
    decision_band: str


@dataclass(frozen=True, kw_only=True)
class ReportGenerationFailed(DomainEvent):
    session_id: str
    reason: str
