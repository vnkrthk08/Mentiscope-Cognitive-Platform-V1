from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import uuid


@dataclass(frozen=True)
class DeploymentManifest:
    """Immutable manifest declaring platform build, environment, and subsystem versioning."""

    manifest_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform_version: str = "1.0.0"
    environment: str = "production"
    subsystem_versions: Dict[str, str] = field(default_factory=lambda: {
        "ScenarioManagementSystem": "1.0.0",
        "AssessmentExecutionEngine": "1.0.0",
        "ListeningAssessmentEngine": "1.0.0",
        "SpeakingAssessmentEngine": "1.0.0",
        "SpeechProcessingService": "1.0.0",
        "AIPromptOrchestrationService": "1.0.0",
        "BehavioralEvidenceExtractionEngine": "1.0.0",
        "PsychometricConstructEvaluationEngine": "1.0.0",
        "PsychometricScoringDecisionEngine": "1.0.0",
        "AssessmentReportingEngine": "1.0.0",
        "ResearchAnalyticsFramework": "1.0.0",
    })
    config_summary: str = "Standard Production Configuration (All Subsystems Active)"
    build_metadata: Dict[str, Any] = field(default_factory=lambda: {
        "build_hash": "GIT-PROD-2026-07-21-PHASE15",
        "python_version": "3.14",
    })


@dataclass(frozen=True)
class PlatformStatus:
    """Operational status representation for the complete MentiScope platform."""

    is_ready: bool = True
    health_summary: str = "HEALTHY"
    registered_subsystems: List[str] = field(default_factory=list)
    active_providers: List[str] = field(default_factory=lambda: ["Whisper", "Gemini"])
    configuration_status: str = "VALIDATED"
    security_status: str = "SECURITY_POLICIES_ENFORCED"
    observability_status: str = "TELEMETRY_CORRELATION_ACTIVE"
    startup_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
