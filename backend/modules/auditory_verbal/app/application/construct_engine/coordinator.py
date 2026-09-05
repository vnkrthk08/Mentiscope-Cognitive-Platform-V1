from typing import Dict, Any, Optional
from app.infrastructure.prompt_service import AIPromptOrchestrationService, PromptOrchestrationResult
from app.domain.exceptions.construct_exceptions import EvaluationPromptFailure
from app.core.logging import logger


class ConstructEvaluationCoordinator:
    """Coordinates psychometric evaluation prompt execution exclusively through APOS Gateway."""

    def __init__(self, apos: Optional[AIPromptOrchestrationService] = None):
        self.apos = apos or AIPromptOrchestrationService()

    async def evaluate_construct_via_apos(
        self,
        variables: Dict[str, Any],
        prompt_id: str = "CONSTRUCT_EVALUATION_PROMPT",
        version: str = "1.0.0",
    ) -> PromptOrchestrationResult:
        logger.info(f"[PCEE COORDINATOR] Requesting APOS evaluation prompt '{prompt_id}' (v{version})")
        try:
            result = await self.apos.execute_prompt(prompt_id=prompt_id, variables=variables, version=version)
            return result
        except Exception as e:
            raise EvaluationPromptFailure(prompt_id, str(e))
