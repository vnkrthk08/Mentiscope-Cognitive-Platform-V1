import pytest
from app.application.construct_engine import (
    PsychometricConstructEvaluationEngine,
    ConstructRepository,
    ConstructGroupingService,
    ConstructEvaluationCoordinator,
    ConstructEvaluationBuilder,
    ConstructValidator,
    ConstructEvaluationSet,
)
from app.application.evidence_engine.models import (
    BehavioralEvidenceSet,
    BehavioralEvidence,
    BehavioralQuote,
)
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.exceptions.construct_exceptions import (
    BehavioralEvidenceMissing,
    EvaluationValidationFailure,
    PsychometricEvaluationFailure,
)


def _create_mock_evidence_set():
    quote = BehavioralQuote(quote="Our team must prioritize safety protocols.", segment_id=0)
    ev_item = BehavioralEvidence(
        construct="DECISION_MAKING",
        behavior="Prioritized human safety over delays",
        observation="Candidate demonstrated ethical decision making",
        supporting_quote=quote,
        confidence=0.95,
    )
    return BehavioralEvidenceSet(
        session_id="SESS-PCEE-001",
        scenario_id="SCENARIO_LOGISTICS_01",
        prompt_id="S_P1",
        evidence_items=[ev_item],
    )


def test_construct_repository_and_grouping():
    repo = ConstructRepository()
    grouping = ConstructGroupingService()

    defn = repo.get_construct_definition("DECISION_MAKING")
    assert defn["name"] == "Decision Making"

    ev_set = _create_mock_evidence_set()
    grouped = grouping.group_evidence_by_construct(ev_set)
    assert "DECISION_MAKING" in grouped

    summaries = grouping.build_evidence_summaries(grouped)
    assert len(summaries) == 1
    assert summaries[0].evidence_count == 1

    # Missing evidence exception
    empty_ev_set = BehavioralEvidenceSet(session_id="EMPTY", scenario_id="SCENARIO_01")
    with pytest.raises(BehavioralEvidenceMissing):
        grouping.group_evidence_by_construct(empty_ev_set)


def test_construct_validator():
    validator = ConstructValidator()
    ev_set = _create_mock_evidence_set()
    grouping = ConstructGroupingService()
    builder = ConstructEvaluationBuilder()

    from app.infrastructure.prompt_service.result import PromptOrchestrationResult

    mock_apos = PromptOrchestrationResult(
        prompt_id="CONSTRUCT_EVALUATION_PROMPT",
        validated_response={
            "construct_evaluations": [
                {
                    "construct": "DECISION_MAKING",
                    "behavioral_summary": "Prioritized safety protocols under pressure.",
                    "evaluation_narrative": "Consistently applied risk mitigation.",
                    "confidence": 0.95,
                }
            ]
        },
    )

    summaries = grouping.build_evidence_summaries(grouping.group_evidence_by_construct(ev_set))
    eval_set = builder.build_evaluation_set("SESS-PCEE-001", "SCENARIO_01", mock_apos, summaries)

    assert validator.validate_evaluation_set(eval_set) is True


@pytest.mark.asyncio
async def test_pcee_facade_end_to_end_evaluation():
    pcee = PsychometricConstructEvaluationEngine()
    session = AssessmentSession(session_id="SESS-PCEE-001", candidate_id="CAND-01", scenario_id="SCENARIO_LOGISTICS_01")
    ev_set = _create_mock_evidence_set()

    eval_set = await pcee.evaluate_constructs(session, ev_set)

    assert eval_set.session_id == "SESS-PCEE-001"
    assert eval_set.scenario_id == "SCENARIO_LOGISTICS_01"
    assert len(eval_set.construct_evaluations) > 0
    assert eval_set.construct_evaluations[0].construct_name == "DECISION_MAKING"
    assert eval_set.construct_evaluations[0].evaluation_confidence >= 0.90
    assert len(eval_set.assessments) > 0
