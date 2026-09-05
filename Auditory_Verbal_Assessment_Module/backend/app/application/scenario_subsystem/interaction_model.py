"""
Layer 4: Candidate Interaction Model Engine (8 Candidate Assessment Interaction Models)
Defines HOW the candidate experiences the assessment.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class InteractionModel:
    name: str
    description: str
    candidate_flow: List[str]


class InteractionModelEngine:
    """Provides 8 candidate assessment interaction models."""

    MODELS: Dict[str, InteractionModel] = {
        "Direct Decision Making": InteractionModel(
            name="Direct Decision Making",
            description="Immediate trade-off decision followed by rationale defense.",
            candidate_flow=[
                "Receive immediate trade-off scenario context",
                "Formulate primary decision response",
                "Defend strategic rationale under questioning",
                "Evaluate operational impact and risk",
            ],
        ),
        "Stakeholder Interview": InteractionModel(
            name="Stakeholder Interview",
            description="Synthesizing conflicting stakeholder briefs into aligned stance.",
            candidate_flow=[
                "Review conflicting stakeholder briefs",
                "Inquire and synthesize priority requirements",
                "Formulate aligned strategic position",
                "Present compromise solution to stakeholders",
            ],
        ),
        "Resource Trade-off Negotiation": InteractionModel(
            name="Resource Trade-off Negotiation",
            description="Allocating constrained assets and defending trade-offs.",
            candidate_flow=[
                "Analyze constrained resource inventory",
                "Select priority allocation plan",
                "Defend trade-off choices against alternatives",
                "Adjust allocation under adaptive challenge",
            ],
        ),
        "Diagnostic Troubleshooting": InteractionModel(
            name="Diagnostic Troubleshooting",
            description="Isolating root cause from symptom telemetry.",
            candidate_flow=[
                "Analyze symptom report and telemetry logs",
                "Isolate root cause hypothesis",
                "Formulate targeted remediation plan",
                "Reflect on preventive protocol standards",
            ],
        ),
        "Crisis Communication": InteractionModel(
            name="Crisis Communication",
            description="Delivering urgent incident briefing and action plan.",
            candidate_flow=[
                "Receive urgent incident alert",
                "Deliver immediate team/public briefing",
                "Outline structured emergency action steps",
                "Reassure key stakeholders under pressure",
            ],
        ),
        "Policy & Dispute Defense": InteractionModel(
            name="Policy & Dispute Defense",
            description="Auditing policy clause dispute and formulating position.",
            candidate_flow=[
                "Audit disputed policy clause or rule",
                "Formulate compliant position statement",
                "Defend policy adherence against pushback",
                "Propose formal resolution amendment",
            ],
        ),
        "Strategic Prioritization": InteractionModel(
            name="Strategic Prioritization",
            description="Triaging competing demands into execution roadmap.",
            candidate_flow=[
                "Triage multiple competing project demands",
                "Construct execution priority roadmap",
                "Justify deferred or deprioritized tasks",
                "Adapt roadmap to unexpected constraint change",
            ],
        ),
        "Consensus Mediation": InteractionModel(
            name="Consensus Mediation",
            description="Proposing compromise to align divergent team members.",
            candidate_flow=[
                "Assess divergent team viewpoints",
                "Propose balanced compromise agreement",
                "Address stakeholder pushback and concerns",
                "Align team around unified execution plan",
            ],
        ),
    }

    @classmethod
    def get_model(cls, name: str) -> InteractionModel:
        return cls.MODELS.get(name, cls.MODELS["Direct Decision Making"])

    @classmethod
    def list_models(cls) -> List[str]:
        return list(cls.MODELS.keys())
