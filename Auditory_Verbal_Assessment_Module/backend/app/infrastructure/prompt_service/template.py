from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class PromptTemplate:
    """Dataclass encapsulating prompt template text, variables, output schema, and version."""

    prompt_id: str
    version: str
    description: str
    prompt_type: str
    template_text: str
    required_variables: List[str]
    output_schema: Dict[str, Any]
    supported_models: List[str] = field(default_factory=lambda: ["gemini-1.5-pro", "gpt-4o"])
    tags: List[str] = field(default_factory=list)
    research_metadata: Dict[str, Any] = field(default_factory=dict)
