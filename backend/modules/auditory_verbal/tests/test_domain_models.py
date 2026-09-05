import pytest
from app.domain.entities.scenario import Scenario
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.evidence import Evidence
from app.domain.value_objects.enums import AssessmentStage, ConstructType, DifficultyLevel
from app.domain.value_objects.audio_asset import AudioAsset
from app.domain.value_objects.time_limit import TimeLimit
from app.domain.value_objects.scenario_version import ScenarioVersion
from app.domain.value_objects.confidence_level import ConfidenceLevel


def test_scenario_aggregate_invariants():
    audio = AudioAsset(url="/audio/test.mp3", duration_seconds=120)
    version = ScenarioVersion("1.0.0")

    question = ListeningQuestion(
        question_id="Q1",
        prompt="What was discussed?",
        options=["Option A", "Option B"],
        correct_option_index=0,
        target_construct=ConstructType.WORKING_MEMORY,
    )

    prompt = SpeakingPrompt(
        prompt_id="P1",
        title="Team Briefing",
        instructions="Explain your decision",
        time_limit=TimeLimit(max_seconds=120),
        target_constructs=[ConstructType.COMMUNICATION],
    )

    scenario = Scenario(
        scenario_id="S1",
        title="Logistics Crisis",
        narrative="A supply chain disruption occurred.",
        audio_asset=audio,
        listening_questions=[question],
        speaking_prompts=[prompt],
        version=version,
    )

    assert scenario.scenario_id == "S1"
    assert len(scenario.listening_questions) == 1
    assert len(scenario.speaking_prompts) == 1


def test_scenario_missing_questions_invariant_raises_error():
    audio = AudioAsset(url="/audio/test.mp3", duration_seconds=120)
    version = ScenarioVersion("1.0.0")

    prompt = SpeakingPrompt(
        prompt_id="P1",
        title="Team Briefing",
        instructions="Explain your decision",
        time_limit=TimeLimit(max_seconds=120),
        target_constructs=[ConstructType.COMMUNICATION],
    )

    with pytest.raises(ValueError, match="must contain at least one listening question"):
        Scenario(
            scenario_id="S1",
            title="Logistics Crisis",
            narrative="A supply chain disruption occurred.",
            audio_asset=audio,
            listening_questions=[],
            speaking_prompts=[prompt],
            version=version,
        )


def test_session_illegal_backwards_transition_raises_error():
    session = AssessmentSession(
        session_id="SESS-001",
        candidate_id="CAND-001",
        scenario_id="SCENARIO-001",
    )

    session.transition_to_stage(AssessmentStage.LISTENING_ASSESSMENT)
    assert session.progress.current_stage == AssessmentStage.LISTENING_ASSESSMENT

    with pytest.raises(ValueError, match="Cannot move backwards"):
        session.transition_to_stage(AssessmentStage.DEVICE_CHECK)


def test_confidence_level_bounds_invariant():
    valid_conf = ConfidenceLevel(0.85)
    assert valid_conf.score == 0.85

    with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
        ConfidenceLevel(1.5)
