from app.core.event_bus import event_bus
from app.domain.events.execution_events import (
    ExecutionStarted,
    ExecutionPaused,
    ExecutionResumed,
    ExecutionTimedOut,
    ExecutionCancelled,
    QuestionStarted,
    QuestionCompleted,
    PromptStarted,
    PromptCompleted,
    ReplayUsed,
    CheckpointCreated,
    ExecutionCompleted,
)


class ExecutionEventPublisher:
    """Helper publishing runtime execution events to the central Domain Event Bus."""

    async def publish_started(self, session_id: str, stage: str):
        await event_bus.publish("ExecutionStarted", ExecutionStarted(session_id=session_id, stage=stage))

    async def publish_paused(self, session_id: str, stage: str, reason: str):
        await event_bus.publish("ExecutionPaused", ExecutionPaused(session_id=session_id, stage=stage, reason=reason))

    async def publish_resumed(self, session_id: str, stage: str):
        await event_bus.publish("ExecutionResumed", ExecutionResumed(session_id=session_id, stage=stage))

    async def publish_timed_out(self, session_id: str, item_id: str, elapsed_seconds: float):
        await event_bus.publish("ExecutionTimedOut", ExecutionTimedOut(session_id=session_id, item_id=item_id, elapsed_seconds=elapsed_seconds))

    async def publish_cancelled(self, session_id: str, reason: str):
        await event_bus.publish("ExecutionCancelled", ExecutionCancelled(session_id=session_id, reason=reason))

    async def publish_question_started(self, session_id: str, question_id: str, index: int):
        await event_bus.publish("QuestionStarted", QuestionStarted(session_id=session_id, question_id=question_id, question_index=index))

    async def publish_question_completed(self, session_id: str, question_id: str, selected_option: int, response_time_ms: int):
        await event_bus.publish("QuestionCompleted", QuestionCompleted(session_id=session_id, question_id=question_id, selected_option_index=selected_option, response_time_ms=response_time_ms))

    async def publish_prompt_started(self, session_id: str, prompt_id: str, index: int):
        await event_bus.publish("PromptStarted", PromptStarted(session_id=session_id, prompt_id=prompt_id, prompt_index=index))

    async def publish_prompt_completed(self, session_id: str, prompt_id: str, audio_url: str, duration_sec: float):
        await event_bus.publish("PromptCompleted", PromptCompleted(session_id=session_id, prompt_id=prompt_id, audio_file_url=audio_url, duration_seconds=duration_sec))

    async def publish_replay_used(self, session_id: str, item_id: str, replay_num: int, max_replays: int):
        await event_bus.publish("ReplayUsed", ReplayUsed(session_id=session_id, item_id=item_id, replay_number=replay_num, max_replays=max_replays))

    async def publish_checkpoint_created(self, session_id: str, checkpoint_id: str, stage: str):
        await event_bus.publish("CheckpointCreated", CheckpointCreated(session_id=session_id, checkpoint_id=checkpoint_id, stage=stage))

    async def publish_completed(self, session_id: str, stage: str, duration_sec: float):
        await event_bus.publish("ExecutionCompleted", ExecutionCompleted(session_id=session_id, stage=stage, duration_seconds=duration_sec))
