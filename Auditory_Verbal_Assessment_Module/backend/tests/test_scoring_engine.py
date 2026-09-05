import pytest
from app.application.scoring_engine import (
    PsychometricScoringDecisionEngine,
    ConstructScoreCalculator,
    ScoreNormalizer,
    CalibrationEngine,
    WeightingEngine,
    ReliabilityEstimator,
    DecisionEngine,
    AssessmentScoreBuilder,
    ScoreValidator,
)
from app.application.construct_engine.models import (
    ConstructEvaluationSet,
    ConstructEvaluation,
)
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.exceptions.scoring_exceptions import (
    NormalizationFailure,
    AssessmentScoreValidationFailure,
    ScoringFailure,
)


def _create_mock_eval_set():
    e1 = ConstructEvaluation(
        construct_name="DECISION_MAKING",
        behavioral_summary="Prioritized safety protocols under risk.",
        evaluation_confidence=0.95,
    )
    e2 = ConstructEvaluation(
        construct_name="COMMUNICATION",
        behavioral_summary="Communicated clearly in sequential manner.",
        evaluation_confidence=0.92,
    )
    return ConstructEvaluationSet(
        session_id="SESS-PSDE-001",
        scenario_id="SCENARIO_LOGISTICS_01",
        construct_evaluations=[e1, e2],
    )


def test_score_calculator_and_normalizer():
    calc = ConstructScoreCalculator()
    norm = ScoreNormalizer()
    eval_set = _create_mock_eval_set()

    raw = calc.calculate_raw_scores(eval_set)
    assert raw["DECISION_MAKING"] > 80.0
    assert raw["COMMUNICATION"] > 80.0

    scores_100 = norm.normalize_scores(raw, scale_type="SCALE_100")
    assert scores_100["DECISION_MAKING"] == raw["DECISION_MAKING"]

    z_scores = norm.normalize_scores(raw, scale_type="Z_SCORE")
    assert z_scores["DECISION_MAKING"] > 0.0

    # Normalization out of bounds exception
    with pytest.raises(NormalizationFailure):
        norm.normalize_scores({"INVALID": 150.0})


def test_calibration_and_weighting_engine():
    cal = CalibrationEngine()
    weighting = WeightingEngine()

    norm_scores = {"DECISION_MAKING": 85.0, "COMMUNICATION": 80.0}
    cal_scores = cal.calibrate_scores(norm_scores)
    assert cal_scores["DECISION_MAKING"] == 87.0

    weights, comp = weighting.compute_weighted_composite(cal_scores)
    assert "DECISION_MAKING" in weights
    assert comp.score > 80.0


def test_reliability_and_decision_engine():
    rel_estimator = ReliabilityEstimator()
    dec_engine = DecisionEngine()
    weighting = WeightingEngine()

    rel = rel_estimator.estimate_reliability(items_count=3)
    assert rel.reliability_estimate >= 0.85
    assert "0." in rel.confidence_interval

    norm_scores = {"DECISION_MAKING": 85.0, "COMMUNICATION": 80.0}
    _, comp = weighting.compute_weighted_composite(norm_scores)
    decision = dec_engine.generate_decision(comp)

    assert decision.decision_band == "HIGH_COMPETENCY"
    assert len(decision.risk_flags) == 0


@pytest.mark.asyncio
async def test_psde_facade_end_to_end_scoring():
    psde = PsychometricScoringDecisionEngine()
    session = AssessmentSession(session_id="SESS-PSDE-001", candidate_id="CAND-01", scenario_id="SCENARIO_LOGISTICS_01")
    eval_set = _create_mock_eval_set()

    score_set = await psde.compute_assessment_scores(session, eval_set)

    assert score_set.session_id == "SESS-PSDE-001"
    assert score_set.scenario_id == "SCENARIO_LOGISTICS_01"
    assert "DECISION_MAKING" in score_set.construct_scores
    assert score_set.composite_scores["OVERALL"].score > 80.0
    assert score_set.assessment_decision.decision_band == "HIGH_COMPETENCY"
    assert "DECISION_MAKING" in session.metadata["overall_construct_scores"]  # Registered in session metadata
