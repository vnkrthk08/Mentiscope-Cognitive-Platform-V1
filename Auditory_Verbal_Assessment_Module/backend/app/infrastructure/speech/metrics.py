from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List


@dataclass
class SpeechMetric:
    provider_name: str
    latency_ms: float
    success: bool
    processing_time_ms: float
    cost_usd: float
    words_count: int
    words_per_second: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SpeechMetricsTracker:
    """In-memory and persistence-ready metric collection store for transcription analytics."""

    def __init__(self):
        self._metrics: List[SpeechMetric] = []

    def record(self, metric: SpeechMetric) -> None:
        self._metrics.append(metric)

    def get_provider_stats(self, provider_name: str) -> Dict[str, Any]:
        provider_name = provider_name.lower()
        records = [m for m in self._metrics if m.provider_name.lower() == provider_name]
        if not records:
            return {
                "availability": 1.0,
                "latency_avg_ms": 0.0,
                "total_cost": 0.0,
                "words_per_second_avg": 0.0,
            }

        successes = [m for m in records if m.success]
        availability = len(successes) / len(records)
        latency_avg = sum(m.latency_ms for m in records) / len(records)
        total_cost = sum(m.cost_usd for m in records)
        wps_avg = sum(m.words_per_second for m in successes) / len(successes) if successes else 0.0

        return {
            "availability": availability,
            "latency_avg_ms": latency_avg,
            "total_cost": total_cost,
            "words_per_second_avg": wps_avg,
        }


# Global metrics tracker
metrics_tracker = SpeechMetricsTracker()
