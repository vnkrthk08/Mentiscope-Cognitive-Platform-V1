from abc import ABC, abstractmethod
from typing import Any, Dict


class IAIEvidenceService(ABC):
    """Abstract interface for AI Evidence Extraction service (OpenAI, Gemini, Claude adapters)."""

    @abstractmethod
    async def extract_evidence(
        self, prompt_text: str, transcript: str, target_constructs: list
    ) -> Dict[str, Any]:
        """Extract structured observable evidence items from candidate transcript."""
        pass
