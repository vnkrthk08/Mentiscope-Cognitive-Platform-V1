from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(frozen=True)
class ProviderResult:
    """Immutable Value Object tracking provider response statistics and details."""

    provider_name: str
    provider_version: str
    model_name: str
    request_id: str
    processing_time_ms: float
    api_latency_ms: float
    estimated_cost_usd: float
    raw_metadata: Dict[str, Any] = field(default_factory=dict)
