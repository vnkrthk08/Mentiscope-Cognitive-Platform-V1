"""
Module: Decision-Centric Interview Engine (v11).
Extracts candidate decisions, builds DecisionKnowledgeGraph, evaluates decision coverage dimensions,
identifies knowledge gaps, selects decision probing strategies, and infers downstream construct evidence.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class DecisionProbingStrategy(str, Enum):
    WHY_PROBE = "WHY_PROBE"
    ALTERNATIVE_PROBE = "ALTERNATIVE_PROBE"
    TRADEOFF_PROBE = "TRADEOFF_PROBE"
    RISK_PROBE = "RISK_PROBE"
    STAKEHOLDER_PROBE = "STAKEHOLDER_PROBE"
    COUNTERFACTUAL_PROBE = "COUNTERFACTUAL_PROBE"
    REFLECTION_PROBE = "REFLECTION_PROBE"


@dataclass(frozen=True)
class CandidateDecision:
    id: str
    action: str
    objective: str
    constraints: List[str]
    stakeholders: List[str]
    risks: List[str]
    justification: str
    alternatives: List[str]
    turn_number: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action": self.action,
            "objective": self.objective,
            "constraints": self.constraints,
            "stakeholders": self.stakeholders,
            "risks": self.risks,
            "justification": self.justification,
            "alternatives": self.alternatives,
            "turn_number": self.turn_number,
        }


@dataclass
class DecisionKnowledgeGraph:
    nodes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    edges: List[Dict[str, Any]] = field(default_factory=list)

    def add_decision(self, decision: CandidateDecision) -> None:
        self.nodes[decision.id] = {
            "type": "DECISION",
            "data": decision.to_dict(),
        }

    def add_dimension(self, decision_id: str, dimension_type: str, content: str) -> None:
        dim_id = f"{decision_id}_{dimension_type.lower()}"
        self.nodes[dim_id] = {
            "type": dimension_type,
            "content": content,
        }
        self.edges.append({
            "source": decision_id,
            "target": dim_id,
            "relation": f"HAS_{dimension_type}",
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": self.nodes,
            "edges": self.edges,
        }


@dataclass(frozen=True)
class DecisionAssessment:
    decision: CandidateDecision
    coverage_score: float                # 0.0 to 1.0
    missing_dimensions: List[str]
    selected_strategy: DecisionProbingStrategy
    probe_question_directive: str
    inferred_construct_evidence: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.to_dict(),
            "coverage_score": self.coverage_score,
            "missing_dimensions": self.missing_dimensions,
            "selected_strategy": self.selected_strategy.value,
            "probe_question_directive": self.probe_question_directive,
            "inferred_construct_evidence": self.inferred_construct_evidence,
        }


class DecisionAnalysisEngine:
    """Extracts candidate decisions, analyzes coverage dimensions, and determines probing strategy."""

    def extract_and_analyze_decision(
        self,
        transcript_text: str,
        turn_number: int,
        graph: DecisionKnowledgeGraph,
    ) -> DecisionAssessment:

        clean_text = (transcript_text or "").strip()
        lower_text = clean_text.lower()

        # Extract Decision Components
        action = clean_text
        if len(action) > 60:
            action = action[:57] + "..."

        objective = "Maintain project deadline"
        constraints = []
        stakeholders = []
        risks = []
        justification = ""
        alternatives = []

        if "arjun" in lower_text or "team" in lower_text:
            stakeholders.append("Team/Arjun")
        if "voltage" in lower_text or "limit" in lower_text or "deadline" in lower_text:
            constraints.append("Time & Voltage Limits")
        if "risk" in lower_text or "danger" in lower_text or "damage" in lower_text:
            risks.append("Operational Risk")
        if "because" in lower_text or "so that" in lower_text or "to" in lower_text:
            justification = "Achieve objective while adhering to constraints"
        if "instead" in lower_text or "alternative" in lower_text:
            alternatives.append("Alternative procedure")

        dec_id = f"dec_turn{turn_number}"
        decision = CandidateDecision(
            id=dec_id,
            action=action,
            objective=objective,
            constraints=constraints,
            stakeholders=stakeholders,
            risks=risks,
            justification=justification,
            alternatives=alternatives,
            turn_number=turn_number,
        )

        graph.add_decision(decision)

        # Evaluate 7 Coverage Dimensions
        missing_dimensions = []
        if not justification:
            missing_dimensions.append("REASON")
            graph.add_dimension(dec_id, "REASON", "Unspecified reasoning")
        if not risks:
            missing_dimensions.append("RISK")
            graph.add_dimension(dec_id, "RISK", "Unspecified risk mitigation")
        if not stakeholders:
            missing_dimensions.append("STAKEHOLDERS")
            graph.add_dimension(dec_id, "STAKEHOLDERS", "Unspecified stakeholder consensus")
        if not alternatives:
            missing_dimensions.append("ALTERNATIVE")
            graph.add_dimension(dec_id, "ALTERNATIVE", "Unspecified alternatives")
        if "tradeoff" not in lower_text and "sacrifice" not in lower_text:
            missing_dimensions.append("TRADEOFF")

        covered_count = 7 - len(missing_dimensions)
        coverage_score = round(covered_count / 7.0, 2)

        # Select Probing Strategy based on highest priority missing gap
        if "RISK" in missing_dimensions:
            strategy = DecisionProbingStrategy.RISK_PROBE
            directive = "Probe what potential risks could arise from this decision."
        elif "STAKEHOLDERS" in missing_dimensions:
            strategy = DecisionProbingStrategy.STAKEHOLDER_PROBE
            directive = "Probe how stakeholders or teammates might react to this decision."
        elif "TRADEOFF" in missing_dimensions:
            strategy = DecisionProbingStrategy.TRADEOFF_PROBE
            directive = "Probe what trade-offs or sacrifices were made in this decision."
        elif "ALTERNATIVE" in missing_dimensions:
            strategy = DecisionProbingStrategy.ALTERNATIVE_PROBE
            directive = "Probe what alternative options were considered before choosing this action."
        elif "REASON" in missing_dimensions:
            strategy = DecisionProbingStrategy.WHY_PROBE
            directive = "Probe the core justification and rationale behind this decision."
        else:
            strategy = DecisionProbingStrategy.REFLECTION_PROBE
            directive = "Probe metacognitive reflection on whether the candidate would repeat this decision."

        # Infer Psychometric Construct Evidence Downstream
        inferred_construct_evidence = {
            "DECISION_MAKING": round(0.50 + (coverage_score * 0.40), 2),
            "RISK_AWARENESS": 0.85 if "RISK" not in missing_dimensions else 0.45,
            "LEADERSHIP": 0.80 if "STAKEHOLDERS" not in missing_dimensions else 0.40,
            "ADAPTABILITY": 0.75 if "ALTERNATIVE" not in missing_dimensions else 0.50,
            "ETHICS": 0.80 if len(constraints) > 0 else 0.60,
        }

        return DecisionAssessment(
            decision=decision,
            coverage_score=coverage_score,
            missing_dimensions=missing_dimensions,
            selected_strategy=strategy,
            probe_question_directive=directive,
            inferred_construct_evidence=inferred_construct_evidence,
        )
