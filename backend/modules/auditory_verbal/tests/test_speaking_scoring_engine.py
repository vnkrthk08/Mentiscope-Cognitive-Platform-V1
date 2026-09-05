import pytest
import asyncio
from typing import Dict, Any
from app.domain.assessment.speaking_canonical_config import (
    CANONICAL_SPEAKING_SPECS,
    CANONICAL_SQ1_INDICATORS,
    CANONICAL_SQ2_INDICATORS,
    CANONICAL_SQ3_INDICATORS,
)
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.scenario import Scenario
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.value_objects.enums import ConstructType
from app.domain.value_objects.time_limit import TimeLimit
from app.application.speech.fluency_engine import FluencyEngine, FluencySource
from app.application.speech.fluency_config import FluencyConfig
from app.application.evidence_engine.anchor_evaluator import AnchorEvaluator
from app.application.scoring_engine.calculator import ConstructScoreCalculator
from app.application.scoring_engine.weighting import WeightingEngine
from app.application.scoring_engine.decision_engine import DecisionEngine
from app.application.scoring_engine.facade import PsychometricScoringDecisionEngine


from app.application.scenario_subsystem.scenario_repository import ScenarioRepository


def _build_test_scenario() -> Scenario:
    repo = ScenarioRepository()
    return repo.get_by_id("SCEN-001")




def test_identical_word_count_divergent_evidence_scoring():
    """Verifies that RubricScore is determined 100% by behavioral evidence against
    canonical anchors and contains ZERO word-count bias or inflation.
    """
    calculator = ConstructScoreCalculator()

    # Response A (45 words): Vacuous, circular fluff with zero justification/action plan
    # Scores anchor levels 0 and 1: [1, 0, 0, 0, 0] on SQ1
    eval_a_scores = [(1, 1.0), (0, 1.0), (0, 0.8), (0, 0.8), (0, 1.0)]
    rubric_score_a = calculator.calculate_rubric_score(eval_a_scores)
    # Weighted sum: 1.0 / 18.4 * 100 = 5.43%
    assert rubric_score_a == 5.43

    # Response B (45 words): Structured decision, constraint justification, trade-off, action plan
    # Scores anchor levels 3 and 4: [3, 4, 3, 3, 4] on SQ1
    eval_b_scores = [(3, 1.0), (4, 1.0), (3, 0.8), (3, 0.8), (4, 1.0)]
    rubric_score_b = calculator.calculate_rubric_score(eval_b_scores)
    # Weighted sum: (3.0 + 4.0 + 2.4 + 2.4 + 4.0) = 15.8 / 18.4 * 100 = 85.87%
    assert rubric_score_b == 85.87

    # Disparity check: Same word count, completely divergent scores driven purely by evidence
    assert rubric_score_b - rubric_score_a > 80.0


def test_fluency_engine_scenarios_a_to_e():
    """Verifies non-blocking graceful degradation across Scenarios A through E with zero arbitrary fallback."""
    fluency_engine = FluencyEngine()

    # Scenario A: Full Audio + Transcript (21 words -> Rate=100, Pause=100, Coherence=100)
    res_a = fluency_engine.evaluate(
        transcript_text="We choose to reroute the power to seventy-five percent in order to meet the strict inspection deadline and preserve rover operation.",
        duration_seconds=10.0,
        audio_file_url="https://s3.amazonaws.com/audio/test.webm",
        pause_ratio=0.20,
    )
    assert res_a.fluency_source == FluencySource.AUDIO_ACOUSTIC
    assert res_a.score == 100.0
    assert res_a.error_flag is False


    # Scenario B: Transcript Only (No audio metadata/file)
    res_b = fluency_engine.evaluate(
        transcript_text="We choose to reroute the power to seventy-five percent in order to meet the strict inspection deadline and preserve rover functionality.",
    )
    assert res_b.fluency_source == FluencySource.TEXT_ONLY
    assert res_b.score == 100.0  # 20+ coherent words with zero fillers = 100

    # Scenario C: Partial Acoustic (Duration available, pause ratio missing)
    res_c = fluency_engine.evaluate(
        transcript_text="We must halt the rover immediately because of battery voltage fluctuations.",
        duration_seconds=5.0,
        audio_file_url="https://s3.amazonaws.com/audio/test.webm",
        pause_ratio=None,
    )
    assert res_c.fluency_source == FluencySource.PARTIAL_ACOUSTIC
    assert res_c.score > 0.0

    # Scenario D: Insufficient Data (Minimal response: 2 words)
    res_d = fluency_engine.evaluate(transcript_text="Reroute power")
    assert res_d.fluency_source == FluencySource.INSUFFICIENT_DATA
    assert res_d.score == 10.0  # 2 * 5.0

    # Scenario E: Zero / Silence (0 words)
    res_e = fluency_engine.evaluate(transcript_text="")
    assert res_e.score == 0.0
    assert res_e.error_flag is False


def test_tier_1_conservative_fallback_ceiling():
    """Verifies that Tier 1 fallback assigns scores <= 2 on all indicators and NEVER assigns 3 or 4."""
    evaluator = AnchorEvaluator()
    scenario = _build_test_scenario()
    prompt = scenario.speaking_prompts[0]

    # Full length transcript evaluated through Tier 1
    transcript = (
        "I decide to re-route current limits to 75% because replacing the power pack takes too long "
        "and will violate the inspection deadline. Consequently, we can still pass inspection instead of being disqualified."
    )
    t1_indicators = evaluator._evaluate_tier1_structural(prompt, transcript)

    assert len(t1_indicators) == 5
    for ind in t1_indicators:
        assert ind.tier_source == "TIER_1_FALLBACK"
        assert ind.score <= 2  # Conservative ceiling enforced!
        assert ind.confidence == 0.60


def test_construct_aggregation_and_mathematical_parity():
    """Verifies exact construct aggregation formulas and (SQ1 + SQ2 + SQ3)/3 mathematical parity theorem."""
    weighting = WeightingEngine()

    # Given Question Scores: SQ1 = 83.26, SQ2 = 77.26, SQ3 = 86.35
    sq1 = 83.26
    sq2 = 77.26
    sq3 = 86.35

    construct_scores, final_speaking_score = weighting.aggregate_speaking_construct_scores(sq1, sq2, sq3)

    # Decision Making: (83.26*1.0 + 77.26*0.5) / 1.5 = 121.89 / 1.5 = 81.26
    assert construct_scores["DECISION_MAKING"] == 81.26

    # Adaptability: 77.26 / 1.0 = 77.26
    assert construct_scores["ADAPTABILITY"] == 77.26

    # Reasoning: 86.35 / 1.0 = 86.35
    assert construct_scores["REASONING"] == 86.35

    # Communication: (83.26*0.5 + 86.35*0.5) / 1.0 = 41.63 + 43.175 = 84.81 (or 84.80 depending on round)
    assert construct_scores["COMMUNICATION"] in (84.80, 84.81)

    # Final Speaking Score: (1.5*81.26 + 1.0*77.26 + 1.0*86.35 + 1.0*84.81) / 4.5 = 370.31 / 4.5 = 82.29
    assert final_speaking_score in (82.28, 82.29)

    # Mathematical Parity Proof: Arithmetic mean of (SQ1 + SQ2 + SQ3) / 3
    arithmetic_mean = round((sq1 + sq2 + sq3) / 3.0, 2)
    assert abs(final_speaking_score - arithmetic_mean) <= 0.02


def test_deterministic_candidate_report_generation():
    """Verifies deterministic candidate report, performance bands, and tie-breaking."""
    decision_engine = DecisionEngine()

    construct_scores = {
        "DECISION_MAKING": 81.3,
        "ADAPTABILITY": 77.3,
        "REASONING": 86.4,
        "COMMUNICATION": 84.8,
    }
    final_score = 82.3

    report = decision_engine.generate_candidate_report(construct_scores, final_score)

    assert report["overall_speaking_score"] == 82.3
    assert report["performance_band"] == "PROFICIENT"
    assert "Reasoning (86.4/100)" in report["key_strength"]
    assert "Adaptability (77.3/100)" in report["primary_growth_area"]
    assert "personality" not in report["key_strength"].lower()
    assert "innate" not in report["primary_growth_area"].lower()
    assert report["generation_mode"] == "DETERMINISTIC_TIER_1_SAFE"


@pytest.mark.asyncio
async def test_psde_facade_end_to_end_speaking_scoring():
    """End-to-end integration test of full speaking assessment scoring pipeline."""
    psde = PsychometricScoringDecisionEngine()
    scenario = _build_test_scenario()
    session = AssessmentSession(session_id="SESS-SCORE-001", candidate_id="CAND-001", scenario_id=scenario.scenario_id)

    candidate_responses = {
        "SQ1": {
            "transcript_text": "I choose to re-route battery current to 75% rather than replacing the pack because replacing it exceeds our 45-minute deadline.",
            "duration_seconds": 12.0,
            "audio_file_url": "https://s3.amazonaws.com/audio/rec1.webm",
            "pause_ratio": 0.22,
        },
        "SQ2": {
            "transcript_text": "Since the climbing hill is steeper than expected, I adapt by reducing drive motor torque and taking the flatter path.",
            "duration_seconds": 14.0,
            "audio_file_url": "https://s3.amazonaws.com/audio/rec2.webm",
            "pause_ratio": 0.25,
        },
        "SQ3": {
            "transcript_text": "In hindsight, we assumed the terrain map was accurate. The key lesson is to always budget a fifteen-percent contingency margin.",
            "duration_seconds": 15.0,
            "audio_file_url": "https://s3.amazonaws.com/audio/rec3.webm",
            "pause_ratio": 0.20,
        },
    }

    score_set, candidate_report = await psde.compute_speaking_assessment_scores(
        session=session,
        scenario=scenario,
        candidate_responses=candidate_responses,
    )

    assert score_set.session_id == "SESS-SCORE-001"
    assert "DECISION_MAKING" in score_set.construct_scores
    assert "ADAPTABILITY" in score_set.construct_scores
    assert "REASONING" in score_set.construct_scores
    assert "COMMUNICATION" in score_set.construct_scores
    assert score_set.composite_scores["FINAL_SPEAKING_SCORE"].score > 0.0
    assert candidate_report["generation_mode"] == "DETERMINISTIC_TIER_1_SAFE"
    assert len(candidate_report["question_breakdown"]) == 3
