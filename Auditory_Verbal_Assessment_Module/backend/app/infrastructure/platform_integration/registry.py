from typing import Dict, Any, List, Optional
from app.domain.exceptions.platform_exceptions import SubsystemRegistrationFailure


class SubsystemRegistry:
    """Central registry maintaining references, version compatibility, and health status for all 14 platform subsystems."""

    def __init__(self):
        self._subsystems: Dict[str, Any] = {}
        self._versions: Dict[str, str] = {}

    def register_subsystem(self, name: str, facade_instance: Any, version: str = "1.0.0"):
        if not name or not name.strip():
            raise SubsystemRegistrationFailure("UNKNOWN", "Subsystem name cannot be empty.")
        if facade_instance is None:
            raise SubsystemRegistrationFailure(name, "Subsystem facade instance cannot be None.")

        self._subsystems[name] = facade_instance
        self._versions[name] = version

    def get_subsystem(self, name: str) -> Optional[Any]:
        return self._subsystems.get(name)

    def verify_dependencies(self) -> bool:
        """Verifies all mandatory core platform subsystems are registered and valid."""
        required = [
            "AssessmentOrchestrator",
            "ScenarioManagementSystem",
            "AssessmentExecutionEngine",
            "ListeningAssessmentEngine",
            "SpeakingAssessmentEngine",
            "SpeechProcessingService",
            "AIPromptOrchestrationService",
            "BehavioralEvidenceExtractionEngine",
            "PsychometricConstructEvaluationEngine",
            "PsychometricScoringDecisionEngine",
            "AssessmentReportingEngine",
            "ResearchAnalyticsFramework",
        ]

        for req in required:
            if req not in self._subsystems:
                raise SubsystemRegistrationFailure(req, f"Required subsystem '{req}' is missing from platform registry.")
        return True

    def list_registered_subsystems(self) -> List[str]:
        return list(self._subsystems.keys())
