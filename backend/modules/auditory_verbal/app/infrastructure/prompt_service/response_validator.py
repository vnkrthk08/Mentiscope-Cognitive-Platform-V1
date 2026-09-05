import json
from typing import Dict, Any
from app.infrastructure.prompt_service.template import PromptTemplate
from app.domain.exceptions.prompt_exceptions import ResponseValidationFailure
from app.infrastructure.prompt_service.pydantic_schemas import (
    AdaptiveFollowupResponse,
    EvidenceExtractionResponse,
    ConstructEvaluationResponse,
    ScenarioGenerationResponse,
)


class ResponseValidator:
    """Validates raw LLM outputs against JSON schema structure and required fields."""

    def validate_pydantic(self, prompt_id: str, raw_content: str) -> Dict[str, Any]:
        """Validates raw output against the Pydantic model for the corresponding prompt_id."""
        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError as e:
            raise ResponseValidationFailure(prompt_id, f"Output is not valid JSON: {str(e)}")

        model_map = {
            "ADAPTIVE_FOLLOWUP_PROMPT": AdaptiveFollowupResponse,
            "EVIDENCE_EXTRACTION_PROMPT": EvidenceExtractionResponse,
            "CONSTRUCT_EVALUATION_PROMPT": ConstructEvaluationResponse,
            "SCENARIO_GENERATION_PROMPT": ScenarioGenerationResponse,
        }

        model = model_map.get(prompt_id)
        if not model:
            # Fallback if no matching pydantic model
            return parsed

        try:
            validated = model.model_validate(parsed)
            return validated.model_dump()
        except Exception as e:
            raise ResponseValidationFailure(prompt_id, f"Pydantic validation failed: {str(e)}")

    def validate_response(self, template: PromptTemplate, raw_content: str) -> Dict[str, Any]:
        # Support running both: if LLM_MODE is real, validate using Pydantic, else check schema keys
        from app.core.config import settings
        if settings.LLM_MODE.lower() == "real":
            return self.validate_pydantic(template.prompt_id, raw_content)

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError as e:
            raise ResponseValidationFailure(template.prompt_id, f"Output is not valid JSON: {str(e)}")

        schema = template.output_schema
        required_keys = schema.get("required", [])

        missing_keys = [k for k in required_keys if k not in parsed]
        if missing_keys:
            raise ResponseValidationFailure(
                template.prompt_id, f"JSON output missing required schema fields: {', '.join(missing_keys)}"
            )

        return parsed

