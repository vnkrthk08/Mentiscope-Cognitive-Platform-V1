from dataclasses import dataclass, field
from typing import Dict, List, Any
from app.domain.value_objects.enums import ConstructType, DifficultyLevel


@dataclass
class ScenarioBlueprint:
    """Domain representation of a planned scenario blueprint."""

    scenario_number: int
    domain: str
    difficulty: DifficultyLevel
    listening_difficulty: DifficultyLevel
    speaking_focus: str
    primary_constructs: List[ConstructType]
    secondary_constructs: List[ConstructType]
    narration_length_min: int
    narration_length_max: int
    expected_speaking_duration_seconds: int
    language_level: str
    diversity_constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssessmentMasterBlueprint:
    """Domain model representing the master plan for the entire assessment session."""

    assessment_id: str
    assessment_policy_version: str
    total_scenario_count: int
    overall_construct_coverage_plan: List[str]
    overall_difficulty_progression: List[DifficultyLevel]
    overall_domain_diversity_strategy: List[str]
    scenario_blueprints: List[ScenarioBlueprint] = field(default_factory=list)
