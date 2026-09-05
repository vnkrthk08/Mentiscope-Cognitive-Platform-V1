class PromptEngineException(Exception):
    """Base exception for AI Prompt Orchestration Service errors."""

    pass


class PromptNotFound(PromptEngineException):
    def __init__(self, prompt_id: str, version: str = "latest"):
        super().__init__(f"Prompt template '{prompt_id}' (version '{version}') not found in repository.")


class PromptValidationFailure(PromptEngineException):
    def __init__(self, prompt_id: str, reason: str):
        super().__init__(f"Prompt template '{prompt_id}' validation failed: {reason}")


class TemplateRenderingFailure(PromptEngineException):
    def __init__(self, prompt_id: str, reason: str):
        super().__init__(f"Failed to render prompt template '{prompt_id}': {reason}")


class MissingVariable(PromptEngineException):
    def __init__(self, prompt_id: str, missing_vars: list):
        super().__init__(f"Missing required variables for prompt '{prompt_id}': {', '.join(missing_vars)}")


class SchemaValidationFailure(PromptEngineException):
    def __init__(self, schema_id: str, reason: str):
        super().__init__(f"Output schema validation error for '{schema_id}': {reason}")


class ModelUnavailable(PromptEngineException):
    def __init__(self, model_name: str):
        super().__init__(f"LLM Model or Provider for '{model_name}' is currently unavailable.")


class GenerationFailure(PromptEngineException):
    def __init__(self, provider_name: str, reason: str):
        super().__init__(f"LLM generation failed on provider '{provider_name}': {reason}")


class ResponseValidationFailure(PromptEngineException):
    def __init__(self, prompt_id: str, reason: str):
        super().__init__(f"LLM output response validation failed for prompt '{prompt_id}': {reason}")


class PromptOrchestrationFailure(PromptEngineException):
    def __init__(self, prompt_id: str, reason: str):
        super().__init__(f"Prompt orchestration pipeline failed for '{prompt_id}': {reason}")
