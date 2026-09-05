"""
Layer 1: Assessment Skeleton Dataclass (Immutable Psychometric Specification)
Owned by AssessmentPlanningEngine.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from app.domain.entities.assessment_blueprint import ScenarioBlueprint


@dataclass(frozen=True)
class AssessmentSkeleton:
    primary_constructs: List[str]
    secondary_constructs: List[str]
    difficulty: str
    listening_difficulty: str
    speaking_difficulty: str
    cognitive_load: int
    target_decision_type: str
    edapaf_mapping: Dict[str, str]
    assessment_objective: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_constructs": self.primary_constructs,
            "secondary_constructs": self.secondary_constructs,
            "difficulty": self.difficulty,
            "listening_difficulty": self.listening_difficulty,
            "speaking_difficulty": self.speaking_difficulty,
            "cognitive_load": self.cognitive_load,
            "target_decision_type": self.target_decision_type,
            "edapaf_mapping": self.edapaf_mapping,
            "assessment_objective": self.assessment_objective,
        }

    @classmethod
    def from_blueprint(cls, blueprint: ScenarioBlueprint) -> "AssessmentSkeleton":
        primary = [c.value for c in blueprint.primary_constructs]
        secondary = [c.value for c in blueprint.secondary_constructs]

        # Determine decision type based on primary constructs
        if "DECISION_MAKING" in primary or "REASONING" in primary:
            dec_type = "Resource Allocation & Trade-off Selection"
        elif "COMMUNICATION" in primary or "LISTENING_ABILITY" in primary:
            dec_type = "Stakeholder Alignment & Positioning"
        elif "ETHICAL_REASONING" in primary:
            dec_type = "Ethical Protocol Adherence"
        else:
            dec_type = "Adaptive Problem Diagnosis & Action"

        edapaf_map = {
            "stage_1": "Initial Strategy & Decision Formulation",
            "stage_2": "Adaptive Challenge & Constraint Navigation",
            "stage_3": "Metacognitive Reflection & Rationale Defense",
        }

        obj = f"Evaluate {', '.join(primary)} at {blueprint.difficulty.value} difficulty under structured EDAPAF constraints."

        return cls(
            primary_constructs=primary,
            secondary_constructs=secondary,
            difficulty=blueprint.difficulty.value,
            listening_difficulty=blueprint.listening_difficulty.value,
            speaking_difficulty=blueprint.difficulty.value,
            cognitive_load=getattr(blueprint, "cognitive_load", 3),
            target_decision_type=dec_type,
            edapaf_mapping=edapaf_map,
            assessment_objective=obj,
        )
