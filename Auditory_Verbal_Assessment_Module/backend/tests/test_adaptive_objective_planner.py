"""
Unit tests for Stage 4: Follow-up Objective Planner.

Covers all 9 required test scenarios plus the rank_key tie-break case
and the no-intersection fallback path.
"""

import pytest
from app.application.followup_subsystem.session_state import (
    FollowUpSessionState,
    EvidenceLogEntry,
)
from app.application.followup_subsystem.adaptive_objective_planner import (
    AdaptiveObjectivePlanner,
    FollowUpObjectiveDecision,
    rank_key,
    DEFAULT_MAX_FOLLOWUP_TURNS,
)


def _make_state(
    primary=None,
    secondary=None,
    evidence_log=None,
    followup_history=None,
):
    """Helper to build a FollowUpSessionState with custom construct lists."""
    state = FollowUpSessionState(
        scenario_id="TEST-SCEN",
        candidate_id="TEST-CAND",
        primary_constructs=primary or ["DECISION_MAKING", "REASONING"],
        secondary_constructs=secondary or ["COMMUNICATION", "ATTENTION"],
    )
    if evidence_log:
        state.evidence_log = evidence_log
    if followup_history:
        state.followup_history = followup_history
    return state


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: Tie-Break Determinism (§1 from design spec)
#
# Two constructs with identical confidence and status. The one declared
# earlier in primary_constructs must win via declared_order_index.
# ═══════════════════════════════════════════════════════════════════════════════
def test_tiebreak_determinism_by_declared_order():
    """
    REASONING and DECISION_MAKING both at confidence=0.25, status=weak.
    primary_constructs declares REASONING first → REASONING must win.
    """
    state = _make_state(primary=["REASONING", "DECISION_MAKING"])
    planner = AdaptiveObjectivePlanner()

    primary_gaps = [
        {"construct": "DECISION_MAKING", "confidence": 0.25, "status": "weak"},
        {"construct": "REASONING", "confidence": 0.25, "status": "weak"},
    ]

    decision = planner.plan_objective(state, primary_gaps, [])

    assert decision.target_constructs[0] == "REASONING"
    assert not decision.is_terminate


def test_rank_key_function_directly():
    """Verify rank_key returns correct tuple for deterministic sorting."""
    # missing (status_priority=2) should rank before weak (status_priority=1)
    # at same confidence
    k_missing = rank_key("A", 0.0, "missing", 0)
    k_weak = rank_key("B", 0.0, "weak", 0)
    assert k_missing < k_weak  # -2 < -1 in second position

    # Same confidence + status: lower declared index wins
    k_first = rank_key("A", 0.25, "weak", 0)
    k_second = rank_key("B", 0.25, "weak", 1)
    assert k_first < k_second


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: Disjoint Objectives Fallback (§3 no-intersection path)
#
# Two primary gaps whose candidate objective sets have ZERO intersection.
# Must fall back to single-construct targeting with explicit rationale.
# ═══════════════════════════════════════════════════════════════════════════════
def test_disjoint_objectives_fallback_to_single_construct():
    """
    ETHICAL_REASONING objectives: [ethical_challenge]
    ADAPTABILITY objectives: [failure_recovery]
    No overlap → fallback to single-construct targeting of ETHICAL_REASONING.
    """
    state = _make_state(primary=["ETHICAL_REASONING", "ADAPTABILITY"])
    planner = AdaptiveObjectivePlanner()

    primary_gaps = [
        {"construct": "ETHICAL_REASONING", "confidence": 0.0, "status": "missing"},
        {"construct": "ADAPTABILITY", "confidence": 0.0, "status": "missing"},
    ]

    decision = planner.plan_objective(state, primary_gaps, [])

    assert decision.target_constructs == ["ETHICAL_REASONING"]
    assert decision.objective == "ethical_challenge"
    assert "no shared objective" in decision.reason
    assert "falling back to single-construct" in decision.reason
    assert not decision.is_terminate


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: Objective Exhaustion Escalation
#
# Top-ranked construct's candidate objectives are fully exhausted.
# Planner must escalate to the 2nd-ranked construct.
# ═══════════════════════════════════════════════════════════════════════════════
def test_objective_exhaustion_escalates_to_next_construct():
    """
    DECISION_MAKING objectives: [trade_off_analysis, priority_shift, risk_assessment]
    All exhausted. REASONING objectives: [trade_off_analysis, reasoning_probe]
    trade_off_analysis is also exhausted, but reasoning_probe is not.
    Must escalate to REASONING and pick reasoning_probe.
    """
    state = _make_state(
        primary=["DECISION_MAKING", "REASONING"],
        followup_history=[
            {"objective": "trade_off_analysis"},
            {"objective": "priority_shift"},
            {"objective": "risk_assessment"},
        ],
    )
    planner = AdaptiveObjectivePlanner()

    primary_gaps = [
        {"construct": "DECISION_MAKING", "confidence": 0.25, "status": "weak"},
        {"construct": "REASONING", "confidence": 0.25, "status": "weak"},
    ]

    decision = planner.plan_objective(state, primary_gaps, [])

    assert decision.objective == "reasoning_probe"
    assert "REASONING" in decision.target_constructs
    assert "escalated" in decision.reason
    assert not decision.is_terminate


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: All Gaps Sufficient Termination
#
# primary_gaps and secondary_gaps both empty → session termination.
# ═══════════════════════════════════════════════════════════════════════════════
def test_all_gaps_sufficient_terminates():
    state = _make_state()
    planner = AdaptiveObjectivePlanner()

    decision = planner.plan_objective(state, [], [])

    assert decision.is_terminate is True
    assert "sufficient" in decision.termination_reason.lower()
    assert decision.objective == ""


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 5: Turn Cap Reached Termination
#
# turn_number >= max_followup_turns → forced termination regardless of gaps.
# ═══════════════════════════════════════════════════════════════════════════════
def test_turn_cap_reached_terminates():
    state = _make_state()
    planner = AdaptiveObjectivePlanner(max_followup_turns=3)

    primary_gaps = [
        {"construct": "DECISION_MAKING", "confidence": 0.25, "status": "weak"},
    ]

    decision = planner.plan_objective(state, primary_gaps, [], turn_number=3)

    assert decision.is_terminate is True
    assert "Max turn cap reached" in decision.termination_reason
    assert decision.objective == ""


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 6: Contradiction Signal Pre-emption
#
# Non-empty contradictions in latest evidence_log entry → contradiction_detection
# pre-empts normal gap ranking.
# ═══════════════════════════════════════════════════════════════════════════════
def test_contradiction_signal_preempts_ranking():
    entry = EvidenceLogEntry(
        turn=2,
        source="followup_1",
        claims=["I chose option A", "Actually I prefer option B"],
        contradictions=["Previously claimed option A but now says option B"],
    )
    state = _make_state(evidence_log=[entry])
    planner = AdaptiveObjectivePlanner()

    primary_gaps = [
        {"construct": "DECISION_MAKING", "confidence": 0.25, "status": "weak"},
    ]

    decision = planner.plan_objective(state, primary_gaps, [])

    assert decision.objective == "contradiction_detection"
    assert "Contradiction detected" in decision.reason
    assert not decision.is_terminate


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 7: Heavy Hedging Signal Trigger
#
# len(hedges) >= 2 in latest evidence → confidence_verification fires.
# ═══════════════════════════════════════════════════════════════════════════════
def test_heavy_hedging_triggers_confidence_verification():
    entry = EvidenceLogEntry(
        turn=1,
        source="initial_response",
        claims=["I think maybe we should try option A"],
        hedges=["I think", "maybe", "probably"],
    )
    state = _make_state(evidence_log=[entry])
    planner = AdaptiveObjectivePlanner()

    primary_gaps = [
        {"construct": "REASONING", "confidence": 0.25, "status": "weak"},
    ]

    decision = planner.plan_objective(state, primary_gaps, [])

    assert decision.objective == "confidence_verification"
    assert "hedging" in decision.reason.lower()
    assert not decision.is_terminate


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 8: Stage 2 Dependency Check Fixture
#
# This test verifies Stage 4's ranking determinism under the Stage 2 contract
# using synthetic, controlled evidence-indexed construct_coverage input.
# It does NOT validate that Stage 2's runtime implementation produces
# evidence-indexed coverage — that remains a separate, still-open upstream
# verification task outside Stage 4's test suite.
# ═══════════════════════════════════════════════════════════════════════════════
def test_stage2_dependency_evidence_indexed_ranking():
    """
    Stage 2 dependency check fixture.

    Verifies that Stage 4 ranking produces correct results when given
    evidence-indexed confidence values (where only the construct whose
    behavioral indicators were matched gets an increment, not all
    constructs uniformly).

    This fixture does NOT validate Stage 2's real output — it validates
    Stage 4's behavior given the expected Stage 2 contract.
    """
    state = _make_state(primary=["DECISION_MAKING", "REASONING", "COMMUNICATION"])
    planner = AdaptiveObjectivePlanner()

    # Simulate evidence-indexed coverage: REASONING got evidence (0.5),
    # DECISION_MAKING did not (0.0), COMMUNICATION partially (0.25).
    # Expected ranking: DECISION_MAKING (0.0) first, then COMMUNICATION (0.25),
    # then REASONING (0.5).
    primary_gaps = [
        {"construct": "REASONING", "confidence": 0.5, "status": "weak"},
        {"construct": "DECISION_MAKING", "confidence": 0.0, "status": "missing"},
        {"construct": "COMMUNICATION", "confidence": 0.25, "status": "weak"},
    ]

    decision = planner.plan_objective(state, primary_gaps, [])

    # DECISION_MAKING must win — it's at 0.0 (missing), lowest confidence
    assert decision.target_constructs[0] == "DECISION_MAKING"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 9: Dead-End Objective Exhaustion
#
# All primary AND secondary gaps have exhausted their candidate objectives,
# but confidence has NOT reached sufficiency and turn cap has NOT been hit.
# This is a distinct reachable state — Stage 4 must terminate cleanly.
# ═══════════════════════════════════════════════════════════════════════════════
def test_dead_end_objective_exhaustion_terminates_cleanly():
    """
    All candidate objectives for ETHICAL_REASONING and ADAPTABILITY are
    exhausted (ethical_challenge and failure_recovery both used). Gaps
    remain but no further objectives are available.
    """
    state = _make_state(
        primary=["ETHICAL_REASONING"],
        secondary=["ADAPTABILITY"],
        followup_history=[
            {"objective": "ethical_challenge"},
            {"objective": "failure_recovery"},
        ],
    )
    planner = AdaptiveObjectivePlanner()

    primary_gaps = [
        {"construct": "ETHICAL_REASONING", "confidence": 0.25, "status": "weak"},
    ]
    secondary_gaps = [
        {"construct": "ADAPTABILITY", "confidence": 0.25, "status": "weak"},
    ]

    decision = planner.plan_objective(state, primary_gaps, secondary_gaps)

    assert decision.is_terminate is True
    assert "exhausted" in decision.termination_reason.lower()
    assert decision.objective == ""


# ═══════════════════════════════════════════════════════════════════════════════
# Additional edge case tests
# ═══════════════════════════════════════════════════════════════════════════════

def test_canonical_5_field_output():
    """Stage 5 JSON output must have exactly 5 canonical fields."""
    state = _make_state()
    planner = AdaptiveObjectivePlanner()
    primary_gaps = [
        {"construct": "DECISION_MAKING", "confidence": 0.25, "status": "weak"},
    ]
    decision = planner.plan_objective(state, primary_gaps, [])
    d = decision.to_dict()

    assert set(d.keys()) == {"objective", "target_constructs", "reason", "difficulty", "constraints"}
    assert "is_repeat" not in d
    assert "is_terminate" not in d
    assert "action" not in d


def test_difficulty_intermediate_for_first_probe():
    """First probe on a construct → difficulty = Intermediate."""
    state = _make_state()
    planner = AdaptiveObjectivePlanner()
    primary_gaps = [
        {"construct": "DECISION_MAKING", "confidence": 0.25, "status": "weak"},
    ]
    decision = planner.plan_objective(state, primary_gaps, [])
    assert decision.to_dict()["difficulty"] == "Intermediate"


def test_signal_priority_contradiction_over_hedging():
    """When both contradiction AND heavy hedging exist, contradiction wins."""
    entry = EvidenceLogEntry(
        turn=1,
        source="initial_response",
        claims=["I chose A", "Actually I chose B"],
        hedges=["I think", "maybe", "probably"],
        contradictions=["Previously said A, now says B"],
    )
    state = _make_state(evidence_log=[entry])
    planner = AdaptiveObjectivePlanner()
    primary_gaps = [
        {"construct": "DECISION_MAKING", "confidence": 0.25, "status": "weak"},
    ]

    decision = planner.plan_objective(state, primary_gaps, [])

    assert decision.objective == "contradiction_detection"


def test_dual_construct_shared_objective():
    """
    DECISION_MAKING and LEADERSHIP both have 'priority_shift' in their
    candidate objectives. Should select dual-construct targeting.
    """
    state = _make_state(primary=["DECISION_MAKING", "LEADERSHIP"])
    planner = AdaptiveObjectivePlanner()
    primary_gaps = [
        {"construct": "DECISION_MAKING", "confidence": 0.25, "status": "weak"},
        {"construct": "LEADERSHIP", "confidence": 0.25, "status": "weak"},
    ]

    decision = planner.plan_objective(state, primary_gaps, [])

    # trade_off_analysis is first for DECISION_MAKING and also maps to REASONING,
    # not LEADERSHIP. But priority_shift maps to both DECISION_MAKING and LEADERSHIP.
    assert len(decision.target_constructs) == 2, f"Expected dual-construct targeting, got {decision.target_constructs}"
    assert set(decision.target_constructs) == {"DECISION_MAKING", "LEADERSHIP"}
    assert decision.objective == "priority_shift"


def test_secondary_gap_dual_construct_check():
    """
    Dual-construct intersection also applies within secondary_gaps when
    primary_gaps is empty.
    """
    state = _make_state(
        primary=["DECISION_MAKING"],
        secondary=["COMMUNICATION", "ATTENTION"],
    )
    planner = AdaptiveObjectivePlanner()

    # All primary constructs sufficient
    primary_gaps = []
    secondary_gaps = [
        {"construct": "COMMUNICATION", "confidence": 0.25, "status": "weak"},
        {"construct": "ATTENTION", "confidence": 0.25, "status": "weak"},
    ]

    decision = planner.plan_objective(state, primary_gaps, secondary_gaps)

    # Both COMMUNICATION and ATTENTION have 'clarification' in catalog
    assert decision.objective == "clarification"
    assert set(decision.target_constructs) == {"COMMUNICATION", "ATTENTION"}


def test_single_primary_gap_with_multiple_secondary_does_not_cross():
    """
    1 primary gap + 2+ secondary gaps: primary always wins, no cross-tier
    dual-construct intersection.
    """
    state = _make_state(
        primary=["DECISION_MAKING"],
        secondary=["COMMUNICATION", "ATTENTION"],
    )
    planner = AdaptiveObjectivePlanner()

    primary_gaps = [
        {"construct": "DECISION_MAKING", "confidence": 0.25, "status": "weak"},
    ]
    secondary_gaps = [
        {"construct": "COMMUNICATION", "confidence": 0.25, "status": "weak"},
        {"construct": "ATTENTION", "confidence": 0.25, "status": "weak"},
    ]

    decision = planner.plan_objective(state, primary_gaps, secondary_gaps)

    # Must target DECISION_MAKING only — no cross-tier intersection
    assert decision.target_constructs == ["DECISION_MAKING"]


def test_scenario_constraints_passed_through():
    """Constraints from upstream scenario context appear in Stage 5 output."""
    state = _make_state()
    planner = AdaptiveObjectivePlanner()
    primary_gaps = [
        {"construct": "DECISION_MAKING", "confidence": 0.25, "status": "weak"},
    ]

    decision = planner.plan_objective(
        state, primary_gaps, [], scenario_constraints=["Time Pressure"]
    )

    assert decision.to_dict()["constraints"] == ["Time Pressure"]
