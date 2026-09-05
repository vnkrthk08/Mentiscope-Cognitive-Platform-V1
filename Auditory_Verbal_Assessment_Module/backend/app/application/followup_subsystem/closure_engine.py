"""
Module: Construct Saturation Engine & Interview Closure Engine.
Calculates multi-dimensional construct saturation scores and deterministically decides interview termination.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.evidence_graph import BehavioralEvidenceGraph, NodeType, EdgeType
from app.application.followup_subsystem.conversation_state import ConversationState


@dataclass
class ConstructSaturationMetrics:
    construct_name: str
    coverage_score: float       # 0.0 to 1.0
    confidence_score: float     # 0.0 to 1.0
    evidence_diversity: float   # 0.0 to 1.0
    evidence_consistency: float # 0.0 to 1.0
    evidence_freshness: float   # 0.0 to 1.0
    evidence_novelty: float     # 0.0 to 1.0
    saturation_score: float     # Integrated Saturation Index (0.0 to 1.0)
    is_saturated: bool          # True if saturation_score >= 0.75

    def to_dict(self) -> Dict[str, Any]:
        return {
            "construct_name": self.construct_name,
            "coverage_score": self.coverage_score,
            "confidence_score": self.confidence_score,
            "evidence_diversity": self.evidence_diversity,
            "evidence_consistency": self.evidence_consistency,
            "evidence_freshness": self.evidence_freshness,
            "evidence_novelty": self.evidence_novelty,
            "saturation_score": self.saturation_score,
            "is_saturated": self.is_saturated,
        }


class ConstructSaturationEngine:
    """Calculates multi-dimensional saturation metrics per construct using the BehavioralEvidenceGraph."""

    def calculate_saturation(
        self,
        graph: BehavioralEvidenceGraph,
        target_constructs: List[str],
        state: ConversationState,
    ) -> Dict[str, ConstructSaturationMetrics]:

        results: Dict[str, ConstructSaturationMetrics] = {}
        ev_nodes = graph.get_nodes_by_type(NodeType.EVIDENCE)
        diversity = graph.calculate_diversity_score()
        contradictions = graph.get_contradiction_count()
        consistency = max(0.0, 1.0 - (contradictions * 0.2))

        for c in target_constructs:
            c_nodes = [n for n in ev_nodes if n.metadata.get("construct") == c or c.lower() in n.content.lower()]
            ev_count = len(c_nodes)

            cov = min(ev_count * 0.35, 1.0)
            conf = round(sum(n.confidence for n in c_nodes) / max(ev_count, 1), 2) if c_nodes else 0.0
            freshness = 1.0 if any(n.turn_number >= max(state.turn_number - 1, 1) for n in c_nodes) else 0.5
            novelty = min(0.4 + (ev_count * 0.2), 1.0)

            # Weighted Saturation Score Index
            sat = round(0.25 * cov + 0.25 * conf + 0.20 * diversity + 0.15 * consistency + 0.15 * freshness, 2)
            is_sat = sat >= 0.75

            results[c] = ConstructSaturationMetrics(
                construct_name=c,
                coverage_score=round(cov, 2),
                confidence_score=round(conf, 2),
                evidence_diversity=diversity,
                evidence_consistency=round(consistency, 2),
                evidence_freshness=round(freshness, 2),
                evidence_novelty=round(novelty, 2),
                saturation_score=sat,
                is_saturated=is_sat,
            )

        return results


@dataclass
class ClosureDecision:
    should_close: bool
    closure_reason: str
    saturation_percentage: float
    remaining_constructs: List[str]
    unresolved_contradictions_count: int
    completion_percentage: float
    estimated_remaining_turns: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "should_close": self.should_close,
            "closure_reason": self.closure_reason,
            "saturation_percentage": self.saturation_percentage,
            "remaining_constructs": self.remaining_constructs,
            "unresolved_contradictions_count": self.unresolved_contradictions_count,
            "completion_percentage": self.completion_percentage,
            "estimated_remaining_turns": self.estimated_remaining_turns,
        }


class InterviewClosureEngine:
    """Deterministically evaluates evidence sufficiency and graph metrics to decide interview termination."""

    def evaluate_closure(
        self,
        graph: BehavioralEvidenceGraph,
        saturation_matrix: Dict[str, ConstructSaturationMetrics],
        state: ConversationState,
        target_constructs: List[str],
    ) -> ClosureDecision:

        total_targets = len(target_constructs)
        saturated_list = [c for c, m in saturation_matrix.items() if m.is_saturated]
        remaining_list = [c for c in target_constructs if c not in saturated_list]

        sat_pct = round((len(saturated_list) / max(total_targets, 1)) * 100.0, 1)
        contradictions = graph.get_contradiction_count()
        diversity = graph.calculate_diversity_score()

        completion_pct = round(min((sat_pct * 0.7) + (diversity * 30.0), 100.0), 1)

        # Condition 1: Overall Remaining Uncertainty < 0.10 across turns
        overall_uncertainty = getattr(state, "overall_uncertainty", 0.50)
        if overall_uncertainty < 0.10:
            return ClosureDecision(
                should_close=True,
                closure_reason="Overall candidate model uncertainty is below threshold (< 0.10). Further questions yield negligible information gain.",
                saturation_percentage=100.0,
                remaining_constructs=[],
                unresolved_contradictions_count=contradictions,
                completion_percentage=100.0,
                estimated_remaining_turns=0,
            )

        # Condition 2: All required constructs saturated & no unresolved contradictions
        if len(remaining_list) == 0 and contradictions == 0:
            return ClosureDecision(
                should_close=True,
                closure_reason="All target constructs saturated with consistent evidence.",
                saturation_percentage=100.0,
                remaining_constructs=[],
                unresolved_contradictions_count=0,
                completion_percentage=100.0,
                estimated_remaining_turns=0,
            )

        # Condition 2: Maximum evidence saturation reached across turns (Turn >= 4 and sat_pct >= 80%)
        if state.turn_number >= 4 and sat_pct >= 80.0:
            return ClosureDecision(
                should_close=True,
                closure_reason="Evidence saturation threshold reached across turns.",
                saturation_percentage=sat_pct,
                remaining_constructs=remaining_list,
                unresolved_contradictions_count=contradictions,
                completion_percentage=completion_pct,
                estimated_remaining_turns=0,
            )

        # Estimate remaining turns
        est_remaining = max(len(remaining_list), 1) if not remaining_list else len(remaining_list)

        return ClosureDecision(
            should_close=False,
            closure_reason=f"Interview active. {len(remaining_list)} construct(s) require evidence saturation.",
            saturation_percentage=sat_pct,
            remaining_constructs=remaining_list,
            unresolved_contradictions_count=contradictions,
            completion_percentage=completion_pct,
            estimated_remaining_turns=est_remaining,
        )


# Alias for Module 10 (AIIS v15 10-Module Pipeline)
InterviewCompletionEngine = InterviewClosureEngine
