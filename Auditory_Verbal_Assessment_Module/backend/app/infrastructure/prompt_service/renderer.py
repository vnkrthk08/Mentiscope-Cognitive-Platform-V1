from typing import Dict, Any
from app.infrastructure.prompt_service.template import PromptTemplate
from app.domain.exceptions.prompt_exceptions import TemplateRenderingFailure


class PromptRenderer:
    """Renders prompt templates by safely performing variable substitution."""

    def render(self, template: PromptTemplate, variables: Dict[str, Any]) -> str:
        try:
            rendered_text = template.template_text.format(**variables)
            return rendered_text
        except KeyError as e:
            raise TemplateRenderingFailure(template.prompt_id, f"Missing variable key: {str(e)}")
        except Exception as e:
            raise TemplateRenderingFailure(template.prompt_id, str(e))
