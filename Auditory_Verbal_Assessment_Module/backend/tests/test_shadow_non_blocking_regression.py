"""
Regression test suite ensuring that the shadow adaptive follow-up pipeline
never blocks the live interactive turn execution path.
"""

import asyncio
import time
import pytest
from app.application.followup_subsystem.facade import AdaptiveInterviewIntelligenceSystem


@pytest.mark.asyncio
async def test_live_turn_does_not_block_on_shadow_pipeline():
    """
    Asserts that generate_followup_question returns immediately even if
    the shadow pipeline takes multiple seconds (e.g. slow background LLM calls).
    """
    aiis = AdaptiveInterviewIntelligenceSystem()

    # Track shadow pipeline execution
    shadow_started = asyncio.Event()
    shadow_completed = asyncio.Event()

    async def slow_shadow_pipeline(*args, **kwargs):
        shadow_started.set()
        await asyncio.sleep(0.5)  # Simulate slow background LLM delay
        shadow_completed.set()
        return {"status": "SHADOW_COMPLETE"}

    aiis._run_shadow_adaptive_pipeline = slow_shadow_pipeline

    t0 = time.time()
    res = await aiis.generate_followup_question(
        scenario_title="Robotics Competition Battery Thermal Limit Crisis",
        transcript_text="I decided to re-route current limits to 75% to keep the battery cool.",
        target_construct="DECISION_MAKING",
        session_id="test_non_blocking_session",
    )
    turn_duration = time.time() - t0

    # The main turn must return well before the 0.5s shadow sleep completes
    assert turn_duration < 0.3, f"generate_followup_question took {turn_duration:.3f}s; it is blocking on the shadow pipeline!"
    assert res is not None
    assert "follow_up_question" in res
    assert res["follow_up_question"]

    # Verify that the shadow task was retained in _shadow_tasks set
    assert len(aiis._shadow_tasks) == 1, "Shadow task reference was not retained in _shadow_tasks!"

    # Yield to event loop to allow background task to start
    await shadow_started.wait()
    assert not shadow_completed.is_set(), "Shadow pipeline should still be executing asynchronously in background!"

    # Wait for the background task to complete and clean up
    await shadow_completed.wait()
    await asyncio.sleep(0.01)
    assert len(aiis._shadow_tasks) == 0, "Shadow task reference was not discarded after completion!"
