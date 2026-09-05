"""
Module: Scenario Metadata (Assessment Assembly Engine v1.0).
Defines comprehensive metadata schema for expert-authored scenarios.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class StakeholderType(str, Enum):
    TEACHER = "TEACHER"
    FRIEND = "FRIEND"
    PRINCIPAL = "PRINCIPAL"
    JUNIOR_STUDENT = "JUNIOR_STUDENT"
    COACH = "COACH"
    PARENT = "PARENT"
    COMMUNITY_MEMBER = "COMMUNITY_MEMBER"
    JUDGE = "JUDGE"


class CommunicationStyle(str, Enum):
    NEGOTIATION = "NEGOTIATION"
    PRESENTATION = "PRESENTATION"
    CONFLICT_RESOLUTION = "CONFLICT_RESOLUTION"
    EXPLANATION = "EXPLANATION"
    DECISION_JUSTIFICATION = "DECISION_JUSTIFICATION"
    REFLECTION = "REFLECTION"


class DecisionType(str, Enum):
    RESOURCE_ALLOCATION = "RESOURCE_ALLOCATION"
    PRIORITIZATION = "PRIORITIZATION"
    ETHICS = "ETHICS"
    RISK_MITIGATION = "RISK_MITIGATION"
    LEADERSHIP = "LEADERSHIP"
    PLANNING = "PLANNING"
    PROBLEM_DIAGNOSIS = "PROBLEM_DIAGNOSIS"
    TRADEOFF = "TRADEOFF"


class InteractionType(str, Enum):
    DIRECT_DECISION = "DIRECT_DECISION"
    TEAM_NEGOTIATION = "TEAM_NEGOTIATION"
    CRISIS_RESPONSE = "CRISIS_RESPONSE"
    SOCRATIC_INQUIRY = "SOCRATIC_INQUIRY"


class ScenarioType(str, Enum):
    INDIVIDUAL_DECISION = "INDIVIDUAL_DECISION"
    TEAM_LEADERSHIP = "TEAM_LEADERSHIP"
    ETHICAL_DILEMMA = "ETHICAL_DILEMMA"
    PLANNING = "PLANNING"
    CRISIS_RESPONSE = "CRISIS_RESPONSE"


@dataclass(frozen=True)
class ScenarioMetadata:
    scenario_id: str
    family_id: str
    variant_id: str
    category: str
    subcategory: str
    primary_constructs: List[str]
    secondary_constructs: List[str]
    cognitive_processes: List[str]
    interaction_type: InteractionType
    scenario_type: ScenarioType
    stakeholder_type: StakeholderType
    ethical_dimension: bool
    collaboration_level: str            # INDIVIDUAL, PAIR, TEAM
    decision_type: DecisionType
    communication_style: CommunicationStyle
    time_pressure: str                  # LOW, MODERATE, HIGH
    uncertainty_level: str              # LOW, MODERATE, HIGH
    complexity_level: str               # LOW, MODERATE, HIGH
    listening_difficulty: str           # EASY, EASY_MEDIUM, MEDIUM, MEDIUM_HARD, HARD
    speaking_difficulty: str            # EASY, EASY_MEDIUM, MEDIUM, MEDIUM_HARD, HARD
    estimated_duration: int             # Seconds
    prerequisite_tags: List[str] = field(default_factory=list)
    exclusion_tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "family_id": self.family_id,
            "variant_id": self.variant_id,
            "category": self.category,
            "subcategory": self.subcategory,
            "primary_constructs": self.primary_constructs,
            "secondary_constructs": self.secondary_constructs,
            "cognitive_processes": self.cognitive_processes,
            "interaction_type": self.interaction_type.value,
            "scenario_type": self.scenario_type.value,
            "stakeholder_type": self.stakeholder_type.value,
            "ethical_dimension": self.ethical_dimension,
            "collaboration_level": self.collaboration_level,
            "decision_type": self.decision_type.value,
            "communication_style": self.communication_style.value,
            "time_pressure": self.time_pressure,
            "uncertainty_level": self.uncertainty_level,
            "complexity_level": self.complexity_level,
            "listening_difficulty": self.listening_difficulty,
            "speaking_difficulty": self.speaking_difficulty,
            "estimated_duration": self.estimated_duration,
            "prerequisite_tags": self.prerequisite_tags,
            "exclusion_tags": self.exclusion_tags,
        }
