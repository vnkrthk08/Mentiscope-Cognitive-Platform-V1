from typing import List, Dict, Any, Tuple


class ConstructMappingEngine:
    """Maps behavior observation categories to psychometric constructs across standard frameworks."""

    # Category -> list of (framework, construct_name, mapping_strength)
    MAPPING_RULES = {
        "leadership": [
            ("PERSONALITY", "Leadership", 1.0),
            ("RIASEC", "Enterprising", 0.75),
        ],
        "communication": [
            ("PERSONALITY", "Team Orientation", 0.8),
            ("EMOTIONAL_REGULATION", "Self-Regulation", 0.65),
        ],
        "problem solving": [
            ("CHC", "Fluid Intelligence (Gf)", 0.95),
            ("RIASEC", "Investigative", 0.85),
        ],
        "adaptability": [
            ("PERSONALITY", "Adaptability", 1.0),
            ("EMOTIONAL_REGULATION", "Resilience", 0.8),
        ],
        "persistence": [
            ("PERSONALITY", "Persistence", 1.0),
            ("EMOTIONAL_REGULATION", "Self-Regulation", 0.7),
        ],
        "attention to detail": [
            ("CHC", "Processing Speed (Gs)", 0.90),
            ("PERSONALITY", "Attention to Detail", 0.85),
        ],
        "sequential memory": [
            ("CHC", "Short-Term Memory (Gsm)", 0.95),
            ("PERSONALITY", "Sequential Memory", 0.85),
        ],
        "listening accuracy": [
            ("CHC", "Auditory Processing (Ga)", 0.95),
            ("PERSONALITY", "Listening Accuracy", 0.85),
        ],
    }

    @classmethod
    def get_mappings(cls, behavior_type: str) -> List[Tuple[str, str, float]]:
        """Resolves target framework mappings for a given behavior type category."""
        return cls.MAPPING_RULES.get(behavior_type.lower(), [("PERSONALITY", behavior_type.title(), 0.5)])
pre=1.0
