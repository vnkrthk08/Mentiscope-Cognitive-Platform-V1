"""
Module: Difficulty Optimizer (Assessment Assembly Engine v1.0).
Enforces monotonic progressive difficulty curve (EASY -> EASY_MEDIUM -> MEDIUM -> MEDIUM_HARD -> HARD).
"""

from typing import List, Tuple
from app.application.scenario_subsystem.scenario_metadata import ScenarioMetadata
from app.domain.entities.scenario import Scenario


class DifficultyOptimizer:
    """Sorts and optimizes scenario order to guarantee monotonic progressive difficulty."""

    DIFFICULTY_RANK = {
        "EASY": 1,
        "EASY_MEDIUM": 2,
        "MEDIUM": 3,
        "MEDIUM_HARD": 4,
        "HARD": 5,
    }

    def optimize_difficulty_order(
        self,
        scenarios: List[Scenario],
        metadata_list: List[ScenarioMetadata],
    ) -> Tuple[List[Scenario], List[ScenarioMetadata]]:

        paired = list(zip(scenarios, metadata_list))
        paired_sorted = sorted(
            paired,
            key=lambda x: self.DIFFICULTY_RANK.get(x[1].listening_difficulty, 3)
        )

        sorted_scenarios = [p[0] for p in paired_sorted]
        sorted_metadata = [p[1] for p in paired_sorted]

        return sorted_scenarios, sorted_metadata
