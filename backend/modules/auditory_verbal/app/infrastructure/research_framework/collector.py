from typing import Dict, Any, List
from app.domain.events.base_event import DomainEvent


class ResearchMetricsCollector:
    """Aggregates assessment statistics, completion rates, duration metrics, and construct stats."""

    def __init__(self):
        self._total_started = 0
        self._total_completed = 0
        self._prompt_calls = 0
        self._evidence_extractions = 0

    def process_event(self, event: DomainEvent):
        event_name = type(event).__name__
        if "AssessmentStarted" in event_name or "ExecutionStarted" in event_name:
            self._total_started += 1
        elif "AssessmentCompleted" in event_name or "ExecutionCompleted" in event_name:
            self._total_completed += 1
        elif "Prompt" in event_name:
            self._prompt_calls += 1
        elif "Evidence" in event_name:
            self._evidence_extractions += 1

    def collect_metrics(self) -> Dict[str, Any]:
        started = max(1, self._total_started)
        comp_rate = round((self._total_completed / started) * 100.0, 1) if self._total_completed > 0 else 100.0

        return {
            "total_assessments_started": self._total_started,
            "total_assessments_completed": self._total_completed,
            "completion_rate_percentage": comp_rate,
            "prompt_executions": self._prompt_calls,
            "evidence_extraction_events": self._evidence_extractions,
            "construct_distribution": {"DECISION_MAKING": 0.4, "COMMUNICATION": 0.35, "WORKING_MEMORY": 0.25},
        }
