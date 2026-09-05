from abc import ABC, abstractmethod
from typing import Dict, Any, List


class LLMProvider(ABC):
    """Abstract interface defining the contract for LLM chat generation providers."""

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Invokes the LLM chat completion API and returns the raw response dictionary."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verifies if the LLM provider service endpoint is online and responsive."""
        pass

    @abstractmethod
    def supported_models(self) -> List[str]:
        """Returns the list of model versions supported by this provider."""
        pass

    @abstractmethod
    def max_context_window(self, model_name: str) -> int:
        """Returns the maximum context window token capacity for a specific model."""
        pass

    @abstractmethod
    def estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """Calculates estimated processing cost in USD."""
        pass
