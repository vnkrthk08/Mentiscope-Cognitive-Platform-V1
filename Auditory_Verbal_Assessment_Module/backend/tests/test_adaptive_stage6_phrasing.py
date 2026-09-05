"""
Unit tests for Stage 6: Follow-up Question Phrasing in Shadow Mode.
"""

import pytest
from app.application.followup_subsystem.facade import AdaptiveInterviewIntelligenceSystem
from app.application.followup_subsystem.session_state import FollowUpSessionState, EvidenceLogEntry


def test_shadow_formatter_helper_methods():
    """Verifies _format_shadow_assessment_state, _format_shadow_behavior_evidence, and _format_shadow_conversation_history."""
    aiis = AdaptiveInterviewIntelligenceSystem()

    state = FollowUpSessionState(
        scenario_id="SCEN-001",
        candidate_id="CAND-001",
        primary_constructs=["DECISION_MAKING", "REASONING"],
    )
    entry = EvidenceLogEntry(
        turn=1,
        source="initial_response",
        claims=["Re-routed battery current limit to 75%."],
        reasoning_shown=["Evaluated climbing speed vs temperature trade-off."],
    )
    state.evidence_log.append(entry)

    summary_state = aiis._format_shadow_assessment_state(state)
    assert "DECISION_MAKING: 0.00 (missing)" in summary_state

    evidence_str = aiis._format_shadow_behavior_evidence(entry)
    assert "Re-routed battery current limit" in evidence_str
    assert "Evaluated climbing speed" in evidence_str

    history_str = aiis._format_shadow_conversation_history(state)
    assert "Turn 1 (initial_response)" in history_str


@pytest.mark.asyncio
async def test_shadow_adaptive_pipeline_stage6_execution():
    """Verifies end-to-end shadow pipeline run (Stages 1 to 6) returning stage6_phrasing payload."""
    aiis = AdaptiveInterviewIntelligenceSystem()
    aiis.enable_shadow_stage6_llm = True

    result = await aiis._run_shadow_adaptive_pipeline(
        session_id="test_stage6_shadow_session",
        scenario_title="Robotics Competition Battery Thermal Limit Crisis",
        transcript_text="I decided to re-route current limits to 75% to prevent overheating.",
        target_constructs=["DECISION_MAKING", "REASONING"],
        turn_number=1,
    )

    assert result["shadow_pipeline_stage"] == "STAGE_1_2_3_4_5_6_COMPLETE"
    assert "stage6_phrasing" in result
    phrasing = result["stage6_phrasing"]
    assert phrasing is not None
    assert "raw_llm_question" in phrasing
    assert "edited_question" in phrasing
    assert "qa_evaluation" in phrasing


@pytest.mark.asyncio
async def test_stage6_exception_isolation():
    """Verifies that an exception inside Stage 6 phrasing logs a warning and returns Stage 1-5 results cleanly without raising."""
    aiis = AdaptiveInterviewIntelligenceSystem()
    aiis.enable_shadow_stage6_llm = True

    # Intentionally break APOS prompt execution for this call to simulate LLM API error
    async def mock_failing_prompt(*args, **kwargs):
        raise RuntimeError("Simulated Nemotron LLM API connection timeout")

    aiis.apos.execute_prompt = mock_failing_prompt

    # Pipeline should NOT raise runtime exception — it must return STAGE_1_2_3_4_5_COMPLETE safely
    result = await aiis._run_shadow_adaptive_pipeline(
        session_id="test_stage6_isolation_session",
        scenario_title="Robotics Competition Battery Thermal Limit Crisis",
        transcript_text="I decided to re-route current limits to 75% to prevent overheating.",
        target_constructs=["DECISION_MAKING", "REASONING"],
        turn_number=1,
    )

    assert result["shadow_pipeline_stage"] == "STAGE_1_2_3_4_5_COMPLETE"
    assert result["stage6_phrasing"] is None
    assert result["stage5_spec"] is not None


@pytest.mark.asyncio
async def test_stage6_timeout_handling(caplog):
    """Verifies that asyncio.TimeoutError during Stage 6 prompt execution logs a distinct timeout warning and returns STAGE_1_2_3_4_5_COMPLETE safely."""
    import asyncio
    aiis = AdaptiveInterviewIntelligenceSystem()
    aiis.enable_shadow_stage6_llm = True

    async def mock_timeout_prompt(*args, **kwargs):
        raise asyncio.TimeoutError()

    aiis.apos.execute_prompt = mock_timeout_prompt

    result = await aiis._run_shadow_adaptive_pipeline(
        session_id="test_stage6_timeout_session",
        scenario_title="Robotics Competition Battery Thermal Limit Crisis",
        transcript_text="I decided to re-route current limits to 75% to prevent overheating.",
        target_constructs=["DECISION_MAKING", "REASONING"],
        turn_number=1,
    )

    assert result["shadow_pipeline_stage"] == "STAGE_1_2_3_4_5_COMPLETE"
    assert result["stage6_phrasing"] is None
    assert "timed out after 45.0s" in caplog.text

