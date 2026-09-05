import pytest
from app.application.speaking_engine import (
    SpeakingAssessmentEngine,
    RecordingManager,
    RecordingValidator,
    SpeakingNavigator,
    SpeakingResponseCollector,
    SpeakingResultBuilder,
)
from app.application.scenario_subsystem import ScenarioManagementSystem
from app.application.execution_engine import AssessmentExecutionEngine
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.value_objects.time_limit import TimeLimit
from app.domain.value_objects.enums import ConstructType
from app.domain.exceptions.speaking_exceptions import (
    RecordingTooShort,
    InvalidRecordingFormat,
    RecordingNotFound,
)


def _create_test_prompt():
    return SpeakingPrompt(
        prompt_id="S_P1",
        title="Team Emergency Briefing",
        instructions="Explain decision clearly",
        time_limit=TimeLimit(max_seconds=120),
        target_constructs=[ConstructType.COMMUNICATION, ConstructType.DECISION_MAKING],
    )


def test_recording_manager_lifecycle():
    rm = RecordingManager()
    assert rm.initialize_device() is True

    rm.start_recording("S_P1")
    assert rm.active_status == "RECORDING"

    rm.pause_recording()
    assert rm.active_status == "PAUSED"

    rm.resume_recording()
    assert rm.active_status == "RECORDING"

    rec_meta = rm.stop_recording("S_P1")
    assert rec_meta["file_url"].endswith("S_P1_rec.webm")
    assert rec_meta["duration_seconds"] >= 2.0


def test_recording_validator():
    validator = RecordingValidator()

    # Valid recording
    valid_meta = {"file_url": "/audio/rec.webm", "duration_seconds": 15.0, "format": "audio/webm", "file_size_bytes": 1024}
    assert validator.validate_recording(valid_meta) is True

    # Too short recording exception
    short_meta = {"file_url": "/audio/rec.webm", "duration_seconds": 0.5, "format": "audio/webm", "file_size_bytes": 1024}
    with pytest.raises(RecordingTooShort):
        validator.validate_recording(short_meta, min_duration_seconds=2.0)

    # Invalid format exception
    invalid_fmt = {"file_url": "/audio/rec.txt", "duration_seconds": 15.0, "format": "text/plain", "file_size_bytes": 1024}
    with pytest.raises(InvalidRecordingFormat):
        validator.validate_recording(invalid_fmt)


def test_speaking_response_collector():
    collector = SpeakingResponseCollector()
    prompt = _create_test_prompt()
    meta = {"file_url": "/audio/rec.webm", "duration_seconds": 12.5, "format": "audio/webm"}

    resp = collector.collect_response("SESS-01", prompt, meta)
    assert resp.prompt_id == "S_P1"
    assert resp.audio_file_url == "/audio/rec.webm"
    assert resp.duration_seconds == 12.5
    assert resp.transcript_text is None  # Ensures SAE does NOT transcribe speech!


def test_speaking_result_builder():
    builder = SpeakingResultBuilder()
    collector = SpeakingResponseCollector()
    prompt = _create_test_prompt()
    meta = {"file_url": "/audio/rec.webm", "duration_seconds": 10.0, "format": "audio/webm"}

    resp = collector.collect_response("SESS-01", prompt, meta)
    result = builder.build_result("SESS-01", "SCENARIO_01", [prompt], {"S_P1": resp})

    assert result.total_prompts == 1
    assert result.completed_prompts_count == 1
    assert result.total_speaking_duration_seconds == 10.0
    assert "S_P1" in result.responses


@pytest.mark.asyncio
async def test_sae_facade_and_aee_integration():
    sms = ScenarioManagementSystem()
    scenario = await sms.load_scenario("SCENARIO_LOGISTICS_01")
    session = AssessmentSession(session_id="SESS-SAE-001", candidate_id="CAND-01", scenario_id=scenario.scenario_id)

    sae = SpeakingAssessmentEngine()
    aee = AssessmentExecutionEngine()

    # Execute speaking stage via AEE delegating to SAE
    res = await aee.execute_stage(session, scenario, "SPEAKING", executor=sae)

    assert res["status"] == "COMPLETED"
    assert res["stage"] == "SPEAKING"
    assert res["result"]["total_prompts"] == 2
    assert res["result"]["completed_prompts_count"] == 2
    assert res["result"]["total_speaking_duration_seconds"] > 0.0
