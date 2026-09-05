"""
Unit tests for Stage 5: Follow-up Specification Compiler (AdaptiveFollowUpSpecificationCompiler).
"""

import pytest
from app.application.followup_subsystem.session_state import FollowUpSessionState, EvidenceLogEntry
from app.application.followup_subsystem.adaptive_objective_planner import FollowUpObjectiveDecision
from app.application.followup_subsystem.adaptive_specification_compiler import (
    AdaptiveFollowUpSpecificationCompiler,
    OBJECTIVE_MAPPING_TABLE,
    DEFAULT_FALLBACK_MAPPING,
)
from app.application.followup_subsystem.specification import FollowUpSpecification
from app.application.followup_subsystem.style_engine import StyleProfile


def _make_sample_state():
    state = FollowUpSessionState(
        scenario_id="SCEN-001",
        candidate_id="CAND-001",
        primary_constructs=["DECISION_MAKING", "REASONING"],
        secondary_constructs=["COMMUNICATION", "ATTENTION"],
    )
    entry1 = EvidenceLogEntry(
        turn=1,
        source="initial_response",
        claims=["I decided to re-route current limits to 75% to keep battery pack cool."],
        reasoning_shown=["Evaluated trade-off between speed and thermal limit"],
        assumptions=["Assumed inspection deadline is fixed"],
        hedges=["decided to"],
    )
    state.evidence_log.append(entry1)
    return state


def test_compile_all_12_objectives_mapping():
    """Verify all 12 objectives in OBJECTIVE_MAPPING_TABLE map correctly."""
    compiler = AdaptiveFollowUpSpecificationCompiler()
    state = _make_sample_state()

    for obj_name, expected in OBJECTIVE_MAPPING_TABLE.items():
        decision = FollowUpObjectiveDecision(
            objective=obj_name,
            target_constructs=["DECISION_MAKING"],
            reason=f"Test reason for {obj_name}",
        )

        spec = compiler.compile(
            decision=decision,
            session_state=state,
            turn_number=1,
            transcript_text="Sample candidate response text",
        )

        assert isinstance(spec, FollowUpSpecification)
        assert spec.intent == expected["intent"]
        assert spec.cognitive_depth == expected["cognitive_depth"]
        assert spec.target_construct == "DECISION_MAKING"
        assert spec.reason == f"Test reason for {obj_name}"


def test_compile_unmapped_objective_safe_fallback():
    """Unmapped objective string should fall back safely to PROBE_MISSING_CONSTRUCT without crashing."""
    compiler = AdaptiveFollowUpSpecificationCompiler()
    state = _make_sample_state()

    decision = FollowUpObjectiveDecision(
        objective="unknown_custom_objective",
        target_constructs=["LEADERSHIP"],
        reason="Reason for unmapped objective",
    )

    spec = compiler.compile(
        decision=decision,
        session_state=state,
        turn_number=1,
    )

    assert spec.intent == DEFAULT_FALLBACK_MAPPING["intent"]
    assert spec.cognitive_depth == DEFAULT_FALLBACK_MAPPING["cognitive_depth"]
    assert spec.target_construct == "LEADERSHIP"


def test_dual_construct_collapsing_rule():
    """Dual target constructs ['LEADERSHIP', 'PROBLEM_SOLVING'] collapse target_construct to 'LEADERSHIP' while preserving metadata."""
    compiler = AdaptiveFollowUpSpecificationCompiler()
    state = _make_sample_state()

    decision = FollowUpObjectiveDecision(
        objective="alternative_strategy",
        target_constructs=["LEADERSHIP", "PROBLEM_SOLVING"],
        reason="Dual construct objective selected",
    )

    spec = compiler.compile(decision=decision, session_state=state, turn_number=1)

    assert spec.target_construct == "LEADERSHIP"
    assert spec.metadata["dual_target_constructs"] == ["LEADERSHIP", "PROBLEM_SOLVING"]
    assert spec.metadata["is_dual_target"] is True


def test_context_snippet_and_memory_reference_grounding():
    """Verifies context_snippet extraction from Stage 1 claims and memory reference formatting."""
    compiler = AdaptiveFollowUpSpecificationCompiler()
    state = _make_sample_state()

    # Add a 2nd turn entry to test multi-turn memory reference formatting
    entry2 = EvidenceLogEntry(
        turn=2,
        source="followup_1",
        claims=["Missing the 10:00 AM deadline causes automatic disqualification."],
        hedges=["because"],
    )
    state.evidence_log.append(entry2)

    decision = FollowUpObjectiveDecision(
        objective="reasoning_probe",
        target_constructs=["REASONING"],
        reason="Probe reasoning depth",
    )

    spec = compiler.compile(decision=decision, session_state=state, turn_number=2)

    assert spec.context_snippet == "Missing the 10:00 AM deadline causes automatic disqualification."
    assert "Earlier in turn 1" in spec.interviewer_memory_reference
    assert "I decided to re-route current limits" in spec.interviewer_memory_reference


def test_canonical_18_field_dict_schema():
    """spec.to_dict() must return all canonical 18 fields required by Stage 6 and QA engine."""
    compiler = AdaptiveFollowUpSpecificationCompiler()
    state = _make_sample_state()
    style = StyleProfile(
        interviewer_tone="CHALLENGING",
        empathy_level="MODERATE",
        assertiveness_level="HIGH",
        questioning_style="COUNTERFACTUAL",
        pacing="MEASURED",
        encouragement_level="MODERATE",
        pressure_level="HIGH",
        followup_length="CONCISE",
        conversational_personality="ANALYTICAL_EVALUATOR",
    )

    decision = FollowUpObjectiveDecision(
        objective="trade_off_analysis",
        target_constructs=["DECISION_MAKING"],
        reason="Challenge trade-offs",
        constraints=["Time Pressure"],
    )

    spec = compiler.compile(
        decision=decision,
        session_state=state,
        style_profile=style,
        turn_number=1,
    )

    d = spec.to_dict()
    canonical_keys = {
        "intent", "target_construct", "reason", "context_snippet", "cognitive_depth",
        "conversation_stage", "turn_number", "style_profile", "interviewer_memory_reference",
        "questioning_style", "tone", "pressure_level", "empathy_level",
        "remaining_constructs", "saturation_scores", "closure_probability",
        "estimated_remaining_turns", "metadata"
    }

    assert canonical_keys.issubset(set(d.keys()))
    assert d["intent"] == "CHALLENGE_REASONING"
    assert d["cognitive_depth"] == "TRADE_OFF_DEFENSE"
    assert d["tone"] == "CHALLENGING"
    assert d["pressure_level"] == "HIGH"
    assert d["metadata"]["constraints"] == ["Time Pressure"]


def test_additive_metadata_merging():
    """Verify pre-existing metadata dict is merged additively without overwriting keys."""
    compiler = AdaptiveFollowUpSpecificationCompiler()
    state = _make_sample_state()

    decision = FollowUpObjectiveDecision(
        objective="reasoning_probe",
        target_constructs=["REASONING"],
        reason="Probe reasoning depth",
    )

    existing = {"pre_existing_key": "pre_existing_value", "custom_flag": True}
    spec = compiler.compile(
        decision=decision,
        session_state=state,
        turn_number=1,
        existing_metadata=existing,
    )

    assert spec.metadata["pre_existing_key"] == "pre_existing_value"
    assert spec.metadata["custom_flag"] is True
    assert spec.metadata["dual_target_constructs"] == ["REASONING"]
    assert spec.metadata["is_dual_target"] is False


def test_empty_target_constructs_warning_fallback(caplog):
    """Empty target_constructs list in decision logs a warning and falls back to primary construct from scenario declaration."""
    compiler = AdaptiveFollowUpSpecificationCompiler()
    state = _make_sample_state()  # primary_constructs = ["DECISION_MAKING", "REASONING"]

    decision = FollowUpObjectiveDecision(
        objective="reasoning_probe",
        target_constructs=[],
        reason="Decision with empty target constructs",
    )

    spec = compiler.compile(decision=decision, session_state=state, turn_number=1)

    assert spec.target_construct == "DECISION_MAKING"
    assert spec.metadata["target_construct_fallback_applied"] is True
    assert "Empty target_constructs list" in caplog.text


def test_style_profile_none_consistency():
    """When style_profile is None, nested style_profile dict and top-level flattened style fields are consistent."""
    compiler = AdaptiveFollowUpSpecificationCompiler()
    state = _make_sample_state()

    decision = FollowUpObjectiveDecision(
        objective="trade_off_analysis",
        target_constructs=["DECISION_MAKING"],
        reason="Challenge trade-offs",
    )

    spec = compiler.compile(decision=decision, session_state=state, style_profile=None)

    assert spec.tone == "NEUTRAL"
    assert spec.pressure_level == "MODERATE"
    assert spec.empathy_level == "MODERATE"
    assert spec.questioning_style == "GUIDED_REFLECTION"

    # Nested style_profile dict must match flattened top-level fields
    assert spec.style_profile["interviewer_tone"] == spec.tone
    assert spec.style_profile["pressure_level"] == spec.pressure_level
    assert spec.style_profile["empathy_level"] == spec.empathy_level
    assert spec.style_profile["questioning_style"] == spec.questioning_style


