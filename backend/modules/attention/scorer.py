import math
from typing import Dict, Any, List, Optional

def clamp(val: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    return max(min_val, min(max_val, val))

def std_dev(arr: List[float]) -> float:
    if not arr or len(arr) < 2:
        return 0.0
    mean = sum(arr) / len(arr)
    variance = sum((x - mean) ** 2 for x in arr) / len(arr)
    return math.sqrt(variance)

def linear_slope(arr: List[float]) -> float:
    if not arr or len(arr) < 2:
        return 0.0
    n = len(arr)
    xs = list(range(n))
    mean_x = (n - 1) / 2.0
    mean_y = sum(arr) / n
    num = sum((xs[i] - mean_x) * (arr[i] - mean_y) for i in range(n))
    den = sum((xs[i] - mean_x) ** 2 for i in range(n))
    return 0.0 if den == 0 else num / den

def calculate_fatigue_score(rt_list: List[float]) -> Dict[str, float]:
    if not rt_list or len(rt_list) < 3:
        return {"slope": 0.0, "score": 100.0}
    block_size = math.ceil(len(rt_list) / 3.0)
    blocks = [rt_list[i * block_size : (i + 1) * block_size] for i in range(3)]
    block_means = [sum(b) / len(b) if b else 0.0 for b in blocks]
    slope = linear_slope(block_means)
    fatigue_score = clamp(100.0 - (max(0.0, slope) / 400.0) * 100.0)
    return {"slope": slope, "score": fatigue_score}

def calculate_attention_stability(hit_rate: float, rt_var_score: float, fatigue_score: float) -> float:
    return clamp((hit_rate * 0.40) + (rt_var_score * 0.30) + (fatigue_score * 0.30))

def calculate_impulsivity_index(false_alarms: int, total_distractors: int) -> float:
    if total_distractors <= 0:
        return 0.0
    return clamp((false_alarms / total_distractors) * 100.0)

def calculate_recovery_after_errors(correctness_array: List[bool]) -> float:
    if not correctness_array:
        return 0.0
    error_count = 0
    total_recovery_trials = 0
    in_error_state = False
    trials_since_error = 0

    for is_correct in correctness_array:
        if not is_correct:
            if not in_error_state:
                in_error_state = True
                error_count += 1
                trials_since_error = 0
            trials_since_error += 1
        else:
            if in_error_state:
                total_recovery_trials += trials_since_error
                in_error_state = False

    return (total_recovery_trials / error_count) if error_count > 0 else 0.0

def score_sustained(
    hits: int,
    total_targets: int,
    rt_list: List[float],
    false_alarms: int = 0,
    total_distractors: int = 0,
    correctness_array: Optional[List[bool]] = None,
) -> Dict[str, Any]:
    correctness_array = correctness_array or []
    missed = max(0, total_targets - hits)
    omission_rate = (missed / total_targets * 100.0) if total_targets > 0 else 100.0
    hit_rate = 100.0 - omission_rate

    rt_sd = std_dev(rt_list)
    rt_var_score = clamp(100.0 - (rt_sd / 500.0) * 100.0)

    fatigue = calculate_fatigue_score(rt_list)
    att_stability = calculate_attention_stability(hit_rate, rt_var_score, fatigue["score"])
    impulsivity = calculate_impulsivity_index(false_alarms, total_distractors)
    recovery_trials = calculate_recovery_after_errors(correctness_array)

    fa_penalty = clamp(100.0 - (false_alarms / max(1, total_distractors)) * 100.0)
    score = clamp(hit_rate * 0.80 + fa_penalty * 0.20)

    return {
        "score": round(score, 1),
        "hitRate": round(hit_rate, 1),
        "omissionRate": round(omission_rate, 1),
        "rtVariabilityScore": round(rt_var_score, 1),
        "fatigueScore": round(fatigue["score"], 1),
        "fatigueSlope": round(fatigue["slope"], 1),
        "rtStdDev": round(rt_sd, 1),
        "avgRT": round(sum(rt_list) / len(rt_list), 1) if rt_list else 0.0,
        "attentionStability": round(att_stability, 1),
        "impulsivityIndex": round(impulsivity, 1),
        "recoveryTrials": round(recovery_trials, 1),
    }

def score_selective(
    correct_clicks: int,
    total_targets: int,
    wrong_clicks: int,
    total_distractors: int,
    rt_high: float = 0.0,
    rt_low: float = 0.0,
    rt_list: Optional[List[float]] = None,
    correctness_array: Optional[List[bool]] = None,
) -> Dict[str, Any]:
    rt_list = rt_list or []
    correctness_array = correctness_array or []

    hit_rate = (correct_clicks / total_targets * 100.0) if total_targets > 0 else 0.0
    false_alarm_rate = (wrong_clicks / total_distractors * 100.0) if total_distractors > 0 else 0.0
    false_alarm_score = clamp(100.0 - false_alarm_rate)

    distractor_cost = max(0.0, rt_high - rt_low)
    distractor_score = clamp(100.0 - (distractor_cost / 300.0) * 100.0)

    rt_sd = std_dev(rt_list)
    rt_var_score = clamp(100.0 - (rt_sd / 500.0) * 100.0)

    fatigue = calculate_fatigue_score(rt_list)
    att_stability = calculate_attention_stability(hit_rate, rt_var_score, fatigue["score"])
    impulsivity = calculate_impulsivity_index(wrong_clicks, total_distractors)
    recovery_trials = calculate_recovery_after_errors(correctness_array)

    score = clamp(hit_rate * 0.50 + false_alarm_score * 0.50)

    return {
        "score": round(score, 1),
        "hitRate": round(hit_rate, 1),
        "falseAlarmRate": round(false_alarm_rate, 1),
        "falseAlarmScore": round(false_alarm_score, 1),
        "distractorScore": round(distractor_score, 1),
        "distractorCost": round(distractor_cost, 1),
        "rtStdDev": round(rt_sd, 1),
        "fatigueSlope": round(fatigue["slope"], 1),
        "attentionStability": round(att_stability, 1),
        "impulsivityIndex": round(impulsivity, 1),
        "recoveryTrials": round(recovery_trials, 1),
    }

def score_divided(
    correct_presses: int,
    total_targets: int,
    false_presses: int,
    total_non_targets: int,
    rt_dual: float = 0.0,
    rt_single: float = 0.0,
    rt_list: Optional[List[float]] = None,
    correctness_array: Optional[List[bool]] = None,
) -> Dict[str, Any]:
    rt_list = rt_list or []
    correctness_array = correctness_array or []

    hit_rate = (correct_presses / total_targets * 100.0) if total_targets > 0 else 0.0
    fa_rate = (false_presses / total_non_targets * 100.0) if total_non_targets > 0 else 0.0
    fa_score = clamp(100.0 - fa_rate)

    split_cost = max(0.0, rt_dual - rt_single)
    split_score = clamp(100.0 - (split_cost / 300.0) * 100.0)

    rt_sd = std_dev(rt_list)
    rt_var_score = clamp(100.0 - (rt_sd / 500.0) * 100.0)

    fatigue = calculate_fatigue_score(rt_list)
    att_stability = calculate_attention_stability(hit_rate, rt_var_score, fatigue["score"])
    impulsivity = calculate_impulsivity_index(false_presses, total_non_targets)
    recovery_trials = calculate_recovery_after_errors(correctness_array)

    score = clamp(hit_rate * 0.50 + fa_score * 0.50)

    return {
        "score": round(score, 1),
        "hitRate": round(hit_rate, 1),
        "falseAlarmRate": round(fa_rate, 1),
        "falseAlarmScore": round(fa_score, 1),
        "splitScore": round(split_score, 1),
        "splitCost": round(split_cost, 1),
        "rtStdDev": round(rt_sd, 1),
        "fatigueSlope": round(fatigue["slope"], 1),
        "attentionStability": round(att_stability, 1),
        "impulsivityIndex": round(impulsivity, 1),
        "recoveryTrials": round(recovery_trials, 1),
    }

def score_executive(
    rt_before_switch: float,
    rt_after_switch: float,
    switch_errors: int,
    total_after_switch: int,
    recovery_trials: float = 0.0,
    rt_list: Optional[List[float]] = None,
    correctness_array: Optional[List[bool]] = None,
    total_distractors: int = 0,
    false_alarms: int = 0,
) -> Dict[str, Any]:
    rt_list = rt_list or []
    correctness_array = correctness_array or []

    switch_cost = max(0.0, rt_after_switch - rt_before_switch)
    switch_cost_score = clamp(100.0 - (switch_cost / 400.0) * 100.0)

    switch_error_rate = (switch_errors / total_after_switch * 100.0) if total_after_switch > 0 else 0.0
    switch_error_score = clamp(100.0 - switch_error_rate)

    recovery_time_score = clamp(100.0 - (recovery_trials / 10.0) * 100.0)

    rt_sd = std_dev(rt_list)
    rt_var_score = clamp(100.0 - (rt_sd / 500.0) * 100.0)

    fatigue = calculate_fatigue_score(rt_list)
    hit_rate = 100.0 - switch_error_rate
    att_stability = calculate_attention_stability(hit_rate, rt_var_score, fatigue["score"])
    impulsivity = calculate_impulsivity_index(false_alarms, total_distractors)
    general_recovery = calculate_recovery_after_errors(correctness_array)

    score = clamp(switch_cost_score * 0.20 + switch_error_score * 0.50 + recovery_time_score * 0.30)

    return {
        "score": round(score, 1),
        "switchCost": round(switch_cost, 1),
        "switchCostScore": round(switch_cost_score, 1),
        "switchErrorRate": round(switch_error_rate, 1),
        "switchErrorScore": round(switch_error_score, 1),
        "recoveryTimeScore": round(recovery_time_score, 1),
        "recoveryTrials": round(recovery_trials, 1),
        "adaptationSpeed": round(recovery_trials, 1),
        "rtStdDev": round(rt_sd, 1),
        "fatigueSlope": round(fatigue["slope"], 1),
        "attentionStability": round(att_stability, 1),
        "impulsivityIndex": round(impulsivity, 1),
        "generalRecoveryTrials": round(general_recovery, 1),
    }

def score_overall(sustained: float, selective: float, divided: float, executive: float) -> float:
    # 25% sustained, 25% selective, 20% divided, 30% executive
    overall = clamp(sustained * 0.25 + selective * 0.25 + divided * 0.20 + executive * 0.30)
    return round(overall, 1)

def estimate_percentile(overall: float) -> float:
    if overall >= 90:
        return 95.0
    if overall >= 80:
        return 82.0
    if overall >= 70:
        return 68.0
    if overall >= 60:
        return 52.0
    if overall >= 50:
        return 38.0
    if overall >= 40:
        return 25.0
    return 12.0
