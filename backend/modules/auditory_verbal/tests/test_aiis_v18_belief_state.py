"""
Unit and Integration Test Suite for AIIS v18 — Behavioral Belief State & Hypothesis-Driven Interviewing Architecture.
Verifies:
1. BehavioralConsistencyEngine principle extraction & state classification.
2. BehavioralBeliefEngine Bayesian-style belief confidence updates & status progression.
3. Contradictions setting BeliefStatus.UNCERTAIN and needs_verification = True.
4. Strategy & Prioritization selecting CONFIRM_BELIEF & VERIFY_CONTEXT objectives.
5. End-to-end facade response containing beliefs_matrix payload.
"""

import pytest
from app.application.followup_subsystem.interview_understanding import InterviewUnderstandingEngine, CandidateDecisionData
from app.application.followup_subsystem.memory import InterviewMemory
from app.application.followup_subsystem.behavioral_consistency_engine import BehavioralConsistencyEngine, BehaviorState
from app.application.followup_subsystem.behavioral_belief_engine import BehavioralBeliefEngine, BehaviorBelief, BeliefStatus
from app.application.followup_subsystem.evidence_sufficiency_engine import EvidenceSufficiencyEngine
from app.application.followup_subsystem.decision_gap_prioritization import DecisionGapPrioritizationEngine
from app.application.followup_subsystem.strategy_engine import InterviewStrategyEngine, InterviewObjective
from app.application.followup_subsystem.conversation_manager import ConversationState, InterviewerAction
from app.application.followup_subsystem.facade import AdaptiveInterviewIntelligenceSystem


def test_aiis_v18_consistency_engine():
    engine = BehavioralConsistencyEngine()
    memory = InterviewMemory(session_id="test_v18")
    dec = CandidateDecisionData(action="Stop the robot", reason="Ensure safety")

    obs1 = engine.evaluate_consistency("Reason", dec, memory, "Science Exhibition", "I would stop the robot to ensure safety.", 1)
    assert obs1.behavior_state == BehaviorState.CONSISTENT
    assert "Safety" in obs1.behavior_principle

    memory.record_behavior_principle(obs1.behavior_principle)

    # Contextual shift under time pressure
    dec2 = CandidateDecisionData(action="Act independently", reason="Time deadline")
    obs2 = engine.evaluate_consistency("Reason", dec2, memory, "Science Exhibition", "I changed my mind because time was running out.", 2)
    assert obs2.behavior_state == BehaviorState.CONTEXTUAL_SHIFT
    assert obs2.explanation is not None


def test_aiis_v18_belief_engine_progression():
    consistency_eng = BehavioralConsistencyEngine()
    belief_eng = BehavioralBeliefEngine()
    memory = InterviewMemory(session_id="test_v18")

    dec = CandidateDecisionData(action="Stop the robot", reason="Ensure safety")
    obs1 = consistency_eng.evaluate_consistency("Reason", dec, memory, "Science Exhibition", "I would stop the robot to ensure safety.", 1)

    beliefs = belief_eng.evaluate_beliefs({"Reason": obs1}, {}, turn_number=1)
    assert "Reason" in beliefs
    b_reason = beliefs["Reason"]

    assert b_reason.supporting_evidence_count == 1
    assert b_reason.confidence > 0.30
    assert b_reason.status in (BeliefStatus.EMERGING, BeliefStatus.LIKELY)

    # Simulate 3 consecutive consistent turns to reach VERIFIED status
    beliefs = belief_eng.evaluate_beliefs({"Reason": obs1}, beliefs, turn_number=2)
    beliefs = belief_eng.evaluate_beliefs({"Reason": obs1}, beliefs, turn_number=3)
    b_reason_updated = beliefs["Reason"]

    assert b_reason_updated.supporting_evidence_count == 3
    assert b_reason_updated.confidence >= 0.70


def test_aiis_v18_belief_contradiction_uncertainty():
    consistency_eng = BehavioralConsistencyEngine()
    belief_eng = BehavioralBeliefEngine()
    memory = InterviewMemory(session_id="test_v18")

    dec = CandidateDecisionData(action="Stop the robot")
    obs_contra = consistency_eng.evaluate_consistency("Reason", dec, memory, "Science Exhibition", "I changed my mind instead.", 2)
    obs_contra = type(obs_contra)(
        dimension=obs_contra.dimension,
        behavior_principle=obs_contra.behavior_principle,
        scenario_context=obs_contra.scenario_context,
        candidate_quote=obs_contra.candidate_quote,
        explanation=obs_contra.explanation,
        quality_score=obs_contra.quality_score,
        confidence_score=obs_contra.confidence_score,
        behavior_state=BehaviorState.CONTRADICTION,
        turn_number=2,
    )

    beliefs = belief_eng.evaluate_beliefs({"Reason": obs_contra}, {}, turn_number=2)
    b_reason = beliefs["Reason"]

    assert b_reason.status == BeliefStatus.UNCERTAIN
    assert b_reason.needs_verification is True


def test_aiis_v18_prioritization_and_strategy():
    prioritizer = DecisionGapPrioritizationEngine()
    strat_engine = InterviewStrategyEngine()
    state = ConversationState(session_id="test_v18")

    # Belief requiring verification
    belief_uncertain = BehaviorBelief(
        id="belief_reason",
        dimension="Reason",
        statement="Candidate principle",
        confidence=0.40,
        status=BeliefStatus.UNCERTAIN,
        needs_verification=True,
    )

    suff_engine = EvidenceSufficiencyEngine()
    memory = InterviewMemory(session_id="test_v18")
    dec = CandidateDecisionData(action="Stop the robot")
    suff_matrix = suff_engine.evaluate_sufficiency(dec, memory, "Stop the robot")

    needs = prioritizer.prioritize_gaps(suff_matrix, {"Reason": belief_uncertain}, state)
    assert len(needs) > 0
    assert needs[0].objective == "VERIFY_CONTEXT"

    obj = strat_engine.select_objective(InterviewerAction.CONTINUE, needs, state)
    assert obj in (InterviewObjective.VERIFY_CONTEXT, InterviewObjective.CONFIRM_BELIEF, InterviewObjective.ASK_REASON)


@pytest.mark.asyncio
async def test_aiis_v18_end_to_end_beliefs_matrix():
    aiis = AdaptiveInterviewIntelligenceSystem()

    response = await aiis.generate_followup_question(
        scenario_title="Coding Competition Algorithm Limit",
        transcript_text="I would stop the execution immediately to ensure safety.",
        target_construct="DECISION_MAKING",
        session_id="v18_e2e_sess",
    )

    assert "beliefs_matrix" in response
    b_matrix = response["beliefs_matrix"]
    assert "Reason" in b_matrix
    assert "confidence" in b_matrix["Reason"]
    assert "status" in b_matrix["Reason"]
    assert b_matrix["Reason"]["status"] in [s.value for s in BeliefStatus]
