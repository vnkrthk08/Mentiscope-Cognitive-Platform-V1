from app.core.event_bus import event_bus
from app.domain.events.evidence_events import (
    EvidenceExtractionStarted,
    TranscriptLoaded,
    PromptRequested,
    EvidenceValidated,
    EvidenceStored,
    EvidenceExtractionCompleted,
    EvidenceExtractionFailed,
)


class EvidenceEventPublisher:
    """Helper publishing behavioral evidence extraction events to the Event Bus."""

    async def publish_started(self, session_id: str, scenario_id: str):
        await event_bus.publish("EvidenceExtractionStarted", EvidenceExtractionStarted(session_id=session_id, scenario_id=scenario_id))

    async def publish_transcript_loaded(self, session_id: str, text_len: int):
        await event_bus.publish("TranscriptLoaded", TranscriptLoaded(session_id=session_id, transcript_text_len=text_len))

    async def publish_prompt_requested(self, session_id: str, prompt_id: str):
        await event_bus.publish("PromptRequested", PromptRequested(session_id=session_id, prompt_id=prompt_id))

    async def publish_evidence_validated(self, session_id: str, count: int):
        await event_bus.publish("EvidenceValidated", EvidenceValidated(session_id=session_id, evidence_count=count))

    async def publish_evidence_stored(self, session_id: str, set_id: str):
        await event_bus.publish("EvidenceStored", EvidenceStored(session_id=session_id, evidence_set_id=set_id))

    async def publish_completed(self, session_id: str, count: int, confidence: float):
        await event_bus.publish("EvidenceExtractionCompleted", EvidenceExtractionCompleted(session_id=session_id, evidence_count=count, overall_confidence=confidence))

    async def publish_failed(self, session_id: str, reason: str):
        await event_bus.publish("EvidenceExtractionFailed", EvidenceExtractionFailed(session_id=session_id, reason=reason))
