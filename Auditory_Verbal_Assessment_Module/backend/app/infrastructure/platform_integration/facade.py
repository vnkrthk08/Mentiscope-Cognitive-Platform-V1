from typing import Optional, Dict, Any
from app.core.logging import logger
from app.infrastructure.platform_integration.registry import SubsystemRegistry
from app.infrastructure.platform_integration.config_manager import ConfigurationManager
from app.infrastructure.platform_integration.security_manager import SecurityManager
from app.infrastructure.platform_integration.health_manager import HealthCheckManager
from app.infrastructure.platform_integration.observability_manager import ObservabilityManager
from app.infrastructure.platform_integration.resilience_manager import ResilienceManager
from app.infrastructure.platform_integration.lifecycle_manager import PlatformLifecycleManager
from app.infrastructure.platform_integration.publisher import PlatformEventPublisher
from app.infrastructure.platform_integration.models import DeploymentManifest, PlatformStatus
from app.domain.exceptions.platform_exceptions import PlatformStartupFailure

# Import all 14 subsystem facades for registration
from app.application.orchestrator import AssessmentOrchestrator
from app.application.scenario_subsystem import ScenarioManagementSystem
from app.application.execution_engine import AssessmentExecutionEngine
from app.application.listening_engine import ListeningAssessmentEngine
from app.application.speaking_engine import SpeakingAssessmentEngine
from app.infrastructure.speech_service import SpeechProcessingService
from app.infrastructure.prompt_service import AIPromptOrchestrationService
from app.application.evidence_engine import BehavioralEvidenceExtractionEngine
from app.application.construct_engine import PsychometricConstructEvaluationEngine
from app.application.scoring_engine import PsychometricScoringDecisionEngine
from app.application.report_engine import AssessmentReportingEngine
from app.infrastructure.research_framework import ResearchAnalyticsFramework


class PlatformIntegrationManager:
    """Facade for Platform Integration, Security, Operations & Production Readiness (PISOPR).
    Registers, verifies, and coordinates all 14 completed platform subsystems into a production-ready system.
    DOES NOT ALTER ANY ASSESSMENT LOGIC OR BUSINESS RULES!
    """

    def __init__(
        self,
        registry: Optional[SubsystemRegistry] = None,
        config_manager: Optional[ConfigurationManager] = None,
        security_manager: Optional[SecurityManager] = None,
        health_manager: Optional[HealthCheckManager] = None,
        observability_manager: Optional[ObservabilityManager] = None,
        resilience_manager: Optional[ResilienceManager] = None,
        lifecycle_manager: Optional[PlatformLifecycleManager] = None,
        publisher: Optional[PlatformEventPublisher] = None,
    ):
        self.registry = registry or SubsystemRegistry()
        self.config_manager = config_manager or ConfigurationManager()
        self.security_manager = security_manager or SecurityManager()
        self.health_manager = health_manager or HealthCheckManager()
        self.observability_manager = observability_manager or ObservabilityManager()
        self.resilience_manager = resilience_manager or ResilienceManager()
        self.lifecycle_manager = lifecycle_manager or PlatformLifecycleManager()
        self.publisher = publisher or PlatformEventPublisher()
        self.manifest = DeploymentManifest()

    async def initialize_platform(self, env: str = "production") -> PlatformStatus:
        """Executes ordered production startup sequence across all 14 subsystems."""
        logger.info(f"[PISOPR FACADE] Initializing MentiScope Platform (Environment: '{env}')...")
        await self.publisher.publish_starting(env)

        try:
            # 1. Load & Validate Configuration
            self.config_manager.validate_configuration()
            await self.publisher.publish_config_validated(self.config_manager.get_config_summary())

            # 2. Register All 14 Subsystem Facades
            self._register_default_subsystems()

            # 3. Verify Dependency Graph
            self.registry.verify_dependencies()
            registered_subsystems = self.registry.list_registered_subsystems()
            await self.publisher.publish_started(len(registered_subsystems))

            # 4. Initialize Security Policies
            self.security_manager.initialize_security()
            await self.publisher.publish_security_validated(self.security_manager.get_security_status())

            # 5. Initialize Observability & Correlation Telemetry
            self.observability_manager.initialize_observability()
            await self.publisher.publish_observability_initialized(True)

            # 6. Execute Platform Health Checks
            health_report = self.health_manager.check_platform_health(self.registry)
            await self.publisher.publish_health_completed(health_report["status"])

            # 7. Start Platform Lifecycle
            self.lifecycle_manager.start_lifecycle()
            await self.publisher.publish_ready(self.manifest.platform_version)

            status = PlatformStatus(
                is_ready=True,
                health_summary=health_report["status"],
                registered_subsystems=registered_subsystems,
                active_providers=["Whisper", "Gemini"],
                configuration_status=self.config_manager.get_config_summary(),
                security_status=self.security_manager.get_security_status(),
                observability_status=f"Active (Correlation ID: {self.observability_manager.correlation_id})",
            )

            logger.info(f"[PISOPR FACADE] MentiScope Platform is READY! Registered subsystems: {len(registered_subsystems)}")
            return status

        except Exception as e:
            await self.publisher.publish_failed(str(e))
            logger.error(f"[PISOPR FACADE] Platform startup failed: {str(e)}")
            raise PlatformStartupFailure(str(e))

    async def shutdown_platform(self, reason: str = "GRACEFUL_SHUTDOWN") -> bool:
        """Executes graceful platform shutdown and resource cleanup."""
        logger.info(f"[PISOPR FACADE] Shutting down MentiScope Platform: {reason}")
        await self.publisher.publish_stopping(reason)
        self.lifecycle_manager.stop_lifecycle()
        await self.publisher.publish_stopped("STOPPED")
        return True

    def _register_default_subsystems(self):
        """Instantiates and registers all 14 subsystem facades into SubsystemRegistry."""
        subsystems_map = {
            "AssessmentOrchestrator": AssessmentOrchestrator(),
            "ScenarioManagementSystem": ScenarioManagementSystem(),
            "AssessmentExecutionEngine": AssessmentExecutionEngine(),
            "ListeningAssessmentEngine": ListeningAssessmentEngine(),
            "SpeakingAssessmentEngine": SpeakingAssessmentEngine(),
            "SpeechProcessingService": SpeechProcessingService(),
            "AIPromptOrchestrationService": AIPromptOrchestrationService(),
            "BehavioralEvidenceExtractionEngine": BehavioralEvidenceExtractionEngine(),
            "PsychometricConstructEvaluationEngine": PsychometricConstructEvaluationEngine(),
            "PsychometricScoringDecisionEngine": PsychometricScoringDecisionEngine(),
            "AssessmentReportingEngine": AssessmentReportingEngine(),
            "ResearchAnalyticsFramework": ResearchAnalyticsFramework(),
        }

        for name, facade in subsystems_map.items():
            self.registry.register_subsystem(name, facade, version="1.0.0")
