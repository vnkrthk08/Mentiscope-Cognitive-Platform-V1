"""
Test Suite: test_aiis_v20_1_dialogue_intelligence.py
Verifies AIIS v20.1 Dialogue Intelligence Architecture.
"""

import pytest
from app.application.followup_subsystem import (
    AdaptiveInterviewIntelligenceSystem,
    InterviewWorldModel,
    IntentUnderstandingEngine,
    CandidateIntent,
    InterviewController,
    InterviewMode,
    CandidateReadiness,
    QuestionDifficulty,
    InformationGainEngine,
    DialoguePlanner,
    InterviewMove,
    ConversationFlowEngine,
    DialogueEditor,
)


@pytest.fixture
def aiis_system():
    return AdaptiveInterviewIntelligenceSystem()


def test_intent_understanding_engine_perception():
    engine = IntentUnderstandingEngine()

    # Clear decision
    res1 = engine.evaluate_intent(
        "I would stop the robot execution immediately because safety is our highest priority.",
        turn_number=1
    )
    assert res1.candidate_intent == CandidateIntent.CLEAR_DECISION
    assert res1.decision_confidence >= 0.80
    assert not res1.needs_clarification

    # Misunderstanding / Help
    res2 = engine.evaluate_intent("What should I do? I don't understand the question.", turn_number=1)
    assert res2.candidate_intent in (CandidateIntent.ASKING_FOR_HELP, CandidateIntent.MISUNDERSTANDING)
    assert res2.decision_confidence < 0.40
    assert res2.needs_clarification


def test_interview_controller_policy_generation():
    intent_engine = IntentUnderstandingEngine()
    controller = InterviewController()

    intent_clear = intent_engine.evaluate_intent("I would pause execution because safety matters most.", 1)
    policy_clear = controller.evaluate_policy(intent_clear, overall_uncertainty=0.60, turn_number=1)

    assert policy_clear.mode == InterviewMode.PROBE_MODE
    assert policy_clear.readiness in (CandidateReadiness.MEDIUM, CandidateReadiness.HIGH)

    intent_help = intent_engine.evaluate_intent("Help me, what question?", 1)
    policy_guidance = controller.evaluate_policy(intent_help, overall_uncertainty=0.60, turn_number=1)

    assert policy_guidance.mode == InterviewMode.GUIDANCE_MODE
    assert policy_guidance.need_clarification


def test_information_gain_engine_expected_reduction():
    gain_engine = InformationGainEngine()
    world_model = InterviewWorldModel(session_id="test_wm", scenario_title="Test Scenario")

    res = gain_engine.compute_information_gain(world_model)
    assert res.recommended_dimension in res.expected_gain_matrix
    assert res.highest_gain_score > 0.0


def test_dialogue_planner_pure_semantic_act():
    planner = DialoguePlanner()
    intent_engine = IntentUnderstandingEngine()
    controller = InterviewController()

    intent_clear = intent_engine.evaluate_intent("I would stop the robot execution immediately.", 1)
    policy = controller.evaluate_policy(intent_clear, 0.60, 1)

    act = planner.plan_dialogue_act(
        objective="ASK_RISK",
        policy=policy,
        candidate_summary="Candidate stopped execution for safety.",
        target_dimension="Risk",
    )

    assert act.interview_move in (InterviewMove.EXPLORE, InterviewMove.CHALLENGE, InterviewMove.CLARIFY)
    assert act.uncertainty_target == "risk_uncertainty"


def test_dialogue_editor_template_rotation():
    editor = DialogueEditor()
    raw_text = "Regarding your choice to 'stop execution', what risks did you consider?"
    summary = "Candidate chose to stop execution."

    res = editor.edit_dialogue(raw_text, summary, "Risk", used_openings=[])

    assert "regarding your choice to" not in res.edited_question_text.lower()
    assert res.opening_template_used in editor.OPENING_TEMPLATES


@pytest.mark.asyncio
async def test_v20_1_end_to_end_facade_trace(aiis_system):
    response = await aiis_system.generate_followup_question(
        scenario_title="AI Robotics Emergency Stop",
        transcript_text="I would stop the robot execution immediately and inform Arjun because safety is our priority.",
        target_construct="LEADERSHIP",
        session_id="v20_1_test_session",
    )

    assert "world_model" in response
    assert "intent_result" in response
    assert "interview_policy" in response
    assert "information_gain" in response
    assert "dialogue_act" in response
    assert "flow_decision" in response
    assert "dialogue_editor" in response
    assert "question_text" in response
    assert len(response["question_text"]) > 10


def test_dual_objective_rejection():
    from app.application.followup_subsystem.interview_quality_engine import InterviewQAEngine
    from app.application.followup_subsystem.specification import FollowUpSpecification
    from app.application.followup_subsystem.interview_understanding import CandidateDecisionData
    from app.application.followup_subsystem.conversation_manager import ConversationState

    qa_engine = InterviewQAEngine()
    spec = FollowUpSpecification.from_dict({"intent": "ASK_RISK"})
    decision = CandidateDecisionData(action="stop robot")
    state = ConversationState(session_id="test_qa")

    # Dual objective with 'or' across distinct dimensions should fail check #3
    res_dual = qa_engine.evaluate_question(
        question_text="Was your primary concern safety or speed when you made this decision?",
        spec=spec,
        decision_data=decision,
        scenario_title="Test Scenario",
        state=state,
        previous_questions=[],
    )
    assert not res_dual.is_passed
    assert "exactly_one_objective" in res_dual.failed_checks

    # Single objective with aligned intent should pass check #3
    res_single = qa_engine.evaluate_question(
        question_text="What specific risk were you aiming to avoid when stopping the robot?",
        spec=spec,
        decision_data=decision,
        scenario_title="Test Scenario",
        state=state,
        previous_questions=[],
    )
    assert res_single.exactly_one_objective


@pytest.mark.asyncio
async def test_facade_passes_prioritized_needs_to_strategy_engine(aiis_system):
    """Assert facade.py calls prioritization_engine.prioritize_gaps and passes non-empty needs to strategy_engine."""
    from unittest.mock import MagicMock

    original_select_obj = aiis_system.strategy_engine.select_objective
    captured_prioritized_needs = []

    def spy_select_objective(action, prioritized_needs, state, *args, **kwargs):
        captured_prioritized_needs.extend(prioritized_needs)
        return original_select_obj(action, prioritized_needs, state, *args, **kwargs)

    aiis_system.strategy_engine.select_objective = spy_select_objective

    res = await aiis_system.generate_followup_question(
        scenario_title="AI Robotics Emergency Stop",
        transcript_text="I would stop the robot execution immediately because safety is our priority.",
        target_construct="SAFETY_AWARENESS",
        session_id="test_facade_prioritization_spy",
    )

    assert len(captured_prioritized_needs) > 0
    assert captured_prioritized_needs[0].priority_score > 0.0
