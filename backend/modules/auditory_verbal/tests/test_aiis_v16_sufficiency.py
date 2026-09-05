"""
Unit and Integration Test Suite for AIIS v16 — Evidence Sufficiency & Belief Tracking Architecture.
Verifies:
1. Evidence Sufficiency Engine evaluation (WEAK vs STRONG reasoning for Answer A vs Answer B).
2. Priority Score calculation (Priority = Importance x Deficit).
3. Prioritizing strengthening WEAK reasoning before collecting missing secondary dimensions.
4. End-to-end AIIS facade payload containing sufficiency_matrix.
"""

import pytest
from app.application.followup_subsystem.interview_understanding import InterviewUnderstandingEngine, CandidateDecisionData
from app.application.followup_subsystem.memory import InterviewMemory
from app.application.followup_subsystem.evidence_sufficiency_engine import EvidenceSufficiencyEngine, EvidenceLevel
from app.application.followup_subsystem.behavioral_consistency_engine import BehavioralConsistencyEngine
from app.application.followup_subsystem.behavioral_belief_engine import BehavioralBeliefEngine
from app.application.followup_subsystem.decision_gap_prioritization import DecisionGapPrioritizationEngine
from app.application.followup_subsystem.conversation_manager import ConversationState
from app.application.followup_subsystem.facade import AdaptiveInterviewIntelligenceSystem


def test_aiis_v16_answer_a_vs_answer_b_sufficiency():
    engine = EvidenceSufficiencyEngine()
    memory = InterviewMemory(session_id="test_v16")

    # Answer A: Superficial / weak reasoning ("because it felt right")
    dec_a = CandidateDecisionData(action="Option A", reason="felt right")
    suff_a = engine.evaluate_sufficiency(dec_a, memory, "I chose Option A because it felt right.")

    assert suff_a["Reason"].level == EvidenceLevel.WEAK
    assert suff_a["Reason"].score < 0.50
    assert suff_a["Reason"].deficit > 0.50

    # Answer B: Detailed / strong reasoning ("minimized safety risks, reduced costs, allowed team to finish before deadline")
    dec_b = CandidateDecisionData(
        action="Option A",
        reason="Minimized safety risks, reduced costs, finished before deadline",
        risks=["Safety risks"],
        tradeoffs=["Cost"],
    )
    suff_b = engine.evaluate_sufficiency(dec_b, memory, "I chose Option A because it minimized safety risks, reduced costs, and allowed the team to finish before the deadline.")

    assert suff_b["Reason"].level in (EvidenceLevel.STRONG, EvidenceLevel.SATURATED)
    assert suff_b["Reason"].score >= 0.75
    assert suff_b["Reason"].deficit <= 0.25


def test_aiis_v16_priority_calculation():
    engine = EvidenceSufficiencyEngine()
    prioritizer = DecisionGapPrioritizationEngine()
    memory = InterviewMemory(session_id="test_v16")
    state = ConversationState(session_id="test_v16")

    # Candidate with WEAK reasoning (Answer A)
    dec_a = CandidateDecisionData(action="Option A", reason="felt right")
    suff_a = engine.evaluate_sufficiency(dec_a, memory, "I chose Option A because it felt right.")

    c_engine = BehavioralConsistencyEngine()
    obs = c_engine.evaluate_consistency("Reason", dec_a, memory, "Science Exhibition", "I chose Option A because it felt right.", 1)
    b_engine = BehavioralBeliefEngine()
    beliefs = b_engine.evaluate_beliefs({"Reason": obs}, {}, turn_number=1)

    needs = prioritizer.prioritize_gaps(suff_a, beliefs, state)
    assert len(needs) > 0
    assert needs[0].objective in ("ASK_REASON", "CONFIRM_BELIEF")


@pytest.mark.asyncio
async def test_aiis_v16_end_to_end_sufficiency_matrix():
    aiis = AdaptiveInterviewIntelligenceSystem()

    response = await aiis.generate_followup_question(
        scenario_title="Coding Competition Algorithm Limit",
        transcript_text="I would stop the execution immediately because it felt right.",
        target_construct="DECISION_MAKING",
        session_id="v16_e2e_sess",
    )

    assert "sufficiency_matrix" in response
    matrix = response["sufficiency_matrix"]
    assert "Reason" in matrix
    assert "score" in matrix["Reason"]
    assert "level" in matrix["Reason"]
    assert matrix["Reason"]["level"] == "WEAK"
    assert response["intent"] in ("ASK_REASON", "CONFIRM_BELIEF")
