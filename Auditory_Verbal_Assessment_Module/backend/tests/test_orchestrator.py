import pytest
from app.application.orchestrator import AssessmentOrchestrator, IllegalStateTransitionError, SessionTimeoutError, InvalidSessionStateError
from app.core.event_bus import event_bus
from app.domain.value_objects.enums import SessionStatus


@pytest.mark.asyncio
async def test_orchestrator_valid_lifecycle_execution():
    orchestrator = AssessmentOrchestrator()
    session = orchestrator.create_assessment_session("CAND-100", "SCENARIO-01")

    assert session.metadata["current_fsm_state"] == "CREATED"
    assert session.status == SessionStatus.INITIALIZED

    # 1. Start assessment
    await orchestrator.start_assessment(session)
    assert session.metadata["current_fsm_state"] == "DEVICE_CHECK"
    assert session.status == SessionStatus.IN_PROGRESS

    # 2. Advance through valid sequence
    stages = [
        "INSTRUCTIONS",
        "PRACTICE",
        "SCENARIO_PRESENTATION",
        "LISTENING",
        "SPEAKING",
        "ADAPTIVE_FOLLOWUP",
        "EVIDENCE_PROCESSING",
        "SCORING",
        "REPORT_GENERATION",
        "COMPLETED",
    ]

    for stage in stages:
        await orchestrator.transition_to(session, stage, reason=f"Advancing to {stage}")
        assert session.metadata["current_fsm_state"] == stage

    assert session.status == SessionStatus.COMPLETED
    assert session.completed_at is not None

    audit_trail = orchestrator.get_audit_trail(session.session_id)
    assert len(audit_trail) == 12  # CREATED + 11 transitions


@pytest.mark.asyncio
async def test_orchestrator_illegal_transition_raises_error():
    orchestrator = AssessmentOrchestrator()
    session = orchestrator.create_assessment_session("CAND-101", "SCENARIO-01")
    await orchestrator.start_assessment(session)  # Now in DEVICE_CHECK

    # Attempt illegal transition: DEVICE_CHECK -> LISTENING directly
    with pytest.raises(IllegalStateTransitionError) as exc_info:
        await orchestrator.transition_to(session, "LISTENING", reason="Illegal skip")

    assert exc_info.value.current_stage == "DEVICE_CHECK"
    assert exc_info.value.target_stage == "LISTENING"


@pytest.mark.asyncio
async def test_orchestrator_pause_and_resume_flow():
    orchestrator = AssessmentOrchestrator()
    session = orchestrator.create_assessment_session("CAND-102", "SCENARIO-01")
    await orchestrator.start_assessment(session)
    await orchestrator.transition_to(session, "INSTRUCTIONS")
    await orchestrator.transition_to(session, "PRACTICE")
    await orchestrator.transition_to(session, "SCENARIO_PRESENTATION")
    await orchestrator.transition_to(session, "LISTENING")

    session.metadata["last_active_stage"] = "LISTENING"

    # Pause assessment
    await orchestrator.pause_assessment(session, reason="User paused session")
    assert session.metadata["current_fsm_state"] == "PAUSED"
    assert session.status == SessionStatus.PAUSED

    # Resume assessment
    await orchestrator.resume_assessment(session)
    assert session.metadata["current_fsm_state"] == "LISTENING"
    assert session.status == SessionStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_orchestrator_completion_percentage_calculation():
    orchestrator = AssessmentOrchestrator()
    session = orchestrator.create_assessment_session("CAND-103", "SCENARIO-01")
    
    assert orchestrator.calculate_completion_percentage(session) == 0.0
    await orchestrator.start_assessment(session)  # DEVICE_CHECK = idx 1
    assert orchestrator.calculate_completion_percentage(session) > 0.0
    
    await orchestrator.transition_to(session, "INSTRUCTIONS")
    await orchestrator.transition_to(session, "PRACTICE")
    await orchestrator.transition_to(session, "SCENARIO_PRESENTATION")
    await orchestrator.transition_to(session, "LISTENING")
    
    listening_pct = orchestrator.calculate_completion_percentage(session)
    assert listening_pct > 30.0


@pytest.mark.asyncio
async def test_orchestrator_domain_events_published(monkeypatch):
    events_published = []

    async def mock_publish(event_type: str, payload: Any):
        events_published.append(event_type)

    monkeypatch.setattr(event_bus, "publish", mock_publish)

    orchestrator = AssessmentOrchestrator()
    session = orchestrator.create_assessment_session("CAND-104", "SCENARIO-01")
    await orchestrator.start_assessment(session)
    await orchestrator.transition_to(session, "INSTRUCTIONS")

    assert "AssessmentStarted" in events_published
    assert "StageEntered" in events_published
