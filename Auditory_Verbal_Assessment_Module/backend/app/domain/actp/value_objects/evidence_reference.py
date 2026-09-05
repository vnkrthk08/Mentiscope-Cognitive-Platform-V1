"""EvidenceReference Value Object."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class EvidenceReference:
    """Reference link connecting extracted behavioral evidence to construct evaluations."""

    evidence_id: str
    construct_name: str
    verbatim_quote: str
    behavioral_indicator: str
    confidence: float = 0.0
    evidence_type: str = "VERBATIM"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "construct_name": self.construct_name,
            "verbatim_quote": self.verbatim_quote,
            "behavioral_indicator": self.behavioral_indicator,
            "confidence": self.confidence,
            "evidence_type": self.evidence_type,
        }
