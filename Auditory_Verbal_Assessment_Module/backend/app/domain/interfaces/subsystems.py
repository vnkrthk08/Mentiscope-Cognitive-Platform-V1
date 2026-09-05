from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.scenario import Scenario
from app.domain.entities.evidence import Evidence
from app.domain.entities.assessment_report import AssessmentReport


class IScenarioEngine(ABC):
    """Abstract interface for Scenario Management Subsystem."""

    @abstractmethod
    async def load_scenario(self, scenario_id: str) -> Scenario:
        pass


class IListeningEngine(ABC):
    """Abstract interface for Listening Assessment Engine."""

    @abstractmethod
    async def execute_listening_stage(self, session: AssessmentSession) -> Dict[str, Any]:
        pass


class ISpeakingEngine(ABC):
    """Abstract interface for Speaking Assessment Engine."""

    @abstractmethod
    async def execute_speaking_stage(self, session: AssessmentSession) -> Dict[str, Any]:
        pass


class IAdaptiveEngine(ABC):
    """Abstract interface for Adaptive Follow-up Engine."""

    @abstractmethod
    async def evaluate_followup_need(self, session: AssessmentSession) -> Dict[str, Any]:
        pass


class IEvidenceEngine(ABC):
    """Abstract interface for AI Evidence Extraction Engine."""

    @abstractmethod
    async def process_evidence_extraction(self, session: AssessmentSession) -> List[Evidence]:
        pass


class IScoringEngine(ABC):
    """Abstract interface for Deterministic Scoring Engine."""

    @abstractmethod
    async def calculate_construct_scores(self, session: AssessmentSession) -> Dict[str, float]:
        pass


class IMetricsEngine(ABC):
    """Abstract interface for Report Metrics Engine."""

    @abstractmethod
    async def generate_report(self, session: AssessmentSession) -> AssessmentReport:
        pass


class IPlatformAdapter(ABC):
    """Abstract interface for MentiScope Central Platform REST Client Adapter."""

    @abstractmethod
    async def sync_metrics_to_platform(self, report: AssessmentReport) -> bool:
        pass
