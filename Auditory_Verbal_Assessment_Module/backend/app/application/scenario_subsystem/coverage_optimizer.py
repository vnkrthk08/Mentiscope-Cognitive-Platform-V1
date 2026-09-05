"""
Module: Coverage Optimizer (Assessment Assembly Engine v1.0).
Computes construct coverage matrix and ensures optimal alignment with blueprint targets.
"""

from typing import List, Dict, Any
from app.application.scenario_subsystem.scenario_metadata import ScenarioMetadata


class CoverageOptimizer:
    """Computes construct coverage matrix across 5 assembled scenarios."""

    def compute_coverage_matrix(self, metadata_list: List[ScenarioMetadata]) -> Dict[str, int]:
        coverage: Dict[str, int] = {}

        for m in metadata_list:
            for c in m.primary_constructs:
                coverage[c] = coverage.get(c, 0) + 1
            for c in m.secondary_constructs:
                coverage[c] = coverage.get(c, 0) + 1

        return coverage

    def compute_distribution(self, items: List[str]) -> Dict[str, int]:
        dist: Dict[str, int] = {}
        for item in items:
            dist[item] = dist.get(item, 0) + 1
        return dist
