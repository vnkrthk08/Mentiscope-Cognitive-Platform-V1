from typing import Any, Dict, Optional
from app.domain.entities.scenario import Scenario
from app.domain.interfaces.subsystems import IScenarioEngine
from app.application.scenario_subsystem.repository import ScenarioRepository
from app.application.scenario_subsystem.resource_manager import ScenarioResourceManager
from app.application.scenario_subsystem.construct_mapper import ScenarioConstructMapper
from app.application.scenario_subsystem.analytics import ScenarioAnalytics
from app.application.scenario_subsystem.version_manager import ScenarioVersionManager


class ScenarioManagementSystem(IScenarioEngine):
    """Facade for the Scenario Management System (SMS) implementing IScenarioEngine interface.
    Exposes authoritative scenario entities, resource resolution, construct mapping, version management, and analytics to external consumers.
    """

    def __init__(
        self,
        repository: Optional[ScenarioRepository] = None,
        resource_manager: Optional[ScenarioResourceManager] = None,
        construct_mapper: Optional[ScenarioConstructMapper] = None,
        analytics: Optional[ScenarioAnalytics] = None,
        version_manager: Optional[ScenarioVersionManager] = None,
    ):
        self.repository = repository or ScenarioRepository()
        self.resource_manager = resource_manager or ScenarioResourceManager()
        self.construct_mapper = construct_mapper or ScenarioConstructMapper()
        self.analytics = analytics or ScenarioAnalytics()
        self.version_manager = version_manager or ScenarioVersionManager()

    async def load_scenario(self, scenario_id: str) -> Scenario:
        """Loads, validates, hydrates, and returns an authoritative Scenario aggregate root."""
        scenario = self.repository.get_by_id(scenario_id)
        self.resource_manager.validate_scenario_resources(scenario)
        self.construct_mapper.validate_construct_coverage(scenario)
        return scenario

    def get_analytics(self, scenario: Scenario) -> Dict[str, Any]:
        """Returns structural content analytics metadata for a scenario."""
        return self.analytics.analyze_scenario(scenario)
