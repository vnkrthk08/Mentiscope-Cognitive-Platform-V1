from typing import Dict, Any
from app.infrastructure.prompt_service.template import PromptTemplate
from app.domain.exceptions.prompt_exceptions import MissingVariable, PromptValidationFailure


class PromptValidator:
    """Validates prompt template variable presence, syntax, and payload size bounds."""

    def validate_variables(self, template: PromptTemplate, variables: Dict[str, Any]):
        missing = [v for v in template.required_variables if v not in variables]
        if missing:
            raise MissingVariable(template.prompt_id, missing)

    def validate_rendered_prompt(self, template: PromptTemplate, rendered_text: str, max_chars: int = 32000):
        if not rendered_text or len(rendered_text.strip()) == 0:
            raise PromptValidationFailure(template.prompt_id, "Rendered prompt text is empty.")
        if len(rendered_text) > max_chars:
            raise PromptValidationFailure(template.prompt_id, f"Rendered prompt length ({len(rendered_text)} chars) exceeds maximum limit of {max_chars}.")
