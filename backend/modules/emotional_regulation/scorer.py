from typing import Dict, Any, List

WEIGHTS = {
    "recoveryResilience": 0.30,
    "stressTolerance": 0.25,
    "adaptationPersistence": 0.25,
    "decisionStability": 0.20,
}

THRESHOLDS = {
    "minimumReactionTime": 2000.0,      # 2 seconds
    "maximumReactionTime": 15000.0,     # 15 seconds
    "maximumPanicClicks": 20,           # per session
    "maximumRecoveryLatency": 30000.0,  # 30 seconds
}

def inverse_normalize(value: float, ideal: float, worst: float) -> float:
    if value <= ideal:
        return 100.0
    if value >= worst:
        return 0.0
    return round(((worst - value) / (worst - ideal)) * 100.0, 1)

def direct_normalize(value: float, min_val: float, max_val: float) -> float:
    if value >= max_val:
        return 100.0
    if value <= min_val:
        return 0.0
    return round(((value - min_val) / (max_val - min_val)) * 100.0, 1)

def calc_recovery_resilience(events: List[Dict[str, Any]]) -> float:
    recovery_events = [e for e in events if e.get("recovery_latency_ms", 0) > 0]
    avg_rec = (
        sum(e["recovery_latency_ms"] for e in recovery_events) / len(recovery_events)
        if recovery_events else THRESHOLDS["maximumRecoveryLatency"]
    )
    rec_score = inverse_normalize(avg_rec, 3000.0, THRESHOLDS["maximumRecoveryLatency"])

    mod3_events = [e for e in events if e.get("module") == 3]
    wrong_decisions = sum(1 for e in mod3_events if e.get("event_type") == "WRONG_DECISION")
    retries = sum(e.get("retry_count", 0) for e in mod3_events)
    persistence = (
        direct_normalize(retries / wrong_decisions, 0.0, 2.0)
        if wrong_decisions > 0 else 80.0
    )

    post_decisions = [
        e for e in mod3_events if e.get("event_type") in ("CORRECT_DECISION", "WRONG_DECISION")
    ]
    post_correct = sum(1 for e in post_decisions if e.get("event_type") == "CORRECT_DECISION")
    post_acc = (post_correct / len(post_decisions) * 100.0) if post_decisions else 50.0

    return round(rec_score * 0.40 + persistence * 0.30 + post_acc * 0.30, 1)

def calc_stress_tolerance(events: List[Dict[str, Any]]) -> float:
    mod2_events = [e for e in events if e.get("module") == 2]
    panic_clicks = sum(e.get("panic_clicks", 0) for e in mod2_events)
    panic_score = inverse_normalize(panic_clicks, 0, THRESHOLDS["maximumPanicClicks"])

    stress_rts = [e.get("decision_time_ms", 0) for e in mod2_events if e.get("decision_time_ms", 0) > 0]
    avg_stress_rt = (sum(stress_rts) / len(stress_rts)) if stress_rts else THRESHOLDS["maximumReactionTime"]
    rt_score = inverse_normalize(avg_stress_rt, THRESHOLDS["minimumReactionTime"], THRESHOLDS["maximumReactionTime"])

    decisions = [e for e in mod2_events if e.get("event_type") in ("CORRECT_DECISION", "WRONG_DECISION")]
    corrects = sum(1 for e in decisions if e.get("event_type") == "CORRECT_DECISION")
    acc = (corrects / len(decisions) * 100.0) if decisions else 50.0

    timeouts = sum(1 for e in mod2_events if e.get("event_type") == "TIMEOUT")
    penalty = min(timeouts * 5.0, 25.0)

    raw = (panic_score * 0.35) + (rt_score * 0.30) + (acc * 0.35)
    return max(0.0, round(raw - penalty, 1))

def calc_adaptation_persistence(events: List[Dict[str, Any]]) -> float:
    mod4_events = [e for e in events if e.get("module") == 4]
    acc = (
        sum(1 for e in mod4_events if e.get("event_type") == "CORRECT_DECISION")
        / max(1, len([e for e in mod4_events if e.get("event_type") in ("CORRECT_DECISION", "WRONG_DECISION")]))
        * 100.0
    )
    all_retries = sum(e.get("retry_count", 0) for e in events)
    persist = direct_normalize(all_retries, 0.0, 10.0)
    return round(acc * 0.65 + persist * 0.35, 1)

def calc_decision_stability(events: List[Dict[str, Any]]) -> float:
    decisions = [
        e for e in events if e.get("event_type") in ("CORRECT_DECISION", "WRONG_DECISION")
    ]
    if not decisions:
        return 70.0

    half = len(decisions) // 2
    if half > 0:
        first_half = decisions[:half]
        second_half = decisions[half:]
        err1 = sum(1 for e in first_half if e.get("event_type") == "WRONG_DECISION") / len(first_half)
        err2 = sum(1 for e in second_half if e.get("event_type") == "WRONG_DECISION") / len(second_half)
        escalation = max(0.0, err2 - err1)
    else:
        escalation = 0.0

    esc_score = inverse_normalize(escalation, 0.0, 0.5)
    overall_acc = (sum(1 for e in decisions if e.get("event_type") == "CORRECT_DECISION") / len(decisions)) * 100.0
    return round(esc_score * 0.40 + overall_acc * 0.60, 1)

def calculate_crisis_score(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not events:
        return {
            "overallScore": 75.0,
            "recoveryResilience": 75.0,
            "stressTolerance": 75.0,
            "adaptationPersistence": 75.0,
            "decisionStability": 75.0,
        }

    rec = calc_recovery_resilience(events)
    stress = calc_stress_tolerance(events)
    adapt = calc_adaptation_persistence(events)
    stab = calc_decision_stability(events)

    overall = round(
        rec * WEIGHTS["recoveryResilience"] +
        stress * WEIGHTS["stressTolerance"] +
        adapt * WEIGHTS["adaptationPersistence"] +
        stab * WEIGHTS["decisionStability"],
        1
    )

    return {
        "overallScore": max(45.0, min(99.0, overall)),
        "recoveryResilience": rec,
        "stressTolerance": stress,
        "adaptationPersistence": adapt,
        "decisionStability": stab,
        "weights": WEIGHTS
    }
