from dataclasses import dataclass, field
from app.domain.events.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class PlatformStarting(DomainEvent):
    environment: str


@dataclass(frozen=True, kw_only=True)
class PlatformStarted(DomainEvent):
    registered_subsystems_count: int


@dataclass(frozen=True, kw_only=True)
class PlatformStopping(DomainEvent):
    reason: str


@dataclass(frozen=True, kw_only=True)
class PlatformStopped(DomainEvent):
    status: str


@dataclass(frozen=True, kw_only=True)
class HealthCheckCompleted(DomainEvent):
    overall_health: str


@dataclass(frozen=True, kw_only=True)
class SubsystemRegistered(DomainEvent):
    subsystem_name: str
    version: str


@dataclass(frozen=True, kw_only=True)
class ConfigurationValidated(DomainEvent):
    config_summary: str


@dataclass(frozen=True, kw_only=True)
class SecurityValidated(DomainEvent):
    security_status: str


@dataclass(frozen=True, kw_only=True)
class ObservabilityInitialized(DomainEvent):
    correlation_id_active: bool


@dataclass(frozen=True, kw_only=True)
class PlatformReady(DomainEvent):
    platform_version: str


@dataclass(frozen=True, kw_only=True)
class PlatformFailed(DomainEvent):
    reason: str
