from dataclasses import dataclass, field
from typing import Dict, List, Any
from app.domain.value_objects.enums import DifficultyLevel


@dataclass
class AssessmentPlanningPolicy:
    """Domain representation of the psychometric assessment sequencing and planning rules."""

    assessment_size: int = 5
    allowed_domains: List[str] = field(default_factory=lambda: [
        "School Science Exhibition",
        "Group Classroom Project",
        "School Sports Day",
        "Cultural Festival",
        "Community Service Drive"
    ])
    construct_coverage_strategy: Dict[str, Any] = field(default_factory=lambda: {
        "sequence": [
            {
                "speaking_focus": "DECISION_MAKING",
                "primary": ["COMMUNICATION", "DECISION_MAKING"],
                "secondary": ["REASONING"]
            },
            {
                "speaking_focus": "LEADERSHIP",
                "primary": ["COMMUNICATION", "RESPONSIBILITY"],
                "secondary": ["ADAPTABILITY"]
            },
            {
                "speaking_focus": "ADAPTABILITY",
                "primary": ["ADAPTABILITY", "DECISION_MAKING"],
                "secondary": ["CONFIDENCE"]
            },
            {
                "speaking_focus": "ETHICAL_REASONING",
                "primary": ["ETHICAL_REASONING", "RESPONSIBILITY"],
                "secondary": ["REASONING"]
            },
            {
                "speaking_focus": "REASONING",
                "primary": ["REASONING", "COMMUNICATION"],
                "secondary": ["WORKING_MEMORY"]
            }
        ]
    })
    difficulty_progression: List[DifficultyLevel] = field(default_factory=lambda: [
        DifficultyLevel.BEGINNER,       # Scenario 1: Easy
        DifficultyLevel.INTERMEDIATE,   # Scenario 2: Medium
        DifficultyLevel.INTERMEDIATE,   # Scenario 3: Medium
        DifficultyLevel.ADVANCED,       # Scenario 4: Hard
        DifficultyLevel.ADVANCED        # Scenario 5: Hard
    ])
    narration_length_ranges: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        "BEGINNER": {"min": 100, "max": 130},
        "INTERMEDIATE": {"min": 120, "max": 160},
        "ADVANCED": {"min": 150, "max": 200}
    })
    language_level: str = "Class 10-11 student"
    speaking_duration: int = 120
    scenario_sequencing_rules: Dict[str, Any] = field(default_factory=dict)
