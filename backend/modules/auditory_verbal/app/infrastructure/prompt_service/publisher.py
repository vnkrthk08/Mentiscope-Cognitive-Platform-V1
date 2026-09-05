from app.core.event_bus import event_bus
from app.domain.events.prompt_events import (
    PromptLoaded,
    PromptRendered,
    PromptValidated,
    ModelSelected,
    GenerationStarted,
    GenerationCompleted,
    ValidationSucceeded,
    ValidationFailed,
    PromptCompleted,
    PromptFailed,
)


class PromptEventPublisher:
    """Helper publishing prompt domain events to the Event Bus."""

    async def publish_loaded(self, prompt_id: str, version: str):
        await event_bus.publish("PromptLoaded", PromptLoaded(prompt_id=prompt_id, version=version))

    async def publish_rendered(self, prompt_id: str, rendered_hash: str, char_count: int):
        await event_bus.publish("PromptRendered", PromptRendered(prompt_id=prompt_id, rendered_hash=rendered_hash, char_count=char_count))

    async def publish_validated(self, prompt_id: str, status: str):
        await event_bus.publish("PromptValidated", PromptValidated(prompt_id=prompt_id, status=status))

    async def publish_model_selected(self, prompt_id: str, provider_name: str, model_name: str):
        await event_bus.publish("ModelSelected", ModelSelected(prompt_id=prompt_id, provider_name=provider_name, model_name=model_name))

    async def publish_generation_started(self, prompt_id: str, model_name: str):
        await event_bus.publish("GenerationStarted", GenerationStarted(prompt_id=prompt_id, model_name=model_name))

    async def publish_generation_completed(self, prompt_id: str, model_name: str, latency_ms: int):
        await event_bus.publish("GenerationCompleted", GenerationCompleted(prompt_id=prompt_id, model_name=model_name, latency_ms=latency_ms))

    async def publish_validation_succeeded(self, prompt_id: str, schema_version: str):
        await event_bus.publish("ValidationSucceeded", ValidationSucceeded(prompt_id=prompt_id, schema_version=schema_version))

    async def publish_validation_failed(self, prompt_id: str, reason: str):
        await event_bus.publish("ValidationFailed", ValidationFailed(prompt_id=prompt_id, reason=reason))

    async def publish_completed(self, prompt_id: str, latency_ms: int):
        await event_bus.publish("PromptCompleted", PromptCompleted(prompt_id=prompt_id, latency_ms=latency_ms))

    async def publish_failed(self, prompt_id: str, reason: str):
        await event_bus.publish("PromptFailed", PromptFailed(prompt_id=prompt_id, reason=reason))
