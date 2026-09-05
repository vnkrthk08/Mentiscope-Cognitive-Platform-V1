"""
Module 2: Construct Analysis Engine.
Evaluates evidence coverage, calculates confidence scores per construct, and identifies deficits.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from app.application.followup_subsystem.evidence_extractor import EvidenceItem


@dataclass
class ConstructCoverageMatrix:
    confidence_scores: Dict[str, float]
    saturated_constructs: List[str]
    missing_constructs: List[str]
    primary_deficit_construct: str
    total_evidence_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "confidence_scores": self.confidence_scores,
            "saturated_constructs": self.saturated_constructs,
            "missing_constructs": self.missing_constructs,
            "primary_deficit_construct": self.primary_deficit_construct,
            "total_evidence_count": self.total_evidence_count,
        }


class ConstructAnalysisEngine:
    """Evaluates accumulated evidence against target constructs to produce coverage matrix."""

    def evaluate_coverage(
        self, evidence: List[EvidenceItem], target_constructs: List[str]
    ) -> ConstructCoverageMatrix:

        scores: Dict[str, float] = {}
        for c in target_constructs:
            scores[c] = 0.0

        for item in evidence:
            c = item.construct
            if c in scores:
                scores[c] = round(min(scores[c] + item.confidence * 0.5, 1.0), 2)

        saturated: List[str] = [c for c, s in scores.items() if s >= 0.75]
        missing: List[str] = [c for c, s in scores.items() if s < 0.40]

        # Determine primary deficit construct (lowest score among targets)
        sorted_deficits = sorted(scores.items(), key=lambda x: x[1])
        primary_deficit = sorted_deficits[0][0] if sorted_deficits else (target_constructs[0] if target_constructs else "COMMUNICATION")

        return ConstructCoverageMatrix(
            confidence_scores=scores,
            saturated_constructs=saturated,
            missing_constructs=missing,
            primary_deficit_construct=primary_deficit,
            total_evidence_count=len(evidence),
        )
