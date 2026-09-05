from typing import Dict, Any, Optional
from app.infrastructure.prompt_service import AIPromptOrchestrationService, PromptOrchestrationResult
from app.domain.exceptions.evidence_exceptions import PromptExecutionFailure
from app.core.logging import logger


class EvidencePromptCoordinator:
    """Coordinates prompt requests exclusively through AI Prompt Orchestration Service (APOS)."""

    def __init__(self, apos: Optional[AIPromptOrchestrationService] = None):
        self.apos = apos or AIPromptOrchestrationService()

    async def extract_evidence_via_apos(
        self,
        variables: Dict[str, Any],
        prompt_id: str = "EVIDENCE_EXTRACTION_PROMPT",
        version: str = "1.0.0",
    ) -> PromptOrchestrationResult:
        logger.info(f"[BEEE COORDINATOR] Requesting APOS prompt '{prompt_id}' (v{version})")
        try:
            result = await self.apos.execute_prompt(prompt_id=prompt_id, variables=variables, version=version)
            return result
        except Exception as e:
            raise PromptExecutionFailure(prompt_id, str(e))
