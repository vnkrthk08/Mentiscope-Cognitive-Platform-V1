from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import uuid


@dataclass(frozen=True)
class ValidationSummary:
    reliability_status: str = "STABLE (0.92)"
    calibration_status: str = "CALIBRATED (v1.0.0)"
    drift_status: str = "NO_DRIFT_DETECTED"
    norm_status: str = "VALIDATED"
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MonitoringSummary:
    health_status: str = "HEALTHY"
    subsystem_status: Dict[str, str] = field(default_factory=lambda: {
        "ScenarioEngine": "ONLINE",
        "ExecutionEngine": "ONLINE",
        "ListeningEngine": "ONLINE",
        "SpeakingEngine": "ONLINE",
        "SpeechService": "ONLINE",
        "APOS": "ONLINE",
        "EvidenceEngine": "ONLINE",
        "ConstructEngine": "ONLINE",
        "ScoringEngine": "ONLINE",
        "ReportingEngine": "ONLINE",
    })
    provider_status: Dict[str, str] = field(default_factory=lambda: {
        "Whisper": "ACTIVE",
        "Gemini": "ACTIVE",
    })
    latency: Dict[str, float] = field(default_factory=lambda: {"avg_latency_ms": 120.0})
    failures: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ExperimentResult:
    experiment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    experiment_type: str = "PROMPT_A_B_TEST"
    configuration: Dict[str, Any] = field(default_factory=dict)
    outcome: str = "VARIANT_B_SUPERIOR"
    metrics: Dict[str, float] = field(default_factory=lambda: {"accuracy": 0.96, "latency_ms": 110.0})
    winner: str = "VARIANT_B"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResearchDashboardModel:
    """Comprehensive snapshot model representing platform quality, research, analytics, and operational health."""

    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    research_metrics: Dict[str, Any] = field(default_factory=dict)
    analytics_metrics: Dict[str, Any] = field(default_factory=dict)
    validation_metrics: Optional[ValidationSummary] = None
    monitoring_metrics: Optional[MonitoringSummary] = None
    experiment_results: List[ExperimentResult] = field(default_factory=list)
    platform_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
