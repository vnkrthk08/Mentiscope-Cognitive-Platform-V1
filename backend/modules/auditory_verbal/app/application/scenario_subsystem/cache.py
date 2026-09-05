import threading
from typing import Dict, Optional
from app.domain.entities.scenario import Scenario
from app.core.logging import logger


class ScenarioCache:
    """Thread-safe scenario memory cache supporting load once, read many, and version invalidation."""

    def __init__(self):
        self._cache: Dict[str, Scenario] = {}
        self._lock = threading.Lock()

    def get(self, scenario_id: str) -> Optional[Scenario]:
        with self._lock:
            return self._cache.get(scenario_id)

    def put(self, scenario: Scenario):
        with self._lock:
            self._cache[scenario.scenario_id] = scenario
            logger.info(f"[SMS CACHE] Cached scenario '{scenario.scenario_id}' (v{scenario.version})")

    def invalidate(self, scenario_id: str):
        with self._lock:
            if scenario_id in self._cache:
                del self._cache[scenario_id]
                logger.info(f"[SMS CACHE] Invalidated scenario '{scenario_id}' from cache")

    def clear(self):
        with self._lock:
            self._cache.clear()
            logger.info("[SMS CACHE] Cleared all scenario cache entries")
