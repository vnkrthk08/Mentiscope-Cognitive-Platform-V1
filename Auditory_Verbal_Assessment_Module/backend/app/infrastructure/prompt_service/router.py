import os
from typing import Any, List, Optional
from app.infrastructure.prompt_service.provider_interface import ILLMProvider, MockLLMProvider
from app.domain.exceptions.prompt_exceptions import ModelUnavailable
from app.core.logging import logger


class ModelRouter:
    """Selects LLM provider and model based on capability matching, latency tiers, and availability."""

    def __init__(self, providers: Optional[List[ILLMProvider]] = None):
        self.providers: List[ILLMProvider] = providers or [MockLLMProvider()]

    def select_provider_and_model(self, preferred_model: str = "gemini-1.5-pro") -> tuple[Any, str]:
        from app.core.config import settings
        mode = settings.LLM_MODE.lower()
        if mode == "real":
            from app.infrastructure.prompt.provider_registry import llm_registry
            provider_name = settings.LLM_PROVIDER.lower()
            try:
                provider = llm_registry.get_provider(provider_name)
                # Determine target model
                model_name = preferred_model
                if provider_name in ("openrouter", "nvidia"):
                    model_name = settings.OPENROUTER_MODEL
                elif provider_name == "openai":
                    model_name = settings.OPENAI_MODEL
                elif provider_name == "gemini":
                    model_name = settings.GEMINI_MODEL
                elif provider_name == "claude":
                    model_name = settings.CLAUDE_MODEL
                
                logger.info(f"[APOS ROUTER] Selected real provider '{provider_name}' with model '{model_name}' (Reason: Real LLM Mode Configured)")
                return provider, model_name
            except Exception as e:
                logger.error(f"[APOS ROUTER] Failed to get real provider '{provider_name}' from registry: {e}. Aborting.")
                raise ModelUnavailable(preferred_model)

        for p in self.providers:
            if p.health() and preferred_model in p.supported_models():
                logger.info(f"[APOS ROUTER] Selected provider '{p.provider_name}' with model '{preferred_model}' (Reason: Match Preferred Mock Model)")
                return p, preferred_model

        # Fallback to first healthy provider with its first supported model
        for p in self.providers:
            if p.health() and p.supported_models():
                fallback_model = p.supported_models()[0]
                logger.warning(f"[APOS ROUTER] Preferred model '{preferred_model}' unavailable. Falling back to '{p.provider_name}' ({fallback_model})")
                return p, fallback_model

        raise ModelUnavailable(preferred_model)


from typing import Any

