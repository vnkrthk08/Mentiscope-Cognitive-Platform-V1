from dataclasses import dataclass, field
from typing import List
from app.domain.value_objects.enums import PromptType, ProviderType
from app.domain.value_objects.scenario_version import ScenarioVersion


@dataclass
class PromptTemplate:
    """Entity representing versioned AI Prompt templates."""

    prompt_key: str
    prompt_type: PromptType
    template_text: str
    variables: List[str]
    version: ScenarioVersion
    provider_compatibility: List[ProviderType]

    def __post_init__(self):
        if not self.prompt_key or not self.prompt_key.strip():
            raise ValueError("PromptTemplate prompt_key cannot be empty.")
        if not self.template_text or not self.template_text.strip():
            raise ValueError("PromptTemplate template_text cannot be empty.")
        if not self.provider_compatibility:
            raise ValueError("PromptTemplate must specify at least one compatible provider.")
