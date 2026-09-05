from typing import List, Dict, Any
from app.infrastructure.research_framework.models import ExperimentResult


class ExperimentManager:
    """Manages prompt templates, LLM model variations, and calibration experiment trials."""

    def __init__(self):
        self._experiments: List[ExperimentResult] = []
        self._register_default_experiments()

    def _register_default_experiments(self):
        exp1 = ExperimentResult(
            experiment_type="PROMPT_A_B_TEST",
            configuration={"template_a": "EVIDENCE_EXTRACTION_PROMPT_v1", "template_b": "EVIDENCE_EXTRACTION_PROMPT_v2"},
            outcome="VARIANT_B_HIGHER_RECALL",
            metrics={"recall_improvement": 0.08, "latency_diff_ms": -15.0},
            winner="VARIANT_B",
        )
        self._experiments.append(exp1)

    def run_experiment_evaluation(self) -> List[ExperimentResult]:
        return list(self._experiments)

    def get_experiments(self) -> List[ExperimentResult]:
        return list(self._experiments)
