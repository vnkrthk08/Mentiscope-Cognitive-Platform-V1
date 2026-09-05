"""
Layer 3: Scenario Grammar Engine (10 Reusable Narrative Sequences)
Defines HOW the story unfolds.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class ScenarioGrammar:
    name: str
    description: str
    sequence_beats: List[str]


class ScenarioGrammarEngine:
    """Provides 10 reusable narrative sequence grammars."""

    GRAMMARS: Dict[str, ScenarioGrammar] = {
        "Crisis Response": ScenarioGrammar(
            name="Crisis Response",
            description="Immediate catalyst incident requiring rapid containment under time pressure.",
            sequence_beats=[
                "Immediate Catalyst Incident",
                "Severe Operational Time Pressure",
                "Unexpected Secondary Escalation",
                "Containment & Decision Resolution",
            ],
        ),
        "Progressive Discovery": ScenarioGrammar(
            name="Progressive Discovery",
            description="Initial anomaly leading to systematic investigation uncovering root cause.",
            sequence_beats=[
                "Initial Anomaly Detection",
                "Systematic Evidence Gathering",
                "Uncovering Hidden Root Cause",
                "Targeted Remediation Strategy",
            ],
        ),
        "Stakeholder Conflict": ScenarioGrammar(
            name="Stakeholder Conflict",
            description="Competing stakeholder demands requiring diplomatic trade-off mediation.",
            sequence_beats=[
                "Competing Stakeholder Claims",
                "Stakeholder Pushback & Tension",
                "Trade-off Mediation Analysis",
                "Consensus Alignment Agreement",
            ],
        ),
        "Resource Allocation": ScenarioGrammar(
            name="Resource Allocation",
            description="Asset scarcity forcing priority trade-off evaluation under deadlines.",
            sequence_beats=[
                "Resource Scarcity Discovery",
                "Evaluation Matrix Assessment",
                "Priority Selection Trade-off",
                "Operational Plan Execution",
            ],
        ),
        "Ethical Dilemma": ScenarioGrammar(
            name="Ethical Dilemma",
            description="Competing ethical values requiring moral rationale defense.",
            sequence_beats=[
                "Competing Core Values Conflict",
                "Stakeholder Impact Evaluation",
                "Ethical Rationale Formulation",
                "Corrective Protocol Action",
            ],
        ),
        "Strategic Planning": ScenarioGrammar(
            name="Strategic Planning",
            description="System goal interrupted by bottleneck requiring pivot strategy.",
            sequence_beats=[
                "System Goal Objective",
                "Bottleneck Identification",
                "Pivot Strategy Proposal",
                "Demonstration & Validation",
            ],
        ),
        "Negotiation Cycle": ScenarioGrammar(
            name="Negotiation Cycle",
            description="Initial positions resolving into compromise bargaining and agreement.",
            sequence_beats=[
                "Initial Stance Presentation",
                "Counter-proposal Challenge",
                "Compromise Bargaining Phase",
                "Executable Contract Agreement",
            ],
        ),
        "Investigation": ScenarioGrammar(
            name="Investigation",
            description="Symptom report driving rigorous evidence collection and finding.",
            sequence_beats=[
                "Symptom Report Alert",
                "Archival Evidence Collection",
                "Hypothesis Testing Audit",
                "Conclusive Finding Report",
            ],
        ),
        "Recovery After Failure": ScenarioGrammar(
            name="Recovery After Failure",
            description="Operational breakdown managed by immediate control and reconstruction.",
            sequence_beats=[
                "Operational Breakdown Fault",
                "Immediate Damage Control",
                "Systematic Reconstruction",
                "Preventive Protocol Standard",
            ],
        ),
        "Collaborative Solving": ScenarioGrammar(
            name="Collaborative Solving",
            description="Disparate team inputs integrated into unified consensus plan.",
            sequence_beats=[
                "Disparate Team Inputs",
                "Cross-functional Integration",
                "Team Consensus Alignment",
                "Field Trial Demonstration",
            ],
        ),
    }

    @classmethod
    def get_grammar(cls, name: str) -> ScenarioGrammar:
        return cls.GRAMMARS.get(name, cls.GRAMMARS["Crisis Response"])

    @classmethod
    def list_grammars(cls) -> List[str]:
        return list(cls.GRAMMARS.keys())
