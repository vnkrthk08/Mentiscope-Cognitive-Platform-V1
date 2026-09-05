from dataclasses import dataclass, field
from app.domain.events.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class AnalyticsUpdated(DomainEvent):
    total_assessments: int
    completion_rate_percentage: float


@dataclass(frozen=True, kw_only=True)
class ValidationCompleted(DomainEvent):
    reliability_status: str
    drift_status: str


@dataclass(frozen=True, kw_only=True)
class MonitoringUpdated(DomainEvent):
    overall_health: str
    avg_latency_ms: float


@dataclass(frozen=True, kw_only=True)
class ExperimentCompleted(DomainEvent):
    experiment_id: str
    winner_variant: str


@dataclass(frozen=True, kw_only=True)
class PlatformHealthUpdated(DomainEvent):
    active_providers: int
    system_status: str


@dataclass(frozen=True, kw_only=True)
class ResearchSnapshotCreated(DomainEvent):
    snapshot_id: str
    metrics_count: int


@dataclass(frozen=True, kw_only=True)
class FrameworkCompleted(DomainEvent):
    snapshot_id: str


@dataclass(frozen=True, kw_only=True)
class FrameworkFailed(DomainEvent):
    reason: str
