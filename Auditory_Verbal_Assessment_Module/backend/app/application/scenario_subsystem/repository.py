import os
from typing import Dict, List, Optional
from app.core.config import settings
from app.domain.entities.scenario import Scenario
from app.domain.exceptions.scenario_exceptions import ScenarioNotFound
from app.application.scenario_subsystem.loader import ScenarioLoader
from app.application.scenario_subsystem.validator import ScenarioValidator
from app.application.scenario_subsystem.factory import ScenarioFactory
from app.application.scenario_subsystem.cache import ScenarioCache


class ScenarioRepository:
    """Repository managing scenario configuration loading, parsing, validation, and domain object creation."""

    def __init__(
        self,
        config_dir: Optional[str] = None,
        cache: Optional[ScenarioCache] = None,
    ):
        self.config_dir = config_dir or self._resolve_default_config_dir()
        self.loader = ScenarioLoader()
        self.validator = ScenarioValidator()
        self.factory = ScenarioFactory()
        self.cache = cache or ScenarioCache()

    def _resolve_default_config_dir(self) -> str:
        candidates = [
            os.path.join(settings.CONFIG_REPO_PATH, "scenarios"),
            os.path.join("config_repo", "scenarios"),
            os.path.join("backend", "config_repo", "scenarios"),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "config_repo", "scenarios")),
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return candidates[0]

    def get_by_id(self, scenario_id: str) -> Scenario:
        # Check Cache
        cached = self.cache.get(scenario_id)
        if cached:
            return cached

        # Look for matching YAML/JSON file in config_dir
        file_path = self._find_scenario_file(scenario_id)
        if not file_path:
            raise ScenarioNotFound(scenario_id)

        raw_data = self.loader.load_from_file(file_path)
        self.validator.validate(raw_data)
        scenario = self.factory.create_from_dict(raw_data)

        # Cache & Return
        self.cache.put(scenario)
        return scenario

    def save_scenario(self, scenario: Scenario):
        """Caches scenario entity."""
        self.cache.put(scenario)

    def _find_scenario_file(self, scenario_id: str) -> Optional[str]:
        if not os.path.exists(self.config_dir):
            return None

        for filename in os.listdir(self.config_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml") or filename.endswith(".json"):
                full_path = os.path.join(self.config_dir, filename)
                try:
                    raw_data = self.loader.load_from_file(full_path)
                    if raw_data.get("id") == scenario_id:
                        return full_path
                except Exception:
                    continue
        return None
