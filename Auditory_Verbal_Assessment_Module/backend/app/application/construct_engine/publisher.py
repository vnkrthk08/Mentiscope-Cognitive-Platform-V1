from app.core.event_bus import event_bus
from app.domain.events.construct_events import (
    ConstructEvaluationStarted,
    EvidenceLoaded,
    EvaluationPromptRequested,
    EvaluationPromptCompleted,
    ConstructValidated,
    EvaluationStored,
    ConstructEvaluationCompleted,
    ConstructEvaluationFailed,
)


class ConstructEventPublisher:
    """Helper publishing psychometric construct evaluation events to the Event Bus."""

    async def publish_started(self, session_id: str, scenario_id: str):
        await event_bus.publish("ConstructEvaluationStarted", ConstructEvaluationStarted(session_id=session_id, scenario_id=scenario_id))

    async def publish_evidence_loaded(self, session_id: str, count: int):
        await event_bus.publish("EvidenceLoaded", EvidenceLoaded(session_id=session_id, evidence_count=count))

    async def publish_prompt_requested(self, session_id: str, prompt_id: str):
        await event_bus.publish("EvaluationPromptRequested", EvaluationPromptRequested(session_id=session_id, prompt_id=prompt_id))

    async def publish_prompt_completed(self, session_id: str, prompt_id: str, latency_ms: int):
        await event_bus.publish("EvaluationPromptCompleted", EvaluationPromptCompleted(session_id=session_id, prompt_id=prompt_id, latency_ms=latency_ms))

    async def publish_validated(self, session_id: str, count: int):
        await event_bus.publish("ConstructValidated", ConstructValidated(session_id=session_id, construct_count=count))

    async def publish_stored(self, session_id: str, set_id: str):
        await event_bus.publish("EvaluationStored", EvaluationStored(session_id=session_id, evaluation_set_id=set_id))

    async def publish_completed(self, session_id: str, count: int, confidence: float):
        await event_bus.publish("ConstructEvaluationCompleted", ConstructEvaluationCompleted(session_id=session_id, evaluations_count=count, overall_confidence=confidence))

    async def publish_failed(self, session_id: str, reason: str):
        await event_bus.publish("ConstructEvaluationFailed", ConstructEvaluationFailed(session_id=session_id, reason=reason))
