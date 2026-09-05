import pytest
from app.infrastructure.platform_integration import (
    PlatformIntegrationManager,
    SubsystemRegistry,
    ConfigurationManager,
    SecurityManager,
    HealthCheckManager,
    ObservabilityManager,
    ResilienceManager,
    PlatformLifecycleManager,
    DeploymentManifest,
)
from app.domain.exceptions.platform_exceptions import (
    SubsystemRegistrationFailure,
    ConfigurationFailure,
    PlatformStartupFailure,
)


def test_subsystem_registry_and_verification():
    registry = SubsystemRegistry()

    # Missing dependency error
    with pytest.raises(SubsystemRegistrationFailure):
        registry.verify_dependencies()

    registry.register_subsystem("AssessmentOrchestrator", object())
    registry.register_subsystem("ScenarioManagementSystem", object())
    registry.register_subsystem("AssessmentExecutionEngine", object())
    registry.register_subsystem("ListeningAssessmentEngine", object())
    registry.register_subsystem("SpeakingAssessmentEngine", object())
    registry.register_subsystem("SpeechProcessingService", object())
    registry.register_subsystem("AIPromptOrchestrationService", object())
    registry.register_subsystem("BehavioralEvidenceExtractionEngine", object())
    registry.register_subsystem("PsychometricConstructEvaluationEngine", object())
    registry.register_subsystem("PsychometricScoringDecisionEngine", object())
    registry.register_subsystem("AssessmentReportingEngine", object())
    registry.register_subsystem("ResearchAnalyticsFramework", object())

    assert registry.verify_dependencies() is True
    assert len(registry.list_registered_subsystems()) == 12


def test_config_and_security_managers():
    cfg_mgr = ConfigurationManager(env="production")
    sec_mgr = SecurityManager()

    assert cfg_mgr.validate_configuration() is True
    assert cfg_mgr.get_feature_flag("ENABLE_ADAPTIVE_FOLLOWUP") is True

    assert sec_mgr.initialize_security() is True
    assert sec_mgr.verify_authorization("CAND-01", "READ") is True


def test_observability_and_resilience():
    obs_mgr = ObservabilityManager()
    res_mgr = ResilienceManager()

    assert obs_mgr.initialize_observability() is True
    assert "correlation_id" in obs_mgr.get_audit_context()

    status = res_mgr.get_resilience_status()
    assert status["max_retries"] == 3


def test_platform_lifecycle_manager():
    lifecycle = PlatformLifecycleManager()

    assert lifecycle.is_active is False
    assert lifecycle.start_lifecycle() is True
    assert lifecycle.is_active is True
    assert lifecycle.stop_lifecycle() is True
    assert lifecycle.is_active is False


@pytest.mark.asyncio
async def test_pisopr_facade_end_to_end_platform_startup():
    platform = PlatformIntegrationManager()

    status = await platform.initialize_platform(env="production")

    assert status.is_ready is True
    assert status.health_summary == "HEALTHY"
    assert len(status.registered_subsystems) == 12
    assert "Whisper" in status.active_providers

    shutdown_ok = await platform.shutdown_platform(reason="TEST_SHUTDOWN")
    assert shutdown_ok is True
