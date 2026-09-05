from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(frozen=True)
class ProviderResult:
    """Immutable Value Object tracking provider parameters and response statistics."""

    provider_name: str
    provider_version: str
    model_name: str
    request_id: str
    processing_time: float
    api_latency: float
    estimated_cost: float
    billing_units: int
    raw_metadata: Dict[str, Any] = field(default_factory=dict)
