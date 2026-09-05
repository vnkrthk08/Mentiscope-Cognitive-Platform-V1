from app.core.event_bus import event_bus
from app.domain.events.speech_events import (
    SpeechProcessingStarted,
    AudioValidated,
    AudioPreprocessed,
    ProviderSelected,
    TranscriptionStarted,
    TranscriptionCompleted,
    RetryAttempted,
    ProcessingCompleted,
    ProcessingFailed,
)


class SpeechProcessingEventPublisher:
    """Helper publishing speech processing domain events to the Event Bus."""

    async def publish_started(self, session_id: str, prompt_id: str, audio_url: str):
        await event_bus.publish("SpeechProcessingStarted", SpeechProcessingStarted(session_id=session_id, prompt_id=prompt_id, audio_url=audio_url))

    async def publish_audio_validated(self, session_id: str, audio_url: str, duration_sec: float):
        await event_bus.publish("AudioValidated", AudioValidated(session_id=session_id, audio_url=audio_url, duration_seconds=duration_sec))

    async def publish_audio_preprocessed(self, session_id: str, audio_url: str, sample_rate: int, channels: int):
        await event_bus.publish("AudioPreprocessed", AudioPreprocessed(session_id=session_id, audio_url=audio_url, sample_rate=sample_rate, channels=channels))

    async def publish_provider_selected(self, session_id: str, provider_name: str):
        await event_bus.publish("ProviderSelected", ProviderSelected(session_id=session_id, provider_name=provider_name))

    async def publish_transcription_started(self, session_id: str, provider_name: str):
        await event_bus.publish("TranscriptionStarted", TranscriptionStarted(session_id=session_id, provider_name=provider_name))

    async def publish_transcription_completed(self, session_id: str, provider_name: str, confidence: float, text_length: int):
        await event_bus.publish("TranscriptionCompleted", TranscriptionCompleted(session_id=session_id, provider_name=provider_name, confidence=confidence, text_length=text_length))

    async def publish_retry_attempted(self, session_id: str, provider_name: str, attempt: int, reason: str):
        await event_bus.publish("RetryAttempted", RetryAttempted(session_id=session_id, provider_name=provider_name, attempt=attempt, reason=reason))

    async def publish_completed(self, session_id: str, prompt_id: str, confidence: float, duration_sec: float):
        await event_bus.publish("ProcessingCompleted", ProcessingCompleted(session_id=session_id, prompt_id=prompt_id, overall_confidence=confidence, duration_seconds=duration_sec))

    async def publish_failed(self, session_id: str, reason: str):
        await event_bus.publish("ProcessingFailed", ProcessingFailed(session_id=session_id, reason=reason))
