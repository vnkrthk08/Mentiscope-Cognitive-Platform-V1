"""
Layer 2: Scenario Skeleton Dataclass (15 Storytelling Dimensions)
Owned by Diversity Subsystem.
"""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass(frozen=True)
class ScenarioSkeleton:
    category: str
    subcategory: str
    scenario_intent: str
    setting: str
    primary_objective: str
    primary_stakeholder: str
    secondary_stakeholder: str
    trigger_event: str
    operational_constraint: str
    available_resources: List[str]
    missing_resources: List[str]
    time_pressure: str
    success_condition: str
    failure_risk: str
    expected_decision_type: str
    social_dynamics: str
    escalation_event: str
    reflection_theme: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "subcategory": self.subcategory,
            "scenario_intent": self.scenario_intent,
            "setting": self.setting,
            "primary_objective": self.primary_objective,
            "primary_stakeholder": self.primary_stakeholder,
            "secondary_stakeholder": self.secondary_stakeholder,
            "trigger_event": self.trigger_event,
            "operational_constraint": self.operational_constraint,
            "available_resources": self.available_resources,
            "missing_resources": self.missing_resources,
            "time_pressure": self.time_pressure,
            "success_condition": self.success_condition,
            "failure_risk": self.failure_risk,
            "expected_decision_type": self.expected_decision_type,
            "social_dynamics": self.social_dynamics,
            "escalation_event": self.escalation_event,
            "reflection_theme": self.reflection_theme,
        }
