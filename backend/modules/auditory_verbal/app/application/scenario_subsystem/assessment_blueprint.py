"""
Module: Assessment Blueprint Generator (Assessment Assembly Engine v1.0).
Generates the 5-slot assessment blueprint defining construct targets, category constraints, and difficulty targets.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.scenario_subsystem.scenario_metadata import (
    StakeholderType,
    CommunicationStyle,
    DecisionType,
    InteractionType,
    ScenarioType,
)


@dataclass(frozen=True)
class SlotBlueprint:
    slot_number: int                     # 1 to 5
    target_difficulty: str               # EASY, EASY_MEDIUM, MEDIUM, MEDIUM_HARD, HARD
    required_primary_construct: str
    required_secondary_constructs: List[str]
    preferred_scenario_type: ScenarioType
    preferred_interaction_type: InteractionType
    preferred_decision_type: DecisionType
    preferred_stakeholder: StakeholderType
    preferred_communication_style: CommunicationStyle
    ethical_dimension_required: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slot_number": self.slot_number,
            "target_difficulty": self.target_difficulty,
            "required_primary_construct": self.required_primary_construct,
            "required_secondary_constructs": self.required_secondary_constructs,
            "preferred_scenario_type": self.preferred_scenario_type.value,
            "preferred_interaction_type": self.preferred_interaction_type.value,
            "preferred_decision_type": self.preferred_decision_type.value,
            "preferred_stakeholder": self.preferred_stakeholder.value,
            "preferred_communication_style": self.preferred_communication_style.value,
            "ethical_dimension_required": self.ethical_dimension_required,
        }


@dataclass
class AssessmentBlueprint:
    blueprint_id: str
    candidate_id: str
    target_construct_coverage: Dict[str, int]
    slots: List[SlotBlueprint]
    category_rotation_rule: str = "MAX_1_PER_CATEGORY"
    family_exclusion_rule: str = "NO_DUPLICATE_FAMILY"
    difficulty_progression: List[str] = field(default_factory=lambda: ["EASY", "EASY_MEDIUM", "MEDIUM", "MEDIUM_HARD", "HARD"])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blueprint_id": self.blueprint_id,
            "candidate_id": self.candidate_id,
            "target_construct_coverage": self.target_construct_coverage,
            "slots": [s.to_dict() for s in self.slots],
            "category_rotation_rule": self.category_rotation_rule,
            "family_exclusion_rule": self.family_exclusion_rule,
            "difficulty_progression": self.difficulty_progression,
        }


class AssessmentBlueprintGenerator:
    """Generates 5-slot assessment blueprints satisfying psychometric coverage targets."""

    def generate_blueprint(self, blueprint_id: str, candidate_id: str) -> AssessmentBlueprint:
        # Predefined construct targets across 5 scenarios
        target_coverage = {
            "Decision Making": 3,
            "Leadership": 2,
            "Communication": 2,
            "Risk Awareness": 2,
            "Adaptability": 2,
            "Problem Solving": 2,
            "Critical Thinking": 2,
            "Ethics": 2,
            "Planning": 2,
        }

        diffs = ["EASY", "EASY_MEDIUM", "MEDIUM", "MEDIUM_HARD", "HARD"]
        primary_constructs = ["Decision Making", "Leadership", "Risk Awareness", "Adaptability", "Ethics"]
        sec_constructs = [
            ["Communication", "Critical Thinking"],
            ["Problem Solving", "Planning"],
            ["Ethics", "Communication"],
            ["Leadership", "Risk Awareness"],
            ["Decision Making", "Adaptability"],
        ]

        scen_types = [
            ScenarioType.INDIVIDUAL_DECISION,
            ScenarioType.TEAM_LEADERSHIP,
            ScenarioType.ETHICAL_DILEMMA,
            ScenarioType.PLANNING,
            ScenarioType.CRISIS_RESPONSE,
        ]

        inter_types = [
            InteractionType.DIRECT_DECISION,
            InteractionType.TEAM_NEGOTIATION,
            InteractionType.SOCRATIC_INQUIRY,
            InteractionType.DIRECT_DECISION,
            InteractionType.CRISIS_RESPONSE,
        ]

        dec_types = [
            DecisionType.RESOURCE_ALLOCATION,
            DecisionType.PRIORITIZATION,
            DecisionType.ETHICS,
            DecisionType.PLANNING,
            DecisionType.RISK_MITIGATION,
        ]

        stakeholders = [
            StakeholderType.TEACHER,
            StakeholderType.FRIEND,
            StakeholderType.PRINCIPAL,
            StakeholderType.PARENT,
            StakeholderType.COACH,
        ]

        comm_styles = [
            CommunicationStyle.EXPLANATION,
            CommunicationStyle.CONFLICT_RESOLUTION,
            CommunicationStyle.DECISION_JUSTIFICATION,
            CommunicationStyle.PRESENTATION,
            CommunicationStyle.NEGOTIATION,
        ]

        slots = []
        for i in range(5):
            slot = SlotBlueprint(
                slot_number=i + 1,
                target_difficulty=diffs[i],
                required_primary_construct=primary_constructs[i],
                required_secondary_constructs=sec_constructs[i],
                preferred_scenario_type=scen_types[i],
                preferred_interaction_type=inter_types[i],
                preferred_decision_type=dec_types[i],
                preferred_stakeholder=stakeholders[i],
                preferred_communication_style=comm_styles[i],
                ethical_dimension_required=(i == 2),
            )
            slots.append(slot)

        return AssessmentBlueprint(
            blueprint_id=blueprint_id,
            candidate_id=candidate_id,
            target_construct_coverage=target_coverage,
            slots=slots,
        )
