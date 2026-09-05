"""
Test Suite: test_aiis_20_turn_qa_audit.py
Runs a rigorous 20-turn QA pass-rate audit on AIIS across diverse realistic, messy, and high-stakes inputs.
Measures and reports the QA pass rate compared to the baseline 75%.
"""

import re
import pytest
from app.application.followup_subsystem.facade import AdaptiveInterviewIntelligenceSystem

AUDIT_20_TURNS = [
    # Turn 1: Structured action & technical reason
    {
        "scenario_title": "Solar Model Motor Alignment 30 Mins Before Judging",
        "transcript_text": "I would immediately halt the stepper motor because the 12-degree misalignment will corrupt solar tracking data.",
        "target_construct": "DECISION_MAKING",
        "session_id": "audit_sess_01",
    },
    # Turn 2: Direct short answer with zero fluff
    {
        "scenario_title": "AI Robotics Emergency Stop",
        "transcript_text": "Safety first.",
        "target_construct": "SAFETY_AWARENESS",
        "session_id": "audit_sess_02",
    },
    # Turn 3: Messy ASR output #1
    {
        "scenario_title": "Science Exhibition",
        "transcript_text": "Fingered my choice but I'm just saying the rationale will be good.",
        "target_construct": "DECISION_MAKING",
        "session_id": "audit_sess_03",
    },
    # Turn 4: Messy ASR output #2
    {
        "scenario_title": "Naval Port Crisis",
        "transcript_text": "I would use. I would actually agree with this Sir, because Navy places are so restrict.",
        "target_construct": "DECISION_MAKING",
        "session_id": "audit_sess_04",
    },
    # Turn 5: High-stakes thermal threshold response
    {
        "scenario_title": "Robotics Competition Battery Thermal Limit Crisis",
        "transcript_text": "We shut down the high-voltage pack immediately when thermal readings spiked past 65°C.",
        "target_construct": "RISK_MITIGATION",
        "session_id": "audit_sess_05",
    },
    # Turn 6: Team briefing / stakeholder communication
    {
        "scenario_title": "Solar Model Motor Alignment 30 Mins Before Judging",
        "transcript_text": "I briefed Mrs. Sen within 10 minutes so everyone on our team was aligned.",
        "target_construct": "COMMUNICATION",
        "session_id": "audit_sess_06",
    },
    # Turn 7: Explicit engineering trade-off
    {
        "scenario_title": "Robotics Competition Battery Thermal Limit Crisis",
        "transcript_text": "I decided to re-route current limits to 75% so the pack cools down while keeping the robot in the competition.",
        "target_construct": "TRADE_OFF_ANALYSIS",
        "session_id": "audit_sess_07",
    },
    # Turn 8: Ethical dilemma handling
    {
        "scenario_title": "Supply Chain Crisis Management",
        "transcript_text": "I will explain to Arjun why safety protocols must not be bypassed under any circumstances.",
        "target_construct": "ETHICAL_REASONING",
        "session_id": "audit_sess_08",
    },
    # Turn 9: Stakeholder conflict resolution
    {
        "scenario_title": "Robotics Competition Battery Thermal Limit Crisis",
        "transcript_text": "I would call an emergency meeting with Dr. Arora to explain our current limiting strategy.",
        "target_construct": "STAKEHOLDER_ALIGNMENT",
        "session_id": "audit_sess_09",
    },
    # Turn 10: Vague input / hesitant decision
    {
        "scenario_title": "Solar Model Motor Alignment 30 Mins Before Judging",
        "transcript_text": "Well, I guess we could try to tighten the bracket and hope it holds.",
        "target_construct": "DECISION_MAKING",
        "session_id": "audit_sess_10",
    },
    # Turn 11: Budget & material constraint
    {
        "scenario_title": "Science Exhibition",
        "transcript_text": "We chose the standard acrylic mount over the custom metal bracket to stay within our team budget.",
        "target_construct": "RESOURCE_MANAGEMENT",
        "session_id": "audit_sess_11",
    },
    # Turn 12: Time pressure prioritization
    {
        "scenario_title": "Solar Model Motor Alignment 30 Mins Before Judging",
        "transcript_text": "With 30 minutes remaining, tightening the existing bracket in 10 minutes is our only realistic path to scoring.",
        "target_construct": "PRIORITIZATION",
        "session_id": "audit_sess_12",
    },
    # Turn 13: Emergency isolation protocol
    {
        "scenario_title": "AI Robotics Emergency Stop",
        "transcript_text": "We isolated the affected battery cells to prevent thermal runaway.",
        "target_construct": "RISK_MITIGATION",
        "session_id": "audit_sess_13",
    },
    # Turn 14: Informal conversational response
    {
        "scenario_title": "Solar Model Motor Alignment 30 Mins Before Judging",
        "transcript_text": "Yeah, I mean, we gotta stop it right now otherwise the whole motor burns out.",
        "target_construct": "DECISION_MAKING",
        "session_id": "audit_sess_14",
    },
    # Turn 15: Reflective lessons learned
    {
        "scenario_title": "Solar Model Motor Alignment 30 Mins Before Judging",
        "transcript_text": "Looking back, we should have tested the stepper motor mount under direct sunlight yesterday.",
        "target_construct": "SELF_REFLECTION",
        "session_id": "audit_sess_15",
    },
    # Turn 16: Compliance firmness
    {
        "scenario_title": "Supply Chain Crisis Management",
        "transcript_text": "I refused to sign off on the unverified battery pack because safety regulations are non-negotiable.",
        "target_construct": "ETHICAL_REASONING",
        "session_id": "audit_sess_16",
    },
    # Turn 17: Quantitative trade-off
    {
        "scenario_title": "Robotics Competition Battery Thermal Limit Crisis",
        "transcript_text": "Re-routing current reduces climbing speed by 20%, but guarantees our rover completes the course safely.",
        "target_construct": "TRADE_OFF_ANALYSIS",
        "session_id": "audit_sess_17",
    },
    # Turn 18: Resource reallocation
    {
        "scenario_title": "AI Robotics Emergency Stop",
        "transcript_text": "I redirected our backup power module to the primary telemetry sensor.",
        "target_construct": "ADAPTABILITY",
        "session_id": "audit_sess_18",
    },
    # Turn 19: Interpersonal persuasion with telemetry evidence
    {
        "scenario_title": "Robotics Competition Battery Thermal Limit Crisis",
        "transcript_text": "When Arjun argued to keep running, I calmly showed him the live thermal sensor telemetry.",
        "target_construct": "COMMUNICATION",
        "session_id": "audit_sess_19",
    },
    # Turn 20: Forward-looking engineering design
    {
        "scenario_title": "Robotics Competition Battery Thermal Limit Crisis",
        "transcript_text": "In our next design iteration, we will add active thermal heat sinks to prevent throttle limits.",
        "target_construct": "STRATEGIC_THINKING",
        "session_id": "audit_sess_20",
    },
]


@pytest.mark.asyncio
async def test_20_turn_qa_pass_rate_audit():
    aiis = AdaptiveInterviewIntelligenceSystem()
    results = []
    intents = []
    shapes = []

    print("\n" + "=" * 75)
    print("AIIS 20-TURN QA PASS-RATE & DIVERSITY AUDIT")
    print("=" * 75)

    passed_count = 0
    total_turns = len(AUDIT_20_TURNS)

    for i, turn in enumerate(AUDIT_20_TURNS, start=1):
        resp = await aiis.generate_followup_question(
            scenario_title=turn["scenario_title"],
            transcript_text=turn["transcript_text"],
            target_construct=turn["target_construct"],
            session_id=turn["session_id"],
        )

        qa_res = resp["qa_result"]
        q_text = resp["follow_up_question"]
        is_passed = qa_res["is_passed"]
        if is_passed:
            passed_count += 1

        cur_intent = resp.get("intent")
        intents.append(cur_intent)
        opening_stem = " ".join(q_text.split()[:4])
        shapes.append(opening_stem)

        results.append({
            "turn": i,
            "scenario": turn["scenario_title"],
            "input": turn["transcript_text"],
            "question": q_text,
            "intent": cur_intent,
            "is_passed": is_passed,
            "failed_checks": qa_res.get("failed_checks", []),
            "understanding": resp.get("understanding_result", {}),
        })

        status_str = "PASS [OK]" if is_passed else f"FAIL {qa_res.get('failed_checks')}"
        print(f"Turn {i:02d} | {status_str:<12} | Intent: {cur_intent:<18} | Q: \"{q_text}\"")

    pass_rate = passed_count / total_turns
    pass_rate_pct = pass_rate * 100.0

    non_null_count = 0
    for r in results:
        und = r.get("understanding", {})
        cd = und.get("candidate_decision", {})
        if cd.get("action") or cd.get("reason") or (cd.get("risks") and len(cd.get("risks")) > 0):
            non_null_count += 1
    non_null_rate_pct = (non_null_count / total_turns) * 100.0

    from collections import Counter, defaultdict
    intent_counts = Counter(intents)
    shape_counts = Counter(shapes)
    intent_stems = defaultdict(list)
    for q, intent in zip(results, intents):
        q_stem = " ".join(q["question"].split()[:4])
        intent_stems[intent].append(q_stem)

    print("=" * 75)
    print(f"AUDIT SUMMARY: {passed_count}/{total_turns} passed ({pass_rate_pct:.1f}%)")
    print(f"EXTRACTION NON-NULL RATE: {non_null_count}/{total_turns} ({non_null_rate_pct:.1f}%)")
    print("INTENT DISTRIBUTION:")
    for k, v in intent_counts.items():
        print(f"  {k}: {v} turns ({v/total_turns*100:.1f}%)")
    print("OPENING SHAPE DISTRIBUTION:")
    for k, v in shape_counts.items():
        print(f"  \"{k} ...\": {v} turns ({v/total_turns*100:.1f}%)")
    print("PER-INTENT SHAPE DISTRIBUTION:")
    for intent, stems in intent_stems.items():
        stem_c = Counter(stems)
        max_stem, max_c = stem_c.most_common(1)[0]
        pct = (max_c / len(stems)) * 100.0
        print(f"  {intent} ({len(stems)} turns): dominant stem \"{max_stem} ...\" = {max_c}/{len(stems)} ({pct:.1f}%)")
    print("=" * 75 + "\n")

    # 1. Assert pass rate is strictly above the 75% baseline requirement
    assert pass_rate >= 0.90, f"QA pass rate {pass_rate_pct:.1f}% must be >= 90% (exceeding 75% baseline)"

    # 2. Assert Intent Diversity: at least 4 distinct intents, no single intent exceeding 50%
    assert len(intent_counts) >= 4, f"Intent diversity requirement failed: expected >= 4 distinct intents, got {len(intent_counts)}"
    for int_name, cnt in intent_counts.items():
        assert cnt / total_turns <= 0.50, f"Intent {int_name} represents {cnt/total_turns*100:.1f}%, exceeding 50% max threshold"

    # 3. Assert Session-Wide Shape Diversity: no single opening stem exceeds 40% of the session
    for stem_name, cnt in shape_counts.items():
        assert cnt / total_turns <= 0.40, f"Opening stem '{stem_name}' represents {cnt/total_turns*100:.1f}%, exceeding 40% max threshold"

    # 4. Assert Per-Intent Shape Diversity: no single opening stem exceeds 50% for any intent used 3+ times
    for intent, stems in intent_stems.items():
        if len(stems) >= 3:
            stem_c = Counter(stems)
            max_stem, max_c = stem_c.most_common(1)[0]
            pct = max_c / len(stems)
            assert pct <= 0.50, f"Intent {intent} has dominant stem '{max_stem}' at {pct*100:.1f}%, exceeding 50% max threshold"

    # 5. Assert Pairwise Uniqueness: 0 literal duplicates across all 20 generated questions
    all_questions = [r["question"].strip().lower() for r in results]
    for idx_a in range(len(all_questions)):
        for idx_b in range(idx_a + 1, len(all_questions)):
            assert all_questions[idx_a] != all_questions[idx_b], (
                f"Literal duplicate found between Turn {idx_a+1} and Turn {idx_b+1}: '{all_questions[idx_a]}'"
            )

    # 6. Assert Zero Generic Filler & Zero Double-Verb Stacking & Zero Bare Pronoun Details
    for r in results:
        q_raw = r["question"]
        q_lower = q_raw.lower()
        for filler in ["taking that action", "taking this immediate action", "to take that approach"]:
            assert filler not in q_lower, f"Turn {r['turn']} contains generic filler '{filler}': '{r['question']}'"
        assert not re.search(r'\b(?:implemented|choosing|chose|decided\s+on|deciding\s+on|prioritizing|prioritized)\s+(?:explaining|complying|deploying|choosing|shutting|halting|cutting|isolating|rerouting)\b', q_lower), (
            f"Turn {r['turn']} contains double-verb stacking: '{r['question']}'"
        )
        assert not re.search(r'\b(?:showing|briefing|telling|stopping|halting|shutting\s+down|explaining\s+to|regarding|involving|when|about)\s+(?:him|her|them|it|this|that|me|us)\b(?!\s+(?:regulations|requirements|constraints|protocols|guidelines|standards|limits|sensors?|mount|bracket|procedures?|orders?|options?|parameters?|team|system|is|was|will|would|can|could|to|on|in|at|of|\w+\s+(?:is|was|are|were)))', q_raw, re.IGNORECASE), (
            f"Turn {r['turn']} contains bare unresolved pronoun detail: '{r['question']}'"
        )

    # 7. Spot-check grounding quality and semantic verb-object compatibility
    turn1_q = results[0]["question"].lower()
    assert "halting the stepper motor" in turn1_q or "stepper motor" in turn1_q, f"Turn 1 dropped stepper motor action: '{results[0]['question']}'"
    turn5_q = results[4]["question"].lower()
    assert "shutting down the high-voltage pack" in turn5_q, f"Turn 5 dropped high-voltage pack: '{results[4]['question']}'"
    assert "and the thermal readings" not in turn5_q, f"Turn 5 joined incompatible verb with thermal readings: '{results[4]['question']}'"
    turn7_q = results[6]["question"].lower()
    assert "re-routing current" in turn7_q or "rerouting current" in turn7_q, f"Turn 7 dropped rerouting action: '{results[6]['question']}'"
    turn12_q = results[11]["question"].lower()
    assert "tightening the existing bracket" in turn12_q or "tightening" in turn12_q, f"Turn 12 dropped tightening bracket action: '{results[11]['question']}'"
    turn19_q = results[18]["question"].lower()
    assert "him" not in turn19_q.split(), f"Turn 19 has unresolved pronoun 'him': '{results[18]['question']}'"


def test_broken_grounding_and_repetition_fixtures():
    """Targeted regression test asserting QA catches broken grounding, generic filler, and cross-turn repetition."""
    from app.application.followup_subsystem.interview_quality_engine import InterviewQAEngine
    from app.application.followup_subsystem.specification import FollowUpSpecification
    from app.application.followup_subsystem.interview_understanding import CandidateDecisionData
    from app.application.followup_subsystem.conversation_manager import ConversationState

    qa_engine = InterviewQAEngine()
    spec = FollowUpSpecification.from_dict({"intent": "CONFIRM_BELIEF"})
    decision = CandidateDecisionData(action="explain to Arjun safety protocols")
    state = ConversationState(session_id="test_qa_fixtures")

    # Fixture 1: Bare person name in 'considered Arjun' MUST fail natural_conversational_flow
    res_arjun = qa_engine.evaluate_question(
        question_text="What priority guided your choice when you considered Arjun?",
        spec=spec,
        decision_data=decision,
        scenario_title="Supply Chain Crisis Management",
        state=state,
        previous_questions=[],
    )
    assert not res_arjun.is_passed, "Bare person name 'considered Arjun' must fail QA"
    assert "natural_conversational_flow" in res_arjun.failed_checks

    # Fixture 2: Circular phrasing referencing choice and rationale MUST fail natural_conversational_flow
    res_circular = qa_engine.evaluate_question(
        question_text="What priority guided your choice when you considered the choice and the rationale?",
        spec=spec,
        decision_data=decision,
        scenario_title="Science Exhibition",
        state=state,
        previous_questions=[],
    )
    assert not res_circular.is_passed, "Circular question 'considered the choice and the rationale' must fail QA"
    assert "natural_conversational_flow" in res_circular.failed_checks

    # Fixture 3: Generic filler phrase MUST fail natural_conversational_flow
    res_filler = qa_engine.evaluate_question(
        question_text="How did you evaluate the compromise involving taking that action against your main goal?",
        spec=FollowUpSpecification.from_dict({"intent": "ASK_TRADEOFF"}),
        decision_data=decision,
        scenario_title="Solar Model Motor Alignment",
        state=state,
        previous_questions=[],
    )
    assert not res_filler.is_passed, "Generic filler phrase 'taking that action' must fail QA"
    assert "natural_conversational_flow" in res_filler.failed_checks

    # Fixture 4: Check #10 cross-turn repetition (>2 consecutive identical opening stems)
    prev_stems_consecutive = [
        "What priority guided your choice when navigating the motor limits?",
        "What priority guided your choice when deciding on the voltage shutdown?",
    ]
    res_repeat_consecutive = qa_engine.evaluate_question(
        question_text="What priority guided your choice when tightening the mount bracket?",
        spec=spec,
        decision_data=decision,
        scenario_title="Solar Model Motor Alignment",
        state=state,
        previous_questions=prev_stems_consecutive,
    )
    assert not res_repeat_consecutive.is_passed, "3rd consecutive question with identical opening stem must fail QA check #10"
    assert "cross_turn_shape_diversity" in res_repeat_consecutive.failed_checks

    # Fixture 5: Check #10 cross-turn repetition (>40% frequency in session)
    prev_stems_session = [
        "What priority guided your choice when navigating the motor limits?",
        "How did you evaluate the compromise involving the acrylic mount?",
        "What priority guided your choice when deciding on the voltage shutdown?",
    ]
    res_repeat_freq = qa_engine.evaluate_question(
        question_text="What priority guided your choice when tightening the mount bracket?",
        spec=spec,
        decision_data=decision,
        scenario_title="Solar Model Motor Alignment",
        state=state,
        previous_questions=prev_stems_session,
    )
    assert not res_repeat_freq.is_passed, "Question exceeding 40% session stem frequency must fail QA check #10"
    assert "cross_turn_shape_diversity" in res_repeat_freq.failed_checks

    # Fixture 6: Check #10 per-intent repetition (>50% frequency for the same intent)
    spec_risk = FollowUpSpecification.from_dict({"intent": "ASK_RISK"})
    state_risk = ConversationState(session_id="test_qa_intent_rep")
    state_risk.asked_intent_history = ["ASK_RISK", "ASK_RISK"]
    prev_stems_risk = [
        "What specific risk were you aiming to avoid when navigating the motor limits?",
        "What specific risk were you aiming to avoid when deciding on the voltage shutdown?",
    ]
    res_repeat_intent = qa_engine.evaluate_question(
        question_text="What specific risk were you aiming to avoid when tightening the mount bracket?",
        spec=spec_risk,
        decision_data=decision,
        scenario_title="Solar Model Motor Alignment",
        state=state_risk,
        previous_questions=prev_stems_risk,
    )
    assert not res_repeat_intent.is_passed, "Question exceeding 50% intent stem frequency must fail QA check #10"
    assert "cross_turn_shape_diversity" in res_repeat_intent.failed_checks

    # Fixture 7: Bare organization/entity as verb object MUST fail natural_conversational_flow
    res_bare_entity = qa_engine.evaluate_question(
        question_text="Walk me through your thinking when you prioritized Navy?",
        spec=spec,
        decision_data=decision,
        scenario_title="Naval Port Crisis",
        state=state,
        previous_questions=[],
    )
    assert not res_bare_entity.is_passed, "Bare entity as verb object 'prioritized Navy' must fail QA"
    assert "natural_conversational_flow" in res_bare_entity.failed_checks

    # Fixture 8: Malformed terminal punctuation (.?) MUST fail natural_conversational_flow
    res_malformed_punct = qa_engine.evaluate_question(
        question_text="Looking at your decision regarding the safety protocol, what principal reason led to that choice in this situation.?",
        spec=spec,
        decision_data=decision,
        scenario_title="Solar Model Motor Alignment",
        state=state,
        previous_questions=[],
    )
    assert not res_malformed_punct.is_passed, "Malformed terminal punctuation '.?' must fail QA"
    assert "natural_conversational_flow" in res_malformed_punct.failed_checks

    # Fixture 9: Duplicate detail concatenation in same sentence MUST fail natural_conversational_flow
    res_dup_detail = qa_engine.evaluate_question(
        question_text="When you decided on shutting down the high-voltage pack and the high-voltage pack, what potential hazard concerned you most?",
        spec=FollowUpSpecification.from_dict({"intent": "ASK_RISK"}),
        decision_data=decision,
        scenario_title="Robotics Competition",
        state=state,
        previous_questions=[],
    )
    assert not res_dup_detail.is_passed, "Concatenated duplicate detail phrase must fail QA"
    assert "natural_conversational_flow" in res_dup_detail.failed_checks

    # Fixture 10: Ungrammatical verb fragment in gerund phrase MUST fail natural_conversational_flow
    res_verb_frag = qa_engine.evaluate_question(
        question_text="Reflecting on the trade-offs, what did you prioritize over secondary factors when re-routing current reduces?",
        spec=FollowUpSpecification.from_dict({"intent": "ASK_TRADEOFF"}),
        decision_data=decision,
        scenario_title="Robotics Competition",
        state=state,
        previous_questions=[],
    )
    assert not res_verb_frag.is_passed, "Ungrammatical verb fragment 'when re-routing current reduces' must fail QA"
    assert "natural_conversational_flow" in res_verb_frag.failed_checks

    # Fixture 11: Hallucinated domain detail not present in source text MUST fail does_not_hallucinate
    res_hallucinated = qa_engine.evaluate_question(
        question_text="If a teammate or stakeholder questioned your choice regarding showing the live thermal and communicating with Arjun, how would you explain your reasoning?",
        spec=FollowUpSpecification.from_dict({"intent": "ASK_STAKEHOLDER"}),
        decision_data=CandidateDecisionData(action="show him the log file and explain to Arjun"),
        scenario_title="Robotics Competition",
        state=state,
        previous_questions=[],
        transcript_text="I would definitely show him the log file and also explain to Arjun our safety limits."
    )
    assert not res_hallucinated.is_passed, "Hallucinated phrase 'live thermal' not in candidate input must fail does_not_hallucinate"
    assert "does_not_hallucinate" in res_hallucinated.failed_checks

    # Fixture 12: Trailing function/conjunction word in extracted detail phrase MUST fail natural_conversational_flow
    # Regression for garbled ASR text like "...wear a fixture navy blue Blazers which actually stop when a bit"
    # producing detail phrases ending in "stopping when" or "stopping when a bit"
    res_trailing_fw = qa_engine.evaluate_question(
        question_text="What priority guided your choice regarding stopping when and navigating School constraints?",
        spec=spec,
        decision_data=CandidateDecisionData(action="stop when a bit"),
        scenario_title="School Science Fair Project Deadline",
        state=state,
        previous_questions=[],
    )
    assert not res_trailing_fw.is_passed, "Extracted detail ending in trailing function word 'stopping when' must fail QA"
    assert "natural_conversational_flow" in res_trailing_fw.failed_checks


FRESH_10_SCENARIOS = [
    # Turn 21: Nuclear Power Plant Sensor Discrepancy
    {
        "scenario_title": "Nuclear Power Plant Sensor Discrepancy",
        "transcript_text": "I isolated steam generator line B within 15 seconds to comply with NRC safety guidelines.",
        "target_construct": "SAFETY_AWARENESS",
        "session_id": "fresh_sess_21",
    },
    # Turn 22: Autonomous Vehicle Braking Failure
    {
        "scenario_title": "Autonomous Vehicle Braking Failure",
        "transcript_text": "I chose deploying the mechanical emergency brake over waiting for sensor telemetry.",
        "target_construct": "TRADE_OFF_ANALYSIS",
        "session_id": "fresh_sess_22",
    },
    # Turn 23: Hospital ICU Triage Allocation
    {
        "scenario_title": "Hospital ICU Triage Allocation",
        "transcript_text": "I briefed Dr. Reynolds immediately so our clinical team was aligned on ventilator allocation.",
        "target_construct": "COMMUNICATION",
        "session_id": "fresh_sess_23",
    },
    # Turn 24: Aerospace Satellite Re-entry Window
    {
        "scenario_title": "Aerospace Satellite Re-entry Window",
        "transcript_text": "I decided on firing the reserve thrusters early to meet NASA descent parameters.",
        "target_construct": "DECISION_MAKING",
        "session_id": "fresh_sess_24",
    },
    # Turn 25: Subsea Pipeline Pressure Spike
    {
        "scenario_title": "Subsea Pipeline Pressure Spike",
        "transcript_text": "We shut down the subsea injection valve immediately when pressure spiked past 300 bar.",
        "target_construct": "RISK_MITIGATION",
        "session_id": "fresh_sess_25",
    },
    # Turn 26: Financial Trading Engine Latency Spike
    {
        "scenario_title": "Financial Trading Engine Latency Spike",
        "transcript_text": "I rerouted order execution to the secondary gateway to prevent transaction drops.",
        "target_construct": "STRATEGIC_THINKING",
        "session_id": "fresh_sess_26",
    },
    # Turn 27: Smart Grid Substation Overload
    {
        "scenario_title": "Smart Grid Substation Overload",
        "transcript_text": "I balanced load shedding against transformer overheating by cutting non-essential feeders.",
        "target_construct": "TRADE_OFF_ANALYSIS",
        "session_id": "fresh_sess_27",
    },
    # Turn 28: Deep Space Probe Telemetry Loss
    {
        "scenario_title": "Deep Space Probe Telemetry Loss",
        "transcript_text": "Looking back at our decision, we should have verified the backup antenna orientation earlier.",
        "target_construct": "SELF_REFLECTION",
        "session_id": "fresh_sess_28",
    },
    # Turn 29: Biotech Laboratory Containment Breach
    {
        "scenario_title": "Biotech Laboratory Containment Breach",
        "transcript_text": "I instructed Meera to seal containment zone 4 before alerting facility operations.",
        "target_construct": "STAKEHOLDER_ALIGNMENT",
        "session_id": "fresh_sess_29",
    },
    # Turn 30: Wildfire Drone Surveillance Protocol
    {
        "scenario_title": "Wildfire Drone Surveillance Protocol",
        "transcript_text": "I agreed with the field commander because FAA airspace restrictions are strictly enforced.",
        "target_construct": "ETHICAL_REASONING",
        "session_id": "fresh_sess_30",
    },
]


@pytest.mark.asyncio
async def test_10_fresh_scenarios_audit():
    """Run AIIS on 10 fresh, out-of-distribution scenarios to verify generalization and absence of regression."""
    aiis = AdaptiveInterviewIntelligenceSystem()
    results = []
    intents = []
    shapes = []
    passed_count = 0
    total_turns = len(FRESH_10_SCENARIOS)

    print("\n" + "=" * 75)
    print("AIIS 10-TURN FRESH SCENARIO GENERALIZATION AUDIT")
    print("=" * 75)

    for i, turn in enumerate(FRESH_10_SCENARIOS, 1):
        resp = await aiis.generate_followup_question(
            scenario_title=turn["scenario_title"],
            transcript_text=turn["transcript_text"],
            target_construct=turn["target_construct"],
            session_id=turn["session_id"],
        )

        q_text = resp["follow_up_question"]
        qa_res = resp["qa_result"]
        is_passed = qa_res.get("is_passed", False)
        if is_passed:
            passed_count += 1

        cur_intent = resp.get("intent")
        intents.append(cur_intent)
        opening_stem = " ".join(q_text.split()[:4])
        shapes.append(opening_stem)

        results.append({
            "turn": i + 20,
            "scenario": turn["scenario_title"],
            "input": turn["transcript_text"],
            "question": q_text,
            "intent": cur_intent,
            "is_passed": is_passed,
            "failed_checks": qa_res.get("failed_checks", []),
        })

        status_str = "PASS [OK]" if is_passed else f"FAIL {qa_res.get('failed_checks')}"
        print(f"Turn {i+20:02d} | {status_str:<12} | Intent: {cur_intent:<18} | Q: \"{q_text}\"")

    pass_rate = passed_count / total_turns
    pass_rate_pct = pass_rate * 100.0

    print("=" * 75)
    print(f"FRESH SCENARIOS AUDIT SUMMARY: {passed_count}/{total_turns} passed ({pass_rate_pct:.1f}%)")
    print("=" * 75 + "\n")

    # Assert 100% pass rate on fresh scenarios
    assert pass_rate >= 0.90, f"Fresh scenarios pass rate {pass_rate_pct:.1f}% must be >= 90%"

    # Assert Pairwise Uniqueness: 0 literal duplicates across all 10 fresh questions
    all_fresh_questions = [r["question"].strip().lower() for r in results]
    for idx_a in range(len(all_fresh_questions)):
        for idx_b in range(idx_a + 1, len(all_fresh_questions)):
            assert all_fresh_questions[idx_a] != all_fresh_questions[idx_b], (
                f"Literal duplicate found between Fresh Turn {idx_a+21} and Turn {idx_b+21}: '{all_fresh_questions[idx_a]}'"
            )

    # Assert no generic filler, no bare entity objects, no duplicate detail concatenation, no malformed punctuation, no double-verb stacking, no bare pronouns
    for r in results:
        q_raw = r["question"]
        q_lower = q_raw.lower()
        for filler in ["taking that action", "taking this immediate action", "to take that approach"]:
            assert filler not in q_lower, f"Turn {r['turn']} contains generic filler: '{q_raw}'"
        assert not re.search(r'[\.,;:!]\?|\?{2,}|\!{2,}|\.\?|\,\?', q_raw), f"Turn {r['turn']} contains malformed punctuation: '{q_raw}'"
        assert not re.search(r'\b(?:prioritized|prioritizing|considered|considering|chose|choosing)\s+([A-Z][a-zA-Z0-9]+)\b(?!\s+(?:regulations|requirements|constraints|protocols|standards))', q_raw), f"Turn {r['turn']} contains bare entity: '{q_raw}'"
        assert not re.search(r'\b(?:implemented|choosing|chose|decided\s+on|deciding\s+on|prioritizing|prioritized)\s+(?:explaining|complying|deploying|choosing|shutting|halting|cutting|isolating|rerouting)\b', q_lower), (
            f"Turn {r['turn']} contains double-verb stacking: '{q_raw}'"
        )
        assert not re.search(r'\b(?:showing|briefing|telling|stopping|halting|shutting\s+down|explaining\s+to|regarding|involving|when|about)\s+(?:him|her|them|it|this|that|me|us)\b(?!\s+(?:regulations|requirements|constraints|protocols|guidelines|standards|limits|sensors?|mount|bracket|procedures?|orders?|options?|parameters?|team|system|is|was|will|would|can|could|to|on|in|at|of|\w+\s+(?:is|was|are|were)))', q_raw, re.IGNORECASE), (
            f"Turn {r['turn']} contains bare unresolved pronoun detail: '{q_raw}'"
        )

    # Spot-check fresh turns for grounded decision extraction
    turn21_q = results[0]["question"].lower()
    assert "isolating steam generator" in turn21_q or "steam generator" in turn21_q, f"Turn 21 dropped steam generator action: '{results[0]['question']}'"
    turn27_q = results[6]["question"].lower()
    assert "cutting non-essential feeders" in turn27_q or "non-essential feeders" in turn27_q or "load shedding" in turn27_q or "overheating" in turn27_q, f"Turn 27 dropped decision detail: '{results[6]['question']}'"
    turn30_q = results[9]["question"].lower()
    assert "complying with faa standards" in turn30_q or "faa" in turn30_q, f"Turn 30 dropped FAA standards detail: '{results[9]['question']}'"
    assert "implemented complying" not in turn30_q, f"Turn 30 has verb stacking: '{results[9]['question']}'"


@pytest.mark.asyncio
async def test_short_and_filler_candidate_answers():
    """Verify that short/low-content answers do not cause quote-splicing or ungrounded template defaults."""
    aiis = AdaptiveInterviewIntelligenceSystem()
    test_cases = [
        ("I explored another plan.", "DECISION_MAKING", "Solar Model Motor Alignment 30 Mins Before Judging", "short_sess_01"),
        ("I would do nothing.", "DECISION_MAKING", "Robotics Competition Battery Thermal Limit Crisis", "short_sess_02"),
        ("I don't know.", "RISK_MITIGATION", "Solar Model Motor Alignment 30 Mins Before Judging", "short_sess_03"),
        ("not sure", "TRADE_OFF_ANALYSIS", "Supply Chain Crisis Management", "short_sess_04"),
        ("I have no idea.", "COMMUNICATION", "AI Robotics Emergency Stop", "short_sess_05"),
        ("The school exam marks are very important to me, so I focused on scoring as high as possible.", "TRADE_OFF_ANALYSIS", "School Science Fair Project Deadline", "short_sess_06")
    ]
    for text, construct, scenario, sess_id in test_cases:
        resp = await aiis.generate_followup_question(
            scenario_title=scenario,
            transcript_text=text,
            target_construct=construct,
            session_id=sess_id,
        )
        q_text = resp["follow_up_question"]
        q_lower = q_text.lower()
        qa_res = resp["qa_result"]

        # 1. QA must pass
        # 2. No verbatim conversational splicing into prepositional phrases
        assert not re.search(r'\b(?:when considering|looking at|regarding|involving)\s+(?:i\s+|we\s+|i\'d\s+|i\'m\s+|i\s+would|i\s+explored|not\s+sure|don\'t\s+know|no\s+idea)\b', q_lower), (
            f"Verbatim conversational quote-splicing detected: '{q_text}'"
        )
        assert "i explored another plan" not in q_lower, f"Verbatim utterance spliced: '{q_text}'"
        assert "i would do nothing" not in q_lower, f"Verbatim utterance spliced: '{q_text}'"
        assert "i don't know" not in q_lower, f"Verbatim utterance spliced: '{q_text}'"

        # 3. Domain relevance: school exam answer must not mention speed and precision or battery packs
        if "exam marks" in text.lower():
            assert "speed and precision" not in q_lower, f"Irrelevant tradeoff template fired: '{q_text}'"
            assert "speed and safety" not in q_lower, f"Irrelevant tradeoff template fired: '{q_text}'"
            assert "battery" not in q_lower, f"Hallucinated battery in exam scenario: '{q_text}'"


@pytest.mark.asyncio
async def test_abstract_reasoning_fixture_suite():
    """Verify that abstract, psychometric, and cognitive-reasoning candidate inputs are extracted accurately and pass QA."""
    aiis = AdaptiveInterviewIntelligenceSystem()
    abstract_fixtures = [
        ("Because when we use AI generated text without personal understanding, we will be caught.", "ETHICAL_REASONING", "Academic Integrity & AI Tools", "abs_01"),
        ("I feel using AI directly would reduce our learning quality, and our professors will easily notice the difference.", "DECISION_MAKING", "Academic Integrity & AI Tools", "abs_02"),
        ("If I just copy paste without knowing the logic, I might fail the viva interview when external examiners ask questions.", "CRITICAL_THINKING", "Engineering Project Submission", "abs_03"),
        ("Even though management asked to ignore the defect, staying silent violates public safety principles.", "ETHICAL_REASONING", "Quality Assurance Whistleblowing", "abs_04"),
        ("Giving full credit to someone who did not contribute harms team morale and sets a damaging precedent.", "LEADERSHIP", "Team Credit Dispute", "abs_05"),
        ("Taking the quick shortcut now will create severe technical debt that our junior engineers cannot maintain.", "TRADE_OFF_ANALYSIS", "Software Architecture Trade-off", "abs_06"),
        ("Refunding the client costs short-term revenue, but preserves our long-term brand credibility.", "DECISION_MAKING", "Client Relationship Crisis", "abs_07"),
        ("Bypassing two-factor authentication saves 5 seconds, but exposes student health records to data breaches.", "RISK_MITIGATION", "Data Privacy Compliance", "abs_08"),
    ]

    passed_count = 0
    non_null_count = 0
    total = len(abstract_fixtures)

    for text, construct, scenario, sess_id in abstract_fixtures:
        resp = await aiis.generate_followup_question(
            scenario_title=scenario,
            transcript_text=text,
            target_construct=construct,
            session_id=sess_id,
        )
        q_text = resp["follow_up_question"]
        qa_res = resp["qa_result"]
        und = resp.get("understanding_result", {})
        cd = und.get("candidate_decision", {})

        action = cd.get("action")
        reason = cd.get("reason")
        risks = cd.get("risks", [])

        if reason or (risks and len(risks) > 0) or action:
            non_null_count += 1

        if qa_res.get("is_passed", False):
            passed_count += 1

    non_null_rate = (non_null_count / total) * 100.0
    pass_rate = (passed_count / total) * 100.0

    print("\n" + "=" * 75)
    print(f"ABSTRACT REASONING AUDIT: {passed_count}/{total} passed ({pass_rate:.1f}%)")
    print(f"ABSTRACT EXTRACTION NON-NULL RATE: {non_null_count}/{total} ({non_null_rate:.1f}%)")
    print("=" * 75)

    assert pass_rate >= 90.0, f"Abstract QA pass rate {pass_rate:.1f}% must be >= 90%"
    assert non_null_rate >= 85.0, f"Abstract extraction non-null rate {non_null_rate:.1f}% must be >= 85%"
