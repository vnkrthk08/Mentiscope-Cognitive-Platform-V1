from typing import Any, Dict, Optional
from app.core.logging import logger
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.scenario import Scenario
from app.application.execution_engine.context import ExecutionContext
from app.application.execution_engine.checkpoint_manager import CheckpointManager, ExecutionSnapshot
from app.application.execution_engine.publisher import ExecutionEventPublisher
from app.domain.interfaces.executors import IListeningExecutor, ISpeakingExecutor, IAdaptiveExecutor
from app.domain.exceptions.execution_exceptions import ExecutionFailure


class AssessmentExecutionEngine:
    """Facade for Assessment Execution Engine (AEE).
    Coordinates runtime stage execution received from the Assessment Orchestrator.
    Manages contexts, timers, progress, replays, checkpoints, and publishes execution events.
    Does NOT decide which stage comes next!
    """

    def __init__(
        self,
        checkpoint_manager: Optional[CheckpointManager] = None,
        publisher: Optional[ExecutionEventPublisher] = None,
    ):
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        self.publisher = publisher or ExecutionEventPublisher()
        self._active_contexts: Dict[str, ExecutionContext] = {}

    def create_context(
        self, session: AssessmentSession, scenario: Scenario, stage: str, total_items: int = 1
    ) -> ExecutionContext:
        ctx = ExecutionContext(
            session=session,
            scenario=scenario,
            current_stage=stage,
        )
        ctx.progress_tracker.total_items = max(1, total_items)
        self._active_contexts[session.session_id] = ctx
        return ctx

    async def execute_stage(
        self,
        session: AssessmentSession,
        scenario: Scenario,
        stage: str,
        executor: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Executes assigned assessment stage and reports runtime state back to Orchestrator."""
        logger.info(f"[AEE FACADE] Executing stage '{stage}' for session '{session.session_id}'")
        ctx = self.create_context(session, scenario, stage)

        ctx.fsm.transition_to("RUNNING")
        ctx.timer_manager.start_timer()
        await self.publisher.publish_started(session.session_id, stage)

        # Create initial checkpoint
        snapshot = self.checkpoint_manager.create_checkpoint(
            session_id=session.session_id,
            stage=stage,
            item_index=0,
            fsm_state="RUNNING",
        )
        await self.publisher.publish_checkpoint_created(session.session_id, snapshot.checkpoint_id, stage)

        try:
            # Execute through delegate executor if provided
            result: Dict[str, Any] = {}
            if executor:
                result = await executor.execute(session, scenario)
            else:
                result = {"status": "success", "stage": stage, "items_processed": 1}

            elapsed_sec = ctx.timer_manager.stop_timer() if ctx.timer_manager.start_time else 0.0
            ctx.fsm.transition_to("COMPLETED")
            await self.publisher.publish_completed(session.session_id, stage, elapsed_sec)

            return {
                "status": "COMPLETED",
                "session_id": session.session_id,
                "stage": stage,
                "duration_seconds": elapsed_sec,
                "result": result,
            }
        except Exception as e:
            ctx.fsm.transition_to("FAILED")
            logger.error(f"[AEE FACADE] Execution failed at stage '{stage}': {str(e)}")
            raise ExecutionFailure(stage, str(e))

    async def pause_execution(self, session_id: str, reason: str = "User Paused"):
        ctx = self._active_contexts.get(session_id)
        if ctx:
            ctx.fsm.transition_to("PAUSED")
            ctx.timer_manager.pause_timer()
            await self.publisher.publish_paused(session_id, ctx.current_stage, reason)

    async def resume_execution(self, session_id: str):
        ctx = self._active_contexts.get(session_id)
        if ctx:
            ctx.fsm.transition_to("RUNNING")
            ctx.timer_manager.resume_timer()
            await self.publisher.publish_resumed(session_id, ctx.current_stage)

    def restore_checkpoint(self, session_id: str) -> ExecutionSnapshot:
        return self.checkpoint_manager.restore_checkpoint(session_id)
