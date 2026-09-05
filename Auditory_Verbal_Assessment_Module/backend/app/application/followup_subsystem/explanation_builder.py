"""
Module: Construct Explanation Builder (v6).
Aggregates individual ConstructExplanations into a comprehensive, audit-ready AssessmentExplanation report.
"""

import hashlib
import json
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import List, Dict, Any
from app.application.followup_subsystem.reasoning_engine import ConstructExplanation


@dataclass(frozen=True)
class AssessmentExplanation:
    session_id: str
    candidate_id: str
    timestamp: str
    overall_confidence: float
    construct_explanations: Dict[str, Dict[str, Any]]
    key_strengths: List[str]
    growth_areas: List[str]
    audit_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "candidate_id": self.candidate_id,
            "timestamp": self.timestamp,
            "overall_confidence": self.overall_confidence,
            "construct_explanations": self.construct_explanations,
            "key_strengths": self.key_strengths,
            "growth_areas": self.growth_areas,
            "audit_hash": self.audit_hash,
        }


class ConstructExplanationBuilder:
    """Assembles construct explanations into an immutable, audit-hashed AssessmentExplanation object."""

    def build_assessment_explanation(
        self,
        session_id: str,
        candidate_id: str,
        explanations: List[ConstructExplanation],
    ) -> AssessmentExplanation:

        now_str = datetime.now(timezone.utc).isoformat()
        expl_dict: Dict[str, Dict[str, Any]] = {}
        total_conf = 0.0

        strengths: List[str] = []
        growth: List[str] = []

        for e in explanations:
            expl_dict[e.construct_name] = e.to_dict()
            total_conf += e.confidence

            if e.score >= 0.75:
                strengths.append(f"High evidence consistency and performance in '{e.construct_name}' (Score: {e.score * 100:.0f}%)")
            elif e.score < 0.50 or e.missing_evidence:
                growth.append(f"Further construct evidence recommended for '{e.construct_name}' (Score: {e.score * 100:.0f}%)")

        overall_conf = round(total_conf / max(len(explanations), 1), 2)

        # Generate SHA-256 Audit Hash
        raw_bytes = json.dumps(expl_dict, sort_keys=True).encode("utf-8")
        audit_hash = hashlib.sha256(raw_bytes).hexdigest()

        return AssessmentExplanation(
            session_id=session_id,
            candidate_id=candidate_id,
            timestamp=now_str,
            overall_confidence=overall_conf,
            construct_explanations=expl_dict,
            key_strengths=strengths,
            growth_areas=growth,
            audit_hash=audit_hash,
        )
