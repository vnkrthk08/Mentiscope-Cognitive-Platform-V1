import pytest
from app.application.report_engine import (
    AssessmentReportingEngine,
    ExecutiveSummaryGenerator,
    ConstructExplanationGenerator,
    EvidenceTraceabilityBuilder,
    ReliabilityExplanationGenerator,
    ExplainabilityManager,
    ReportFormatter,
    ReportValidator,
)
from app.application.scoring_engine.models import (
    AssessmentScoreSet,
    ConstructScore,
    CompositeScore,
    AssessmentDecision,
    ReliabilitySummary,
)
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.evidence import Evidence
from app.domain.value_objects.confidence_level import ConfidenceLevel
from app.domain.exceptions.report_exceptions import (
    ReportValidationFailure,
    ReportGenerationFailure,
)


def _create_mock_score_set():
    cs1 = ConstructScore("DECISION_MAKING", raw_score=85.0, normalized_score=87.0)
    cs2 = ConstructScore("COMMUNICATION", raw_score=80.0, normalized_score=82.0)
    comp = CompositeScore("OVERALL", score=85.0)
    dec = AssessmentDecision(decision_band="HIGH_COMPETENCY", decision_explanation="Consistently demonstrated risk assessment.")
    rel = ReliabilitySummary(reliability_estimate=0.92, confidence_interval="0.88 - 0.96")

    return AssessmentScoreSet(
        session_id="SESS-AREE-001",
        scenario_id="SCENARIO_LOGISTICS_01",
        construct_scores={"DECISION_MAKING": cs1, "COMMUNICATION": cs2},
        composite_scores={"OVERALL": comp},
        assessment_decision=dec,
        reliability_summary=rel,
    )


def test_summary_and_explanation_generators():
    summary_gen = ExecutiveSummaryGenerator()
    expl_gen = ConstructExplanationGenerator()
    score_set = _create_mock_score_set()

    summary_text = summary_gen.generate_summary(score_set)
    assert "SCENARIO_LOGISTICS_01" in summary_text
    assert "HIGH_COMPETENCY" in summary_text

    sections, strengths, growth = expl_gen.generate_explanations(score_set)
    assert "DECISION_MAKING" in sections
    assert len(strengths) >= 1


def test_traceability_builder_and_reliability_explainer():
    trace_builder = EvidenceTraceabilityBuilder()
    rel_gen = ReliabilityExplanationGenerator()
    score_set = _create_mock_score_set()

    session = AssessmentSession(session_id="SESS-AREE-001", candidate_id="CAND-01", scenario_id="SCENARIO_LOGISTICS_01")
    ev = Evidence(
        session_id="SESS-AREE-001",
        prompt_id="S_P1",
        quote="Our team must prioritize safety protocols.",
        indicator_description="Emergency protocol initiation",
        confidence=ConfidenceLevel(0.95),
    )
    session.add_evidence(ev)

    trace_map = trace_builder.build_traceability_map(session, score_set)
    assert len(trace_map) >= 1
    assert "verbatim_quote" in trace_map[0]

    rel_sec = rel_gen.generate_explanation(score_set)
    assert rel_sec["reliability_estimate"] == 0.92
    assert "EXCELLENT" in rel_sec["quality_rating"]


def test_report_formatter_multi_audience_views():
    formatter = ReportFormatter()
    session = AssessmentSession(session_id="SESS-AREE-001", candidate_id="CAND-01", scenario_id="SCENARIO_LOGISTICS_01")
    score_set = _create_mock_score_set()

    aree = AssessmentReportingEngine()
    import asyncio
    report = asyncio.run(aree.generate_assessment_report(session, score_set))

    assert report.candidate_view is not None
    assert report.candidate_view.decision_band == "HIGH_COMPETENCY"

    assert report.counselor_view is not None
    assert report.research_view is not None
    assert report.research_view.pipeline_version == "1.0.0"

    assert report.administrator_view is not None
    assert report.administrator_view.session_id == "SESS-AREE-001"


@pytest.mark.asyncio
async def test_aree_facade_end_to_end_reporting():
    aree = AssessmentReportingEngine()
    session = AssessmentSession(session_id="SESS-AREE-001", candidate_id="CAND-01", scenario_id="SCENARIO_LOGISTICS_01")
    score_set = _create_mock_score_set()

    report = await aree.generate_assessment_report(session, score_set)

    assert report.session_id == "SESS-AREE-001"
    assert report.scenario_id == "SCENARIO_LOGISTICS_01"
    assert len(report.construct_sections) == 2
    assert len(report.evidence_traceability_map) >= 1
    assert report.candidate_view is not None
    assert report.counselor_view is not None
    assert report.research_view is not None
    assert report.administrator_view is not None
