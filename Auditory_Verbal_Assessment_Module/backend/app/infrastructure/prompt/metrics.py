from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List


@dataclass
class PromptMetric:
    provider_name: str
    model_name: str
    latency_ms: float
    success: bool
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class PromptMetricsTracker:
    def __init__(self):
        self._metrics: List[PromptMetric] = []

    def record(self, metric: PromptMetric) -> None:
        self._metrics.append(metric)


# Global metrics tracker
prompt_metrics = PromptMetricsTracker()
