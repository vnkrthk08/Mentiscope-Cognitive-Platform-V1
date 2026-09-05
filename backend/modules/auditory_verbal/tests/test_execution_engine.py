import pytest
from app.application.execution_engine import (
    AssessmentExecutionEngine,
    ExecutionStateMachine,
    TimerManager,
    ReplayManager,
    ProgressTracker,
    CheckpointManager,
)
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.scenario import Scenario
from app.domain.value_objects.audio_asset import AudioAsset
from app.domain.value_objects.scenario_version import ScenarioVersion
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.value_objects.time_limit import TimeLimit
from app.domain.value_objects.enums import ConstructType
from app.domain.exceptions.execution_exceptions import (
    InvalidExecutionState,
    ReplayLimitExceeded,
    ExecutionTimeout,
    CheckpointFailure,
    ExecutionFailure,
)


def _create_test_session_and_scenario():
    session = AssessmentSession(
        session_id="SESS-EXEC-001",
        candidate_id="CAND-EXEC-001",
        scenario_id="SCENARIO_LOGISTICS_01",
    )
    audio = AudioAsset(url="/audio/test.mp3", duration_seconds=120)
    version = ScenarioVersion("1.0.0")
    q = ListeningQuestion(
        question_id="Q1",
        prompt="What happened?",
        options=["A", "B"],
        correct_option_index=0,
        target_construct=ConstructType.ATTENTION,
    )
    p = SpeakingPrompt(
        prompt_id="P1",
        title="Briefing",
        instructions="Explain decision",
        time_limit=TimeLimit(max_seconds=120),
        target_constructs=[ConstructType.COMMUNICATION],
    )
    scenario = Scenario(
        scenario_id="SCENARIO_LOGISTICS_01",
        title="Logistics Crisis",
        narrative="Supply chain issue",
        audio_asset=audio,
        listening_questions=[q],
        speaking_prompts=[p],
        version=version,
    )
    return session, scenario


def test_execution_state_machine():
    fsm = ExecutionStateMachine("READY")
    assert fsm.current_state == "READY"

    fsm.transition_to("RUNNING")
    assert fsm.current_state == "RUNNING"

    fsm.transition_to("WAITING_FOR_RESPONSE")
    assert fsm.current_state == "WAITING_FOR_RESPONSE"

    with pytest.raises(InvalidExecutionState):
        fsm.transition_to("READY")  # Invalid backwards transition


def test_timer_manager_execution_and_timeout():
    timer = TimerManager(max_seconds=10.0, grace_period_seconds=2.0)
    timer.start_timer()
    assert timer.is_running is True

    elapsed = timer.get_elapsed_seconds()
    assert elapsed >= 0.0
    assert timer.get_remaining_seconds() > 0.0

    # Test timeout assertion with artificial elapsed time check
    timer.max_seconds = 0.001
    timer.grace_period_seconds = 0.0
    import time
    time.sleep(0.01)

    with pytest.raises(ExecutionTimeout):
        timer.check_timeout("Q1")


def test_replay_manager_limits():
    rm = ReplayManager()
    assert rm.get_replay_count("Q1") == 0
    assert rm.get_remaining_replays("Q1", max_replays=2) == 2

    rm.record_replay("Q1", max_replays=2)
    rm.record_replay("Q1", max_replays=2)
    assert rm.get_replay_count("Q1") == 2

    with pytest.raises(ReplayLimitExceeded):
        rm.record_replay("Q1", max_replays=2)


def test_progress_tracker():
    tracker = ProgressTracker(total_items=4)
    assert tracker.get_completion_percentage() == 0.0
    assert tracker.get_remaining_items_count() == 4

    tracker.mark_answered("Q1")
    tracker.mark_answered("Q2")
    assert tracker.get_completion_percentage() == 50.0
    assert tracker.get_remaining_items_count() == 2


def test_checkpoint_manager_save_and_restore():
    cm = CheckpointManager()
    snapshot = cm.create_checkpoint(
        session_id="SESS-EXEC-001",
        stage="LISTENING",
        item_index=1,
        fsm_state="RUNNING",
    )
    assert snapshot.session_id == "SESS-EXEC-001"

    restored = cm.restore_checkpoint("SESS-EXEC-001")
    assert restored.checkpoint_id == snapshot.checkpoint_id
    assert restored.stage == "LISTENING"

    with pytest.raises(CheckpointFailure):
        cm.restore_checkpoint("NON_EXISTENT_SESSION")


@pytest.mark.asyncio
async def test_aee_facade_stage_execution():
    aee = AssessmentExecutionEngine()
    session, scenario = _create_test_session_and_scenario()

    # Create active context
    ctx = aee.create_context(session, scenario, "LISTENING")
    ctx.fsm.transition_to("RUNNING")

    # Test pause and resume during active execution
    await aee.pause_execution(session.session_id, "User Inactivity")
    assert ctx.fsm.current_state == "PAUSED"

    await aee.resume_execution(session.session_id)
    assert ctx.fsm.current_state == "RUNNING"

    # Execute stage to completion
    res = await aee.execute_stage(session, scenario, "LISTENING")
    assert res["status"] == "COMPLETED"
    assert res["stage"] == "LISTENING"
    assert res["session_id"] == "SESS-EXEC-001"

    restored_snapshot = aee.restore_checkpoint(session.session_id)
    assert restored_snapshot.stage == "LISTENING"
