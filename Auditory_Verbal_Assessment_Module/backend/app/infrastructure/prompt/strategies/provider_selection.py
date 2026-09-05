import os
from typing import Tuple
from app.infrastructure.prompt.providers.base_provider import LLMProvider
from app.infrastructure.prompt.provider_registry import llm_registry


class LLMSelectionStrategy:
    """Strategy class resolving the target LLM provider based on operational policies."""

    @staticmethod
    def resolve_provider(policy: str = "DEFAULT", input_tokens: int = 1000) -> Tuple[str, LLMProvider]:
        policy = policy.upper()

        if policy == "LOWEST_COST":
            # Compare cost for standard 1000 input & 500 output tokens
            cheapest_name = "gemini"
            cheapest_cost = float("inf")
            for name in ["openai", "claude", "gemini"]:
                prov = llm_registry.get_provider(name)
                models = prov.supported_models()
                cost = prov.estimate_cost(models[0], input_tokens, 500)
                if cost < cheapest_cost:
                    cheapest_cost = cost
                    cheapest_name = name
            return cheapest_name, llm_registry.get_provider(cheapest_name)

        elif policy == "FASTEST":
            return "openai", llm_registry.get_provider("openai")

        elif policy == "HIGHEST_AVAILABILITY":
            return "openai", llm_registry.get_provider("openai")

        else:
            from app.core.config import settings
            default_name = settings.LLM_PROVIDER.lower()
            return default_name, llm_registry.get_default_provider()
