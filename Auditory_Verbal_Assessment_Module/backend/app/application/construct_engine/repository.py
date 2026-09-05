from typing import Dict, Any, Optional
from app.domain.exceptions.construct_exceptions import ConstructDefinitionMissing


class ConstructRepository:
    """Manages psychometric construct definitions, behavioral indicator catalogs, and evaluation rules."""

    def __init__(self):
        self._construct_definitions: Dict[str, Dict[str, Any]] = {
            "DECISION_MAKING": {
                "name": "Decision Making",
                "description": "Evaluates logical prioritization, risk assessment, and systematic problem solving under pressure.",
                "indicators": ["Emergency Protocol Initiation", "Safety Prioritization", "Risk Mitigation"],
            },
            "COMMUNICATION": {
                "name": "Communication Clarity",
                "description": "Evaluates oral fluency, sequential explanation, and structured argumentation.",
                "indicators": ["Logical Sequencing", "Articulate Response", "Clarity of Expression"],
            },
            "WORKING_MEMORY": {
                "name": "Working Memory Capacity",
                "description": "Evaluates retention and processing of auditory information under temporal constraints.",
                "indicators": ["Detail Retention", "Sequential Recall"],
            },
        }

    def get_construct_definition(self, construct_name: str) -> Dict[str, Any]:
        defn = self._construct_definitions.get(construct_name.upper())
        if not defn:
            # Default fallback for unlisted construct names
            return {
                "name": construct_name,
                "description": f"Psychometric construct evaluation for {construct_name}",
                "indicators": ["Observed behavior"],
            }
        return defn
