"""
Module 3.5: Evidence Sufficiency Engine (AIIS v16.0.0 Architecture).
Evaluates qualitative Evidence Sufficiency Levels (MISSING, WEAK, PARTIAL, STRONG, SATURATED)
and numerical quality scores (0.0 to 1.0) for every decision dimension.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.interview_understanding import CandidateDecisionData
from app.application.followup_subsystem.memory import InterviewMemory


class EvidenceLevel(str, Enum):
    MISSING = "MISSING"     # Score < 0.20 — No evidence stated
    WEAK = "WEAK"           # Score 0.20-0.49 — Superficial / vague mention ("Because it felt right")
    PARTIAL = "PARTIAL"     # Score 0.50-0.74 — Basic explanation ("Saves 10 minutes")
    STRONG = "STRONG"       # Score 0.75-0.89 — Detailed, multi-faceted rationale
    SATURATED = "SATURATED" # Score >= 0.90 — Fully saturated evidence across turns


@dataclass(frozen=True)
class DimensionSufficiency:
    dimension_name: str
    score: float            # 0.0 to 1.0
    level: EvidenceLevel
    indicator_quote: Optional[str]
    deficit: float          # 1.0 - score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension_name": self.dimension_name,
            "score": round(self.score, 2),
            "level": self.level.value,
            "indicator_quote": self.indicator_quote,
            "deficit": round(self.deficit, 2),
        }


class EvidenceSufficiencyEngine:
    """Module 3.5: Evaluates evidence quality scores and levels per decision dimension."""

    DIMENSION_IMPORTANCE: Dict[str, float] = {
        "Reason": 0.95,
        "Risk": 0.90,
        "Stakeholders": 0.85,
        "Alternatives": 0.78,
        "Tradeoffs": 0.72,
        "Reflection": 0.65,
    }

    def evaluate_sufficiency(
        self,
        decision: CandidateDecisionData,
        memory: InterviewMemory,
        transcript_text: str,
    ) -> Dict[str, DimensionSufficiency]:

        clean_text = (transcript_text or "").strip()
        lower_text = clean_text.lower()
        words = clean_text.split()
        word_count = len(words)

        results: Dict[str, DimensionSufficiency] = {}

        # 1. Evaluate Decision Action
        act_score = 0.0
        if decision.action or memory.candidate_decisions:
            act_score = 0.85 if word_count > 6 else 0.55
        results["Decision"] = self._build_sufficiency("Decision", act_score, decision.action)

        # 2. Evaluate Reason (Justification depth)
        reason_score = 0.0
        r_quote = decision.reason or (memory.stated_reasons[-1] if memory.stated_reasons else None)
        weak_phrases = ["felt right", "seemed right", "wanted to", "guess so", "just because", "no reason"]

        if any(wp in lower_text for wp in weak_phrases):
            reason_score = 0.25  # WEAK
        elif r_quote or "because" in lower_text or "since" in lower_text or "so that" in lower_text:
            if word_count >= 15 or "and" in lower_text or "prevent" in lower_text or "ensure" in lower_text:
                reason_score = 0.85  # STRONG
            else:
                reason_score = 0.60  # PARTIAL
        results["Reason"] = self._build_sufficiency("Reason", reason_score, r_quote)

        # 3. Evaluate Risk Awareness
        risk_score = 0.0
        risk_quote = decision.risks[0] if decision.risks else (memory.stated_risks[-1] if memory.stated_risks else None)
        if risk_quote or any(w in lower_text for w in ["risk", "danger", "fail", "damage", "explode", "break"]):
            if word_count > 12 or len(decision.risks) >= 2:
                risk_score = 0.85
            else:
                risk_score = 0.55
        results["Risk"] = self._build_sufficiency("Risk", risk_score, risk_quote)

        # 4. Evaluate Stakeholders
        stk_score = 0.0
        stk_quote = decision.stakeholders[0] if decision.stakeholders else (memory.mentioned_stakeholders[-1] if memory.mentioned_stakeholders else None)
        if stk_quote or any(w in lower_text for w in ["teacher", "team", "teammate", "principal", "judge", "student"]):
            if len(decision.stakeholders) >= 2 or "inform" in lower_text or "discuss" in lower_text:
                stk_score = 0.85
            else:
                stk_score = 0.55
        results["Stakeholders"] = self._build_sufficiency("Stakeholders", stk_score, stk_quote)

        # 5. Evaluate Alternatives
        alt_score = 0.0
        alt_quote = decision.alternatives[0] if decision.alternatives else (memory.proposed_alternatives[-1] if memory.proposed_alternatives else None)
        if alt_quote or any(w in lower_text for w in ["instead", "alternative", "other option", "considered"]):
            alt_score = 0.80 if word_count > 10 else 0.50
        results["Alternatives"] = self._build_sufficiency("Alternatives", alt_score, alt_quote)

        # 6. Evaluate Tradeoffs
        to_score = 0.0
        to_quote = decision.tradeoffs[0] if decision.tradeoffs else (memory.stated_tradeoffs[-1] if memory.stated_tradeoffs else None)
        if to_quote or any(w in lower_text for w in ["tradeoff", "sacrifice", "compromise", "cost"]):
            to_score = 0.80 if word_count > 10 else 0.50
        results["Tradeoffs"] = self._build_sufficiency("Tradeoffs", to_score, to_quote)

        # 7. Evaluate Reflection
        ref_score = 0.0
        if decision.reflection or any(w in lower_text for w in ["reflect", "learned", "looking back", "in hindsight"]):
            ref_score = 0.80
        results["Reflection"] = self._build_sufficiency("Reflection", ref_score, decision.reflection)

        return results

    def _build_sufficiency(self, name: str, score: float, quote: Optional[str]) -> DimensionSufficiency:
        if score >= 0.90:
            level = EvidenceLevel.SATURATED
        elif score >= 0.75:
            level = EvidenceLevel.STRONG
        elif score >= 0.50:
            level = EvidenceLevel.PARTIAL
        elif score >= 0.20:
            level = EvidenceLevel.WEAK
        else:
            level = EvidenceLevel.MISSING

        return DimensionSufficiency(
            dimension_name=name,
            score=score,
            level=level,
            indicator_quote=quote,
            deficit=max(0.0, 1.0 - score),
        )
