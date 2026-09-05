"""
Module: Evidence Reasoning Engine (v6).
Traverses the BehavioralEvidenceGraph to extract supporting/contradictory evidence and produce deterministic score rationale.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.evidence_graph import BehavioralEvidenceGraph, NodeType, EdgeType
from app.application.followup_subsystem.closure_engine import ConstructSaturationMetrics


@dataclass(frozen=True)
class EvidenceItemDetail:
    quote: str
    indicator: str
    turn_number: int
    confidence: float
    node_type: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quote": self.quote,
            "indicator": self.indicator,
            "turn_number": self.turn_number,
            "confidence": self.confidence,
            "node_type": self.node_type,
        }


@dataclass(frozen=True)
class ConstructExplanation:
    construct_name: str
    score: float                         # Normalized score (0.0 to 1.0)
    confidence: float                    # Evaluated confidence (0.0 to 1.0)
    saturation_score: float              # Multi-dimensional saturation index
    supporting_evidence: List[Dict[str, Any]]
    contradictory_evidence: List[Dict[str, Any]]
    missing_evidence: List[str]
    behavioral_summary: str              # Concise behavioral summary
    reasoning_summary: str               # Deterministic explanation of score rationale
    confidence_reason: str               # Mathematical justification for confidence rating

    def to_dict(self) -> Dict[str, Any]:
        return {
            "construct_name": self.construct_name,
            "score": self.score,
            "confidence": self.confidence,
            "saturation_score": self.saturation_score,
            "supporting_evidence": self.supporting_evidence,
            "contradictory_evidence": self.contradictory_evidence,
            "missing_evidence": self.missing_evidence,
            "behavioral_summary": self.behavioral_summary,
            "reasoning_summary": self.reasoning_summary,
            "confidence_reason": self.confidence_reason,
        }


class EvidenceReasoningEngine:
    """Traverses the BehavioralEvidenceGraph to produce deterministic explanations for construct scores."""

    def explain_construct(
        self,
        construct_name: str,
        graph: BehavioralEvidenceGraph,
        saturation_metrics: Optional[ConstructSaturationMetrics] = None,
        score: float = 0.8,
    ) -> ConstructExplanation:

        supporting: List[Dict[str, Any]] = []
        contradictory: List[Dict[str, Any]] = []

        # Traverse edges for supporting / contradictory signals
        for edge in graph.edges:
            source_node = graph.nodes.get(edge.source_id)
            if source_node and (source_node.metadata.get("construct") == construct_name or construct_name.lower() in source_node.content.lower()):
                detail = EvidenceItemDetail(
                    quote=source_node.content,
                    indicator=source_node.label,
                    turn_number=source_node.turn_number,
                    confidence=source_node.confidence,
                    node_type=source_node.node_type.value,
                ).to_dict()

                if edge.edge_type == EdgeType.SUPPORTS:
                    if detail not in supporting:
                        supporting.append(detail)
                elif edge.edge_type == EdgeType.CONTRADICTS:
                    if detail not in contradictory:
                        contradictory.append(detail)

        # Fallback if graph nodes don't have explicit edges
        if not supporting and not contradictory:
            c_nodes = [n for n in graph.nodes.values() if n.metadata.get("construct") == construct_name or construct_name.lower() in n.content.lower()]
            for n in c_nodes:
                supporting.append(
                    EvidenceItemDetail(
                        quote=n.content,
                        indicator=n.label,
                        turn_number=n.turn_number,
                        confidence=n.confidence,
                        node_type=n.node_type.value,
                    ).to_dict()
                )

        sat_val = saturation_metrics.saturation_score if saturation_metrics else 0.5
        is_sat = saturation_metrics.is_saturated if saturation_metrics else False
        conf_val = saturation_metrics.confidence_score if saturation_metrics else 0.75

        missing: List[str] = []
        if not is_sat:
            missing.append(f"Additional evidence required to reach saturation for {construct_name}")

        reasoning = (
            f"Construct '{construct_name}' scored {score * 100:.1f}% based on {len(supporting)} supporting evidence signal(s) "
            f"and {len(contradictory)} contradiction(s). Evidence saturation reached {sat_val * 100:.1f}%."
        )

        conf_reason = (
            f"Confidence rated at {conf_val * 100:.1f}% based on evidence graph node diversity ({graph.calculate_diversity_score() * 100:.0f}%) "
            f"and contradiction frequency ({graph.get_contradiction_count()} contradiction(s) detected)."
        )

        return ConstructExplanation(
            construct_name=construct_name,
            score=round(score, 2),
            confidence=round(conf_val, 2),
            saturation_score=round(sat_val, 2),
            supporting_evidence=supporting,
            contradictory_evidence=contradictory,
            missing_evidence=missing,
            behavioral_summary=f"Candidate demonstrated {len(supporting)} observable indicator(s) for {construct_name}.",
            reasoning_summary=reasoning,
            confidence_reason=conf_reason,
        )
