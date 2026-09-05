from abc import ABC, abstractmethod
from typing import Any, Dict
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.scenario import Scenario


class IListeningExecutor(ABC):
    """Abstract interface for Listening Stage Executor."""

    @abstractmethod
    async def execute(self, session: AssessmentSession, scenario: Scenario) -> Dict[str, Any]:
        pass


class ISpeakingExecutor(ABC):
    """Abstract interface for Speaking Stage Executor."""

    @abstractmethod
    async def execute(self, session: AssessmentSession, scenario: Scenario) -> Dict[str, Any]:
        pass


class IAdaptiveExecutor(ABC):
    """Abstract interface for Adaptive Stage Executor."""

    @abstractmethod
    async def execute(self, session: AssessmentSession, scenario: Scenario) -> Dict[str, Any]:
        pass
