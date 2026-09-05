"""ComparisonReport Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class ComparisonReport:
    """Detailed diff & impact report comparing Baseline vs Candidate experiment runs."""

    experiment_id: str
    baseline_run_id: str
    candidate_run_id: str
    prompt_diff_summary: Dict[str, Any] = field(default_factory=dict)
    evidence_diff_summary: Dict[str, Any] = field(default_factory=dict)
    evaluation_diff_summary: Dict[str, Any] = field(default_factory=dict)
    score_deltas: Dict[str, float] = field(default_factory=dict)
    latency_delta_ms: float = 0.0
    cost_delta_usd: float = 0.0
    overall_recommendation: str = "NO_IMPACT"
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "experiment_id": self.experiment_id,
            "baseline_run_id": self.baseline_run_id,
            "candidate_run_id": self.candidate_run_id,
            "prompt_diff_summary": self.prompt_diff_summary,
            "evidence_diff_summary": self.evidence_diff_summary,
            "evaluation_diff_summary": self.evaluation_diff_summary,
            "score_deltas": self.score_deltas,
            "latency_delta_ms": self.latency_delta_ms,
            "cost_delta_usd": self.cost_delta_usd,
            "overall_recommendation": self.overall_recommendation,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }
