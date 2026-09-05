"""Platform Analytics Domain Model."""
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class PlatformAnalytics:
    speech_provider_usage: Dict[str, int] = field(default_factory=dict)
    prompt_provider_usage: Dict[str, int] = field(default_factory=dict)
    avg_speech_latency_ms: float = 0.0
    avg_prompt_latency_ms: float = 0.0
    avg_pipeline_latency_ms: float = 0.0
    pipeline_completion_rate: float = 0.0
    overall_failure_rate: float = 0.0
    error_count_by_type: Dict[str, int] = field(default_factory=dict)
