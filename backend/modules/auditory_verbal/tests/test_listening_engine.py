import pytest
from app.application.listening_engine import (
    ListeningAssessmentEngine,
    ListeningPlayer,
    ListeningNavigator,
    ListeningResponseCollector,
    ListeningValidator,
    ListeningResultBuilder,
)
from app.application.scenario_subsystem import ScenarioManagementSystem
from app.application.execution_engine import AssessmentExecutionEngine
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.value_objects.audio_asset import AudioAsset
from app.domain.value_objects.enums import ConstructType
from app.domain.exceptions.listening_exceptions import (
    InvalidAnswerOption,
    AudioNotLoaded,
    ListeningValidationError,
)


def _create_test_question():
    return ListeningQuestion(
        question_id="L_Q1",
        prompt="What container was delayed?",
        options=["Option 0 (Correct)", "Option 1", "Option 2"],
        correct_option_index=0,
        target_construct=ConstructType.ATTENTION,
    )


def test_listening_player_lifecycle():
    player = ListeningPlayer()
    with pytest.raises(AudioNotLoaded):
        player.start()

    audio = AudioAsset(url="/audio/test.mp3", duration_seconds=60)
    player.load_audio(audio)
    assert player.playback_status == "LOADED"

    player.start()
    assert player.playback_status == "PLAYING"

    player.pause()
    assert player.playback_status == "PAUSED"

    player.resume()
    assert player.playback_status == "PLAYING"

    player.stop()
    assert player.playback_status == "STOPPED"


def test_listening_navigator():
    q1 = _create_test_question()
    q2 = ListeningQuestion(
        question_id="L_Q2",
        prompt="What location?",
        options=["Port A", "Port B"],
        correct_option_index=1,
        target_construct=ConstructType.WORKING_MEMORY,
    )
    nav = ListeningNavigator([q1, q2])

    assert nav.get_current_question().question_id == "L_Q1"
    assert nav.has_next() is True

    next_q = nav.next_question()
    assert next_q.question_id == "L_Q2"
    assert nav.has_next() is False


def test_listening_response_collector_and_validator():
    q = _create_test_question()
    collector = ListeningResponseCollector()
    validator = ListeningValidator()

    # Valid response
    resp = collector.collect_response("SESS-01", q, selected_option_index=0, response_time_ms=1500)
    assert resp.selected_option_index == 0
    assert validator.is_answer_correct(q, resp) is True

    # Invalid option index exception
    with pytest.raises(InvalidAnswerOption):
        collector.collect_response("SESS-01", q, selected_option_index=5, response_time_ms=1000)


def test_listening_result_builder():
    q = _create_test_question()
    collector = ListeningResponseCollector()
    builder = ListeningResultBuilder()

    resp = collector.collect_response("SESS-01", q, selected_option_index=0, response_time_ms=2000)
    result = builder.build_result(
        session_id="SESS-01",
        scenario_id="SCENARIO_01",
        questions=[q],
        responses={"L_Q1": resp},
        replay_status={"L_Q1": 1},
    )

    assert result.total_questions == 1
    assert result.correct_count == 1
    assert result.raw_accuracy_percentage == 100.0
    assert result.average_response_time_ms == 2000.0


@pytest.mark.asyncio
async def test_lae_facade_and_aee_integration():
    sms = ScenarioManagementSystem()
    scenario = await sms.load_scenario("SCENARIO_LOGISTICS_01")
    session = AssessmentSession(session_id="SESS-LAE-001", candidate_id="CAND-01", scenario_id=scenario.scenario_id)

    lae = ListeningAssessmentEngine()
    aee = AssessmentExecutionEngine()

    # Execute listening stage via AEE delegating to LAE
    res = await aee.execute_stage(session, scenario, "LISTENING", executor=lae)

    assert res["status"] == "COMPLETED"
    assert res["stage"] == "LISTENING"
    assert res["result"]["raw_accuracy_percentage"] == 100.0
    assert res["result"]["total_questions"] == 4
