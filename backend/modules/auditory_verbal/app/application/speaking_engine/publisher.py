from typing import Dict, Any
from app.core.event_bus import event_bus
from app.domain.events.speaking_events import (
    PromptPresented,
    RecordingStarted,
    RecordingPaused,
    RecordingResumed,
    RecordingStopped,
    RecordingDiscarded,
    ResponseCaptured,
    PromptCompleted,
    SpeakingCancelled,
    SpeakingFailed,
)
from app.domain.events.assessment_events import SpeakingStarted, SpeakingCompleted, AudioUploaded


class SpeakingEventPublisher:
    """Helper publishing speaking assessment domain events to the Event Bus."""

    async def publish_started(self, session_id: str, total_prompts: int):
        await event_bus.publish("SpeakingStarted", SpeakingStarted(session_id=session_id, total_prompts=total_prompts))

    async def publish_prompt_presented(self, session_id: str, pid: str, idx: int, total: int):
        await event_bus.publish("PromptPresented", PromptPresented(session_id=session_id, prompt_id=pid, prompt_index=idx, total_prompts=total))

    async def publish_recording_started(self, session_id: str, pid: str, max_sec: float):
        await event_bus.publish("RecordingStarted", RecordingStarted(session_id=session_id, prompt_id=pid, max_seconds=max_sec))

    async def publish_recording_stopped(self, session_id: str, pid: str, duration_sec: float):
        await event_bus.publish("RecordingStopped", RecordingStopped(session_id=session_id, prompt_id=pid, duration_seconds=duration_sec))

    async def publish_response_captured(self, session_id: str, pid: str, audio_url: str, duration_sec: float, meta: Dict[str, Any]):
        await event_bus.publish("ResponseCaptured", ResponseCaptured(session_id=session_id, prompt_id=pid, audio_file_url=audio_url, duration_seconds=duration_sec, metadata=meta))

    async def publish_completed(self, session_id: str, pid: str, audio_url: str):
        await event_bus.publish("SpeakingCompleted", SpeakingCompleted(session_id=session_id, prompt_id=pid, audio_asset_url=audio_url))

    async def publish_cancelled(self, session_id: str, reason: str):
        await event_bus.publish("SpeakingCancelled", SpeakingCancelled(session_id=session_id, reason=reason))

    async def publish_failed(self, session_id: str, reason: str):
        await event_bus.publish("SpeakingFailed", SpeakingFailed(session_id=session_id, reason=reason))
