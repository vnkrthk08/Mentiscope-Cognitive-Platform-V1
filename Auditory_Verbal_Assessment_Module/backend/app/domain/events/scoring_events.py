from dataclasses import dataclass, field
from app.domain.events.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class ScoringStarted(DomainEvent):
    session_id: str
    scenario_id: str


@dataclass(frozen=True, kw_only=True)
class ConstructScoresCalculated(DomainEvent):
    session_id: str
    construct_count: int


@dataclass(frozen=True, kw_only=True)
class NormalizationCompleted(DomainEvent):
    session_id: str
    scale_name: str


@dataclass(frozen=True, kw_only=True)
class CalibrationCompleted(DomainEvent):
    session_id: str
    calibration_version: str


@dataclass(frozen=True, kw_only=True)
class WeightingCompleted(DomainEvent):
    session_id: str
    overall_composite_score: float


@dataclass(frozen=True, kw_only=True)
class ReliabilityEstimated(DomainEvent):
    session_id: str
    reliability_coefficient: float


@dataclass(frozen=True, kw_only=True)
class DecisionGenerated(DomainEvent):
    session_id: str
    decision_band: str


@dataclass(frozen=True, kw_only=True)
class ScoringValidated(DomainEvent):
    session_id: str
    status: str


@dataclass(frozen=True, kw_only=True)
class ScoringCompleted(DomainEvent):
    session_id: str
    composite_score: float
    decision_band: str


@dataclass(frozen=True, kw_only=True)
class ScoringFailed(DomainEvent):
    session_id: str
    reason: str
