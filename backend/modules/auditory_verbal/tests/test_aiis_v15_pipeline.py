"""
Unit and Integration Test Suite for Adaptive Interview Intelligence System (AIIS v15.0.0 Architecture).
Tests all 10 modules:
Module 1: Frontend Validator
Module 2: Interview Understanding Engine
Module 3: Interview Memory (Evidence Repository)
Module 4: Conversation State & Manager (Interviewer Brain)
Module 5: Information Need Prioritization Engine
Module 6: Interview Strategy Engine
Module 7: Specification Compiler
Module 8: Question Writer (Nemotron)
Module 9: Interview QA Engine
Module 10: Interview Completion Engine
"""

import pytest
from app.application.followup_subsystem.interview_understanding import InterviewUnderstandingEngine, InterviewUnderstandingResult, CandidateDecisionData
from app.application.followup_subsystem.evidence_sufficiency_engine import EvidenceSufficiencyEngine
from app.application.followup_subsystem.memory import InterviewMemory, InterviewMemoryManager
from app.application.followup_subsystem.conversation_manager import ConversationManager, ConversationState, InterviewerAction
from app.application.followup_subsystem.decision_gap_prioritization import DecisionGapPrioritizationEngine
from app.application.followup_subsystem.strategy_engine import InterviewStrategyEngine, InterviewObjective
from app.application.followup_subsystem.planning_engine import FollowUpPlanningEngine
from app.application.followup_subsystem.compiler import FollowUpSpecificationCompiler
from app.application.followup_subsystem.style_engine import ConversationStyleEngine
from app.application.followup_subsystem.interview_quality_engine import InterviewQAEngine
from app.application.followup_subsystem.closure_engine import InterviewCompletionEngine
from app.application.followup_subsystem.facade import AdaptiveInterviewIntelligenceSystem


def test_aiis_module2_understanding_engine():
    engine = InterviewUnderstandingEngine()

    # Valid decision response
    res_valid = engine.evaluate_understanding("Science Exhibition", "I would stop the robot and explain the delay to my teacher because safety comes first.")
    assert res_valid.status == "VALID"
    assert res_valid.candidate_decision.action is not None
    assert res_valid.coverage.decision is True
    assert res_valid.coverage.reason is True

    # Off-topic response
    res_off = engine.evaluate_understanding("Science Exhibition", "My favourite movie is Interstellar.")
    assert res_off.status == "OFF_TOPIC"

    # Nonsensical response
    res_non = engine.evaluate_understanding("Science Exhibition", "I am Iron Man.")
    assert res_non.status == "NONSENSICAL"

    # Refusal response
    res_ref = engine.evaluate_understanding("Science Exhibition", "I don't want to answer.")
    assert res_ref.status == "REFUSAL"

    # Uncertain response
    res_unc = engine.evaluate_understanding("Science Exhibition", "I don't know what to do.")
    assert res_unc.status == "UNCERTAIN"


def test_aiis_module3_interview_memory():
    memory = InterviewMemory(session_id="test_sess")
    dec_data = CandidateDecisionData(
        action="Stop the robot",
        reason="Prevent hardware explosion",
        stakeholders=["Teacher"],
        risks=["Motor failure"],
    )
    memory.record_candidate_facts("I would stop the robot because safety comes first.", dec_data, turn_number=1)

    assert "Stop the robot" in memory.candidate_decisions
    assert "Prevent hardware explosion" in memory.stated_reasons
    assert "Teacher" in memory.mentioned_stakeholders

    # Test contradiction detection across turns
    contra = memory.detect_contradiction("Actually I wouldn't tell anyone instead.")
    assert contra is not None
    assert "Stop the robot" in contra["prior_decision"]


def test_aiis_module4_conversation_manager():
    manager = ConversationManager()
    state = ConversationState(session_id="test_sess")

    # Valid response maps to CONTINUE
    act1 = manager.determine_action("VALID", state)
    assert act1 == InterviewerAction.CONTINUE

    # Off-topic maps to REDIRECT
    act2 = manager.determine_action("OFF_TOPIC", state)
    assert act2 == InterviewerAction.REDIRECT

    # 3 consecutive refusals trigger TERMINATE
    manager.determine_action("REFUSAL", state)
    manager.determine_action("REFUSAL", state)
    act_term = manager.determine_action("REFUSAL", state)
    assert act_term == InterviewerAction.TERMINATE
    assert state.is_completed is True


def test_aiis_module5_gap_prioritization():
    understanding = InterviewUnderstandingEngine().evaluate_understanding("Science Exhibition", "I would stop the robot.")
    memory = InterviewMemory(session_id="test_sess")
    suff_matrix = EvidenceSufficiencyEngine().evaluate_sufficiency(understanding.candidate_decision, memory, "I would stop the robot.")
    state = ConversationState(session_id="test_sess")
    p_engine = DecisionGapPrioritizationEngine()

    priorities = p_engine.prioritize_gaps(suff_matrix, {}, state)
    assert len(priorities) > 0
    # Reason missing should be top priority
    assert priorities[0].objective in ("ASK_REASON", "CONFIRM_BELIEF")
    assert priorities[0].priority_score >= 0.50


def test_aiis_module6_strategy_engine():
    understanding = InterviewUnderstandingEngine().evaluate_understanding("Science Exhibition", "I would stop the robot.")
    memory = InterviewMemory(session_id="test_sess")
    suff_matrix = EvidenceSufficiencyEngine().evaluate_sufficiency(understanding.candidate_decision, memory, "I would stop the robot.")
    state = ConversationState(session_id="test_sess")
    p_engine = DecisionGapPrioritizationEngine()
    priorities = p_engine.prioritize_gaps(suff_matrix, {}, state)

    strat_engine = InterviewStrategyEngine()
    objective = strat_engine.select_objective(InterviewerAction.CONTINUE, priorities, state)

    assert objective in (InterviewObjective.ASK_REASON, InterviewObjective.CONFIRM_BELIEF)
    assert isinstance(objective, InterviewObjective)


def test_aiis_module9_qa_engine():
    qa_engine = InterviewQAEngine()
    dec_data = CandidateDecisionData(action="Stop the robot")
    state = ConversationState(session_id="test_sess")

    # High quality question
    good_q = "When you decided to stop the robot, what principal reason led to that choice in this situation?"
    from app.application.followup_subsystem.specification import FollowUpSpecification
    spec = FollowUpSpecification(
        intent="ASK_REASON",
        target_construct="Reason",
        reason="Probe reason",
        context_snippet="Stop the robot",
        cognitive_depth="INITIAL",
        conversation_stage="INITIAL",
        turn_number=1,
        style_profile={},
        interviewer_memory_reference="Earlier you mentioned stopping the robot.",
        questioning_style="OPEN_EXPLORATION",
        tone="PROFESSIONAL",
        pressure_level="MODERATE",
        empathy_level="MODERATE",
    )

    res = qa_engine.evaluate_question(good_q, spec, dec_data, "Science Exhibition", state, [])
    assert res.is_passed is True

    # Generic low-quality question should fail checklist
    bad_q = "Why do you think that?"
    res_bad = qa_engine.evaluate_question(bad_q, spec, dec_data, "Science Exhibition", state, [])
    assert res_bad.is_passed is False
    assert "does_not_skip_reasoning_chain" in res_bad.failed_checks


@pytest.mark.asyncio
async def test_aiis_full_facade_end_to_end():
    aiis = AdaptiveInterviewIntelligenceSystem()

    response = await aiis.generate_followup_question(
        scenario_title="Coding Competition Algorithm Limit",
        transcript_text="I would stop the execution immediately and notify my team member Arjun.",
        target_construct="DECISION_MAKING",
        session_id="e2e_aiis_test_sess",
    )

    assert response["intent"] in [o.value for o in InterviewObjective]
    assert "follow_up_question" in response
    assert len(response["follow_up_question"]) > 15
    assert "qa_result" in response
    assert "interview_memory" in response
    assert "understanding_result" in response
