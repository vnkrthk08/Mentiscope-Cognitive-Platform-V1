"""PipelineInvocation Value Object."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class PipelineInvocation:
    """Invocation provenance details for STT, LLM, or scoring providers."""

    subsystem: str  # SPEECH, PROMPT, BEHAVIOR, CONSTRUCT, SCORING, RESEARCH
    provider: str
    model_name: str
    version: str
    latency_ms: float = 0.0
    token_usage: Dict[str, int] = field(default_factory=dict)
    checksum: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subsystem": self.subsystem,
            "provider": self.provider,
            "model_name": self.model_name,
            "version": self.version,
            "latency_ms": self.latency_ms,
            "token_usage": dict(self.token_usage) if self.token_usage else {},
            "checksum": self.checksum,
        }
