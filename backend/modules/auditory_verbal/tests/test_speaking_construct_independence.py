import pytest
from app.domain.assessment.speaking_canonical_config import (
    CANONICAL_SPEAKING_SPECS,
    CANONICAL_SQ1_INDICATORS,
    CANONICAL_SQ2_INDICATORS,
    CANONICAL_SQ3_INDICATORS,
)
from app.application.scenario_subsystem.scenario_repository import ScenarioRepository
from app.application.evidence_engine.anchor_evaluator import AnchorEvaluator
from app.application.scoring_engine.facade import PsychometricScoringDecisionEngine
from app.application.scoring_engine.weighting import WeightingEngine
from app.domain.entities.assessment_session import AssessmentSession


@pytest.fixture
def test_scenario():
    repo = ScenarioRepository()
    return repo.get_by_id("SCEN-001")


@pytest.fixture
def psde_engine():
    return PsychometricScoringDecisionEngine()


def test_1_psychometric_invariants():
    """Verifies that all canonical psychometric invariants are strictly intact."""
    for q_id, spec in CANONICAL_SPEAKING_SPECS.items():
        indicators = spec["behavioural_indicators"]
        assert len(indicators) == 5, f"{q_id} must have exactly 5 behavioural indicators"
        
        weight_sum = sum(ind.weight for ind in indicators)
        assert round(weight_sum, 2) == 4.6, f"{q_id} weight sum must be 4.6"
        
        max_weighted = 4.0 * weight_sum
        assert round(max_weighted, 2) == 18.4, f"{q_id} max weighted score must be 18.4"
        
        for ind in indicators:
            assert ind.scale == "0-4"
            assert set(ind.anchors.keys()) == {"0", "1", "2", "3", "4"}


def test_2_zero_evidence_scoring_all_zeroes(test_scenario, psde_engine):
    """TEST 8: For a no-response candidate, all 4 speaking constructs receive legitimate zero scores."""
    session = AssessmentSession(session_id="SESS-ZERO-TEST", candidate_id="CAND-000", scenario_id=test_scenario.scenario_id)
    zero_responses = {
        "SQ1": {"transcript_text": "", "duration_seconds": 0.0},
        "SQ2": {"transcript_text": "", "duration_seconds": 0.0},
        "SQ3": {"transcript_text": "", "duration_seconds": 0.0},
    }

    score_set, report = asyncio_run(psde_engine.compute_speaking_assessment_scores(
        session=session,
        scenario=test_scenario,
        candidate_responses=zero_responses,
    ))

    c_scores = report["demonstrated_construct_scores"]
    assert c_scores["DECISION_MAKING"]["score"] == 0.0
    assert c_scores["ADAPTABILITY"]["score"] == 0.0
    assert c_scores["REASONING"]["score"] == 0.0
    assert c_scores["COMMUNICATION"]["score"] == 0.0
    assert report["overall_speaking_score"] == 0.0
    assert report["performance_band"] == "EMERGING"


def test_3_controlled_differentiated_response_test(test_scenario, psde_engine):
    """TEST 6: Controlled speaking-response test with Response A vs Response B."""
    session_a = AssessmentSession(session_id="SESS-DIFF-A", candidate_id="CAND-A", scenario_id=test_scenario.scenario_id)
    # Response A: Strong decision reasoning, weak adaptability, weak reflection
    resp_a = {
        "SQ1": {
            "transcript_text": "I decisively choose to re-route battery current to 75% because replacing it requires 90 minutes and violates the strict deadline. Rather than total disqualification, this alternative ensures thermal stability while executing our roadmap.",
            "duration_seconds": 18.0,
            "words_per_second": 2.2,
            "pause_ratio": 0.15,
        },
        "SQ2": {
            "transcript_text": "I will stick to the original path.",
            "duration_seconds": 4.0,
            "words_per_second": 1.5,
            "pause_ratio": 0.40,
        },
        "SQ3": {
            "transcript_text": "Nothing to improve.",
            "duration_seconds": 3.0,
            "words_per_second": 1.0,
            "pause_ratio": 0.50,
        },
    }

    _, report_a = asyncio_run(psde_engine.compute_speaking_assessment_scores(
        session=session_a,
        scenario=test_scenario,
        candidate_responses=resp_a,
    ))
    scores_a = report_a["demonstrated_construct_scores"]

    # Decision Making must be significantly higher than Adaptability and Reasoning in Response A
    assert scores_a["DECISION_MAKING"]["score"] > scores_a["ADAPTABILITY"]["score"]
    assert scores_a["DECISION_MAKING"]["score"] > scores_a["REASONING"]["score"]

    # Response B: Weak decision reasoning, strong adaptability, strong reflection
    session_b = AssessmentSession(session_id="SESS-DIFF-B", candidate_id="CAND-B", scenario_id=test_scenario.scenario_id)
    resp_b = {
        "SQ1": {
            "transcript_text": "I do not know.",
            "duration_seconds": 3.0,
            "words_per_second": 1.3,
            "pause_ratio": 0.45,
        },
        "SQ2": {
            "transcript_text": "Since the climbing hill is unexpectedly steep, I adapt by switching drive motors to low gear and prioritizing the flatter slope because thermal safety is our primary operational bottleneck. We immediately implement the revised navigation path.",
            "duration_seconds": 18.0,
            "words_per_second": 2.2,
            "pause_ratio": 0.15,
        },
        "SQ3": {
            "transcript_text": "In hindsight, we assumed idealized traction on steep terrain. Rather than assuming zero slippage, the general transferable principle for future missions is to always budget a fifteen percent contingency buffer across all motor torque allocations.",
            "duration_seconds": 20.0,
            "words_per_second": 2.1,
            "pause_ratio": 0.16,
        },
    }

    _, report_b = asyncio_run(psde_engine.compute_speaking_assessment_scores(
        session=session_b,
        scenario=test_scenario,
        candidate_responses=resp_b,
    ))
    scores_b = report_b["demonstrated_construct_scores"]

    # In Response B, Adaptability and Reasoning must be significantly higher than Decision Making
    assert scores_b["ADAPTABILITY"]["score"] > scores_b["DECISION_MAKING"]["score"]
    assert scores_b["REASONING"]["score"] > scores_b["DECISION_MAKING"]["score"]

    # Compare Response A vs Response B construct sensitivities
    assert scores_a["DECISION_MAKING"]["score"] > scores_b["DECISION_MAKING"]["score"]
    assert scores_b["ADAPTABILITY"]["score"] > scores_a["ADAPTABILITY"]["score"]
    assert scores_b["REASONING"]["score"] > scores_a["REASONING"]["score"]


def test_4_cross_construct_independence_tests(test_scenario, psde_engine):
    """TEST 7: Cross-Construct Independence (Test A, Test B, Test C, Test D)."""
    base_responses = {
        "SQ1": {"transcript_text": "I will wait.", "duration_seconds": 4.0},
        "SQ2": {"transcript_text": "I will wait.", "duration_seconds": 4.0},
        "SQ3": {"transcript_text": "I will wait.", "duration_seconds": 4.0},
    }

    sess_base = AssessmentSession(session_id="SESS-BASE", candidate_id="CAND-0", scenario_id=test_scenario.scenario_id)
    _, rep_base = asyncio_run(psde_engine.compute_speaking_assessment_scores(sess_base, test_scenario, base_responses))
    base_c = {k: v["score"] for k, v in rep_base["demonstrated_construct_scores"].items()}

    # Test A: Only Decision-Making (SQ1) evidence increases
    resp_dm = dict(base_responses)
    resp_dm["SQ1"] = {
        "transcript_text": "I decisively choose to re-route secondary power to 75% because replacing the pack takes 90 minutes and would violate the strict inspection deadline. Rather than risking total disqualification, this alternative ensures thermal safety.",
        "duration_seconds": 18.0,
    }
    sess_dm = AssessmentSession(session_id="SESS-DM", candidate_id="CAND-DM", scenario_id=test_scenario.scenario_id)
    _, rep_dm = asyncio_run(psde_engine.compute_speaking_assessment_scores(sess_dm, test_scenario, resp_dm))
    dm_c = {k: v["score"] for k, v in rep_dm["demonstrated_construct_scores"].items()}

    assert dm_c["DECISION_MAKING"] > base_c["DECISION_MAKING"]
    # Adaptability and Reasoning must NOT increase because only SQ1 changed
    assert dm_c["ADAPTABILITY"] == base_c["ADAPTABILITY"]
    assert dm_c["REASONING"] == base_c["REASONING"]

    # Test B: Only Adaptability (SQ2) evidence increases
    resp_ad = dict(base_responses)
    resp_ad["SQ2"] = {
        "transcript_text": "Since the hill is unexpectedly steep, I adapt by switching navigation to the flatter path and prioritizing thermal safety because motor load is the primary bottleneck.",
        "duration_seconds": 18.0,
    }
    sess_ad = AssessmentSession(session_id="SESS-AD", candidate_id="CAND-AD", scenario_id=test_scenario.scenario_id)
    _, rep_ad = asyncio_run(psde_engine.compute_speaking_assessment_scores(sess_ad, test_scenario, resp_ad))
    ad_c = {k: v["score"] for k, v in rep_ad["demonstrated_construct_scores"].items()}

    assert ad_c["ADAPTABILITY"] > base_c["ADAPTABILITY"]
    # Reasoning must remain unchanged
    assert ad_c["REASONING"] == base_c["REASONING"]

    # Test C: Only Reflection (SQ3) evidence increases
    resp_re = dict(base_responses)
    resp_re["SQ3"] = {
        "transcript_text": "In hindsight, our assumption on terrain friction was overly optimistic. Rather than assuming ideal traction, the general principle for future missions is to always maintain a 15% safety buffer.",
        "duration_seconds": 18.0,
    }
    sess_re = AssessmentSession(session_id="SESS-RE", candidate_id="CAND-RE", scenario_id=test_scenario.scenario_id)
    _, rep_re = asyncio_run(psde_engine.compute_speaking_assessment_scores(sess_re, test_scenario, resp_re))
    re_c = {k: v["score"] for k, v in rep_re["demonstrated_construct_scores"].items()}

    assert re_c["REASONING"] > base_c["REASONING"]
    # Adaptability must remain unchanged
    assert re_c["ADAPTABILITY"] == base_c["ADAPTABILITY"]


def test_5_mathematical_parity_proof():
    """TEST 10: Verifies (1.5*DM + 1.0*AD + 1.0*RE + 1.0*COM)/4.5 == (SQ1+SQ2+SQ3)/3 mathematical identity."""
    weighting = WeightingEngine()
    test_cases = [
        (85.0, 72.0, 91.0),
        (0.0, 0.0, 0.0),
        (100.0, 100.0, 100.0),
        (45.65, 11.30, 40.65),
        (60.0, 80.0, 70.0),
    ]

    for sq1, sq2, sq3 in test_cases:
        constructs, final_score = weighting.aggregate_speaking_construct_scores(sq1, sq2, sq3)
        dm = constructs["DECISION_MAKING"]
        ad = constructs["ADAPTABILITY"]
        re = constructs["REASONING"]
        com = constructs["COMMUNICATION"]

        weighted_numerator = 1.5 * dm + 1.0 * ad + 1.0 * re + 1.0 * com
        calculated_final = round(weighted_numerator / 4.5, 2)
        arithmetic_mean = round((sq1 + sq2 + sq3) / 3.0, 2)

        assert abs(final_score - arithmetic_mean) <= 0.02
        assert abs(calculated_final - arithmetic_mean) <= 0.02


def asyncio_run(coro):
    import asyncio
    return asyncio.run(coro)
