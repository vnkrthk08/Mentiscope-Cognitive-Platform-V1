import pytest
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.entities.behavioural_indicator import BehaviouralIndicator
from app.domain.value_objects.enums import ConstructType
from app.domain.value_objects.time_limit import TimeLimit
from app.domain.assessment.speaking_canonical_config import (
    CANONICAL_SPEAKING_SPECS,
    CANONICAL_SQ1_INDICATORS,
    CANONICAL_SQ2_INDICATORS,
    CANONICAL_SQ3_INDICATORS,
)
from app.application.scenario_subsystem.scenario_repository import ScenarioRepository
from app.application.scenario_subsystem.factory import ScenarioFactory
from app.application.scenario_subsystem.scenario_dto import ScenarioDTO
from app.infrastructure.persistence.mappers.scenario_mapper import ScenarioMapper


def test_1_every_speaking_prompt_contains_exactly_5_indicators():
    """TEST 1: Every canonical speaking prompt contains exactly 5 indicators."""
    assert len(CANONICAL_SQ1_INDICATORS) == 5
    assert len(CANONICAL_SQ2_INDICATORS) == 5
    assert len(CANONICAL_SQ3_INDICATORS) == 5

    repo = ScenarioRepository()
    for scenario in repo.list_all_scenarios():
        for sp in scenario.speaking_prompts:
            assert len(sp.behavioural_indicators) == 5, f"Scenario {scenario.scenario_id} prompt {sp.prompt_id} does not have 5 indicators"


def test_2_every_indicator_contains_anchors_0_to_4():
    """TEST 2: Every indicator contains anchors for scores 0, 1, 2, 3, 4."""
    for q_id, spec in CANONICAL_SPEAKING_SPECS.items():
        for ind in spec["behavioural_indicators"]:
            assert set(ind.anchors.keys()) == {"0", "1", "2", "3", "4"}, f"Indicator {ind.indicator_id} missing anchors in {q_id}"
            for score in ["0", "1", "2", "3", "4"]:
                assert len(ind.anchors[score].strip()) > 0, f"Anchor {score} empty in {ind.indicator_id}"


def test_3_every_question_has_weight_sum_4_point_6():
    """TEST 3: Every question has sum(weights) == 4.6."""
    for q_id, spec in CANONICAL_SPEAKING_SPECS.items():
        w_sum = round(sum(ind.weight for ind in spec["behavioural_indicators"]), 2)
        assert w_sum == 4.6, f"{q_id} weight sum is {w_sum}, expected 4.6"


def test_4_every_question_has_max_weighted_score_18_point_4():
    """TEST 4: Every question has maximum weighted indicator score == 18.4."""
    for q_id, spec in CANONICAL_SPEAKING_SPECS.items():
        max_score = round(sum(4.0 * ind.weight for ind in spec["behavioural_indicators"]), 2)
        assert max_score == 18.4, f"{q_id} max score is {max_score}, expected 18.4"
        assert spec["max_indicator_weighted_score"] == 18.4


def test_5_every_scenario_has_exactly_3_speaking_questions():
    """TEST 5: Every scenario in ScenarioRepository has exactly 3 speaking questions."""
    repo = ScenarioRepository()
    scenarios = repo.list_all_scenarios()
    assert len(scenarios) == 50, f"Expected 50 scenarios, got {len(scenarios)}"
    for scen in scenarios:
        assert len(scen.speaking_prompts) == 3, f"Scenario {scen.scenario_id} has {len(scen.speaking_prompts)} speaking prompts, expected 3"


def test_6_question_order_is_sq1_sq2_sq3():
    """TEST 6: Question order is strictly SQ1 -> SQ2 -> SQ3."""
    repo = ScenarioRepository()
    for scen in repo.list_all_scenarios():
        assert scen.speaking_prompts[0].question_id == "SQ1"
        assert scen.speaking_prompts[0].stage == "STAGE_1_DECISION"

        assert scen.speaking_prompts[1].question_id == "SQ2"
        assert scen.speaking_prompts[1].stage == "STAGE_2_CHALLENGE"

        assert scen.speaking_prompts[2].question_id == "SQ3"
        assert scen.speaking_prompts[2].stage == "STAGE_3_REFLECTIVE"


def test_7_construct_mapping_is_canonical():
    """
    TEST 7: Construct mapping is strictly:
    SQ1 -> DECISION_MAKING (primary) / COMMUNICATION (secondary)
    SQ2 -> ADAPTABILITY (primary) / DECISION_MAKING (secondary)
    SQ3 -> REASONING (primary) / COMMUNICATION (secondary)
    """
    repo = ScenarioRepository()
    for scen in repo.list_all_scenarios():
        sq1, sq2, sq3 = scen.speaking_prompts

        assert sq1.primary_constructs == [ConstructType.DECISION_MAKING]
        assert sq1.secondary_constructs == [ConstructType.COMMUNICATION]

        assert sq2.primary_constructs == [ConstructType.ADAPTABILITY]
        assert sq2.secondary_constructs == [ConstructType.DECISION_MAKING]

        assert sq3.primary_constructs == [ConstructType.REASONING]
        assert sq3.secondary_constructs == [ConstructType.COMMUNICATION]


def test_8_scenario_orm_roundtrip_is_lossless():
    """TEST 8: Scenario -> ORM -> Scenario roundtrip preserves all psychometric metadata."""
    repo = ScenarioRepository()
    for scen in repo.list_all_scenarios():
        orm = ScenarioMapper.to_orm(scen)
        restored = ScenarioMapper.to_domain(orm)

        assert len(restored.speaking_prompts) == 3
        for original_sp, restored_sp in zip(scen.speaking_prompts, restored.speaking_prompts):
            assert original_sp.question_id == restored_sp.question_id
            assert original_sp.stage == restored_sp.stage
            assert original_sp.title == restored_sp.title
            assert original_sp.instructions == restored_sp.instructions
            assert original_sp.objective == restored_sp.objective
            assert original_sp.primary_constructs == restored_sp.primary_constructs
            assert original_sp.secondary_constructs == restored_sp.secondary_constructs
            assert original_sp.max_indicator_weighted_score == restored_sp.max_indicator_weighted_score
            assert len(original_sp.behavioural_indicators) == len(restored_sp.behavioural_indicators)

            for orig_ind, rest_ind in zip(original_sp.behavioural_indicators, restored_sp.behavioural_indicators):
                assert orig_ind.indicator_id == rest_ind.indicator_id
                assert orig_ind.name == rest_ind.name
                assert orig_ind.weight == rest_ind.weight
                assert orig_ind.scale == rest_ind.scale
                assert orig_ind.anchors == rest_ind.anchors


def test_9_scenario_dto_preserves_canonical_psychometrics():
    """TEST 9: ScenarioDTO correctly transports all canonical psychometric data for API consumers."""
    repo = ScenarioRepository()
    for scen in repo.list_all_scenarios():
        dto = ScenarioDTO.from_domain(scen)
        assert len(dto.speaking_prompts) == 3

        sq1, sq2, sq3 = dto.speaking_prompts
        assert sq1.question_id == "SQ1"
        assert sq1.stage == "STAGE_1_DECISION"
        assert sq1.primary_constructs == ["DECISION_MAKING"]
        assert sq1.secondary_constructs == ["COMMUNICATION"]
        assert len(sq1.behavioural_indicators) == 5

        assert sq2.question_id == "SQ2"
        assert sq2.stage == "STAGE_2_CHALLENGE"
        assert sq2.primary_constructs == ["ADAPTABILITY"]
        assert sq2.secondary_constructs == ["DECISION_MAKING"]
        assert len(sq2.behavioural_indicators) == 5

        assert sq3.question_id == "SQ3"
        assert sq3.stage == "STAGE_3_REFLECTIVE"
        assert sq3.primary_constructs == ["REASONING"]
        assert sq3.secondary_constructs == ["COMMUNICATION"]
        assert len(sq3.behavioural_indicators) == 5


def test_10_legacy_fallback_migration_on_incomplete_scenario():
    """TEST 10: Incomplete legacy scenario (1 prompt) is automatically migrated with grounded SQ2/SQ3."""
    legacy_data = {
        "id": "SCEN-LEGACY-01",
        "title": "Legacy Test Scenario",
        "narrative": "A legacy narrative for migration test.",
        "version": "1.0.0",
        "difficulty": "INTERMEDIATE",
        "audio_asset": {"url": "/audio/legacy.mp3", "duration_seconds": 120.0, "format": "audio/mp3"},
        "listening_questions": [
            {
                "question_id": "LQ_LEGACY",
                "prompt": "What is the key topic?",
                "options": ["Topic A", "Topic B", "Topic C", "Topic D"],
                "correct_option_index": 0,
                "target_construct": "LISTENING_COMPREHENSION",
                "difficulty": "INTERMEDIATE",
            }
        ],
        "speaking_prompts": [
            {
                "prompt_id": "SP_OLD_1",
                "title": "Old Prompt",
                "instructions": "Make a decision.",
                "max_seconds": 120,
                "target_constructs": ["DECISION_MAKING"],
                "followup_eligible": True,
            }
        ],
    }


    factory = ScenarioFactory()
    scenario = factory.create_from_dict(legacy_data)

    assert len(scenario.speaking_prompts) == 3
    assert scenario.speaking_prompts[0].question_id == "SQ1"
    assert scenario.speaking_prompts[1].question_id == "SQ2"
    assert scenario.speaking_prompts[2].question_id == "SQ3"
    assert len(scenario.speaking_prompts[0].behavioural_indicators) == 5
    assert len(scenario.speaking_prompts[1].behavioural_indicators) == 5
    assert len(scenario.speaking_prompts[2].behavioural_indicators) == 5
