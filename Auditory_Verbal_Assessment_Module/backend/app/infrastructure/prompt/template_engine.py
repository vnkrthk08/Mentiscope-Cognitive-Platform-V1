import re
from typing import Dict, Any, List
from app.domain.prompt.entities.prompt_template import PromptTemplate


class PromptTemplateEngine:
    """Orchestrates string substitution, verification, and variable binding for templates."""

    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}
        # Pre-seed default template for Auditory Processing analysis
        default_text = (
            "Analyze the following transcript for candidate {candidate_id} in assessment {assessment_id}.\n"
            "Scenario context: {scenario_text}\n"
            "Transcript text:\n{transcript_text}\n"
            "Extract structured behavior evidence indicators (Leadership, Communication, Problem Solving, initiative)."
        )
        self.register(
            PromptTemplate(
                template_id="default-assessment-template",
                name="Auditory Assessment template",
                template_text=default_text,
                version="1.0.0",
                required_variables=["candidate_id", "assessment_id", "scenario_text", "transcript_text"],
            )
        )

    def register(self, template: PromptTemplate) -> None:
        self._templates[template.template_id] = template

    def get_template(self, template_id: str) -> PromptTemplate:
        tpl = self._templates.get(template_id)
        if not tpl:
            raise ValueError(f"PromptTemplate with id '{template_id}' is not registered.")
        return tpl

    def render(self, template_id: str, variables: Dict[str, Any]) -> str:
        tpl = self.get_template(template_id)
        tpl.validate_inputs(variables)

        rendered = tpl.template_text
        for key, val in variables.items():
            rendered = rendered.replace(f"{{{key}}}", str(val))
        return rendered

    def list_templates(self) -> List[PromptTemplate]:
        return list(self._templates.values())


# Global template engine
template_engine = PromptTemplateEngine()
