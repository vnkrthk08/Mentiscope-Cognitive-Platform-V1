from dataclasses import dataclass, field
from typing import List


@dataclass
class PromptTemplate:
    """Domain Entity representing a versioned context template for LLM prompts."""

    template_id: str
    name: str
    template_text: str
    version: str
    required_variables: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.template_id or not self.template_id.strip():
            raise ValueError("PromptTemplate template_id cannot be empty.")
        if not self.name or not self.name.strip():
            raise ValueError("PromptTemplate name cannot be empty.")
        if not self.template_text or not self.template_text.strip():
            raise ValueError("PromptTemplate template_text cannot be empty.")

    def validate_inputs(self, variables: dict) -> None:
        """Verifies if all necessary substitution keys are supplied."""
        missing = [v for v in self.required_variables if v not in variables]
        if missing:
            raise ValueError(f"Missing required template substitution variables: {', '.join(missing)}")
