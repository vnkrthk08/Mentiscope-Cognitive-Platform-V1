"""
Unit tests for Module 8.6: Backchannel Registry & Deterministic Canary Router.
"""

import pytest
from app.application.followup_subsystem.backchannel_registry import BackchannelRegistry, backchannel_registry


def test_registry_has_32_unique_phrases():
    reg = BackchannelRegistry()
    all_phrases = reg.get_all_phrases()
    assert len(all_phrases) == 32
    assert len(set(all_phrases)) == 32, "Duplicate phrases found in backchannel registry!"
    for cat in ["COGNITIVE", "ACTION_STANCE", "ANALYTICAL", "FORWARD_LOOKING"]:
        assert cat in reg.CATEGORIES
        assert len(reg.CATEGORIES[cat]) == 8


def test_session_lru_rotation_prevents_repetition():
    reg = BackchannelRegistry(memory_window=8)
    session_id = "test_session_rotation_123"
    selected_phrases = []

    for turn in range(1, 9):
        sel = reg.select_backchannel(session_id=session_id, turn_number=turn)
        selected_phrases.append(sel.text)

    # Within 8 turns, no phrase should be repeated
    assert len(selected_phrases) == 8
    assert len(set(selected_phrases)) == 8, f"Repeated phrase within 8-turn memory window: {selected_phrases}"


def test_category_rotation_across_turns():
    reg = BackchannelRegistry()
    session_id = "test_category_rotation"

    sel1 = reg.select_backchannel(session_id=session_id, turn_number=1)
    sel2 = reg.select_backchannel(session_id=session_id, turn_number=2)
    sel3 = reg.select_backchannel(session_id=session_id, turn_number=3)
    sel4 = reg.select_backchannel(session_id=session_id, turn_number=4)

    assert sel1.category == "COGNITIVE"
    assert sel2.category == "ACTION_STANCE"
    assert sel3.category == "ANALYTICAL"
    assert sel4.category == "FORWARD_LOOKING"


def test_deterministic_canary_routing():
    # Percentage 0: Always False
    assert not BackchannelRegistry.is_canary_session("session_1", rollout_percentage=0)
    assert not BackchannelRegistry.is_canary_session("session_2", rollout_percentage=0)

    # Percentage 100: Always True
    assert BackchannelRegistry.is_canary_session("session_1", rollout_percentage=100)
    assert BackchannelRegistry.is_canary_session("session_2", rollout_percentage=100)

    # Determinism: Repeated calls with same session_id must yield exact same result
    for s_id in ["student_sess_abc", "student_sess_xyz", "student_sess_123"]:
        res_a = BackchannelRegistry.is_canary_session(s_id, rollout_percentage=10)
        res_b = BackchannelRegistry.is_canary_session(s_id, rollout_percentage=10)
        assert res_a == res_b

    # Statistical distribution check on 1,000 sessions with 10% rollout (should be ~8-12%)
    canary_count = sum(1 for i in range(1000) if BackchannelRegistry.is_canary_session(f"sess_{i}", rollout_percentage=10))
    assert 70 <= canary_count <= 130, f"Expected ~10% canary allocation, got {canary_count}/1000"
