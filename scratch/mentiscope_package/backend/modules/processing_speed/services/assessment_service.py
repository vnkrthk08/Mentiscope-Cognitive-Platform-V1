import math
from statistics import mean
from fastapi import HTTPException

from ..engine import generate_trial
from ..repositories import ProcessingSpeedRepository

RECOMMENDATION_MAP = {
    "Efficient Scanner": [
        "Maintain current visual pacing limits.",
        "Integrate complex visual sorting and code debugging challenges.",
        "Participate in timed visual chunking exercises."
    ],
    "Meticulous Solver": [
        "Integrate training modules focusing on spatial chunking to speed up visual categorization.",
        "Work on timed perceptual drills to gradually decrease scan hesitation.",
        "Practice rapid visual-motor tasks."
    ],
    "Impulsive Matcher": [
        "Practice 'double check' pauses before clicking.",
        "Focus on accuracy over raw speed drills.",
        "Take part in self-monitoring error analysis drills."
    ],
    "Cautious Solver": [
        "Begin with structured, scaffolded matching tasks.",
        "Integrate high-contrast visual tasks to build matching confidence.",
        "Gradually build processing speed using low-distractor rows."
    ]
}


class ProcessingSpeedAssessmentService:
    _trials: dict[str, dict] = {}
    _difficulty: dict[str, int] = {}
    _streaks: dict[str, list[bool]] = {}

    def __init__(self, repository: ProcessingSpeedRepository):
        self.repository = repository

    def start(self, session_id: str, student_id: str | None) -> dict:
        self.repository.ensure_session(session_id, student_id)
        self._difficulty[session_id] = 1
        self._streaks[session_id] = []
        trial = self._next_trial(session_id, 1)
        return {"status": "success", "totalQuestions": 20, "question": self._question_payload(trial)}

    def answer(self, session_id: str, question_id: str, answer: str, duration_ms: int) -> dict:
        trial = self._trials.get(session_id)
        if trial is None or trial["id"] != question_id:
            raise HTTPException(status_code=409, detail="No active Processing Speed item matches this response.")
            
        correct = trial["correct_answer"] == answer
        trial_num = int(question_id.rsplit("-", 1)[1])
        
        self.repository.record_answer(session_id, question_id, answer, correct, duration_ms, trial["difficulty_level"])
        
        # Track streaks for adaptive difficulty scaling
        streak = self._streaks.get(session_id, [])
        streak.append(correct)
        self._streaks[session_id] = streak
        
        curr_diff = self._difficulty.get(session_id, 1)
        
        # Adaptive Scaling:
        # Promotion: Streak of 3 correct
        if len(streak) >= 3 and all(streak[-3:]):
            if curr_diff < 9:
                curr_diff += 1
        # Demotion: Streak of 2 errors
        elif len(streak) >= 2 and not streak[-1] and not streak[-2]:
            if curr_diff > 1:
                curr_diff -= 1
                
        self._difficulty[session_id] = curr_diff
        
        next_trial_num = trial_num + 1
        if next_trial_num > 20:
            return {"status": "success", "isCorrect": correct, "feedback": "Assessment completed.", "finished": True}
            
        next_trial = self._next_trial(session_id, next_trial_num)
        return {"status": "success", "isCorrect": correct, "feedback": "Duplicate identified." if correct else "Response recorded.", "nextQuestion": self._question_payload(next_trial)}

    def finish(self, session_id: str) -> dict:
        responses = self.repository.responses(session_id)
        total_trials = len(responses)
        if total_trials == 0:
            return {"status": "success", "scorePercentage": 0, "analytics": {}, "metrics": {}}

        correct_events = [r for r in responses if r.correct]
        incorrect_events = [r for r in responses if not r.correct]
        
        correct_count = len(correct_events)
        commission_errors = len([r for r in incorrect_events if getattr(r, 'response', '') != 'TIMEOUT'])
        omission_errors = len([r for r in incorrect_events if getattr(r, 'response', '') == 'TIMEOUT'])
        
        accuracy = (correct_count / total_trials) * 100
        
        # 1. Perceptual Speed (PS) — Mean reaction time of correct matches (baseline 600ms, cap 4000ms)
        correct_rts = [r.reaction_time_ms for r in correct_events if r.reaction_time_ms]
        mean_correct_rt = sum(correct_rts) / len(correct_rts) if correct_rts else 2500
        ps_score = max(0, min(100, round(100 * (1 - (mean_correct_rt - 600) / 3400))))
        
        # 2. Visual Scanning Efficiency (VSE) — Mean response time (baseline 400ms)
        all_rts = [r.reaction_time_ms for r in responses if r.reaction_time_ms]
        mean_first_click = sum(all_rts) / len(all_rts) if all_rts else 1800
        vse_score = max(0, min(100, round(100 * (1 - (mean_first_click - 400) / 3600))))
        
        # 3. Rapid Classification (RC) — Accuracy weighted by average difficulty tier achieved
        diffs = [r.difficulty_level for r in responses]
        avg_difficulty = sum(diffs) / len(diffs) if diffs else 1
        rc_score = max(0, min(100, round(accuracy * (0.8 + 0.2 * (avg_difficulty / 9)))))
        
        # 4. Speed-Accuracy Trade-off (SAT)
        speed_factor = max(0.2, min(1.0, 1 - (mean_correct_rt - 600) / 4000))
        sat_score = round(accuracy * speed_factor)
        
        # Composite Score (Balanced Accuracy + Speed Psychometric Formula)
        base_accuracy_pts = round(accuracy * 0.70)
        speed_bonus = max(0, min(30, round(30 * (1 - max(0, mean_correct_rt - 600) / 3400)))) if accuracy >= 50 else 0
        raw_composite = base_accuracy_pts + speed_bonus
        if accuracy == 100:
            raw_composite = max(85, raw_composite)
        composite_score = min(100, max(0, raw_composite))
        
        # Fatigue Slope
        half_idx = total_trials // 2
        first_half_rts = [r.reaction_time_ms for r in responses[:half_idx] if r.reaction_time_ms]
        second_half_rts = [r.reaction_time_ms for r in responses[half_idx:] if r.reaction_time_ms]
        mean_h1 = sum(first_half_rts) / len(first_half_rts) if first_half_rts else 1
        mean_h2 = sum(second_half_rts) / len(second_half_rts) if second_half_rts else 1
        fatigue_slope = round((mean_h2 - mean_h1) / mean_h1, 4) if mean_h1 > 0 else 0.0
        
        # Speed Consistency Index
        if len(correct_rts) > 1:
            variance = sum((rt - mean_correct_rt) ** 2 for rt in correct_rts) / (len(correct_rts) - 1)
            std_dev = math.sqrt(variance)
            consistency = max(0.0, min(1.0, 1 - (std_dev / mean_correct_rt))) if mean_correct_rt > 0 else 0.0
        else:
            consistency = 1.0
            
        # Archetype Mapping
        if mean_correct_rt <= 1800:
            archetype = "Efficient Scanner" if accuracy >= 85 else "Impulsive Matcher"
        else:
            archetype = "Meticulous Solver" if accuracy >= 85 else "Cautious Solver"
            
        recs = RECOMMENDATION_MAP.get(archetype, RECOMMENDATION_MAP["Efficient Scanner"])
        
        analytics = {
            "raw_score": correct_count,
            "accuracy": round(accuracy, 2),
            "perceptual_speed": ps_score,
            "visual_scanning_efficiency": vse_score,
            "rapid_classification": rc_score,
            "speed_accuracy_tradeoff": sat_score,
            "composite_score": composite_score,
            "archetype": archetype,
            "fatigue_slope": fatigue_slope,
            "speed_consistency": round(consistency, 4),
            "correct_responses": correct_count,
            "commission_errors": commission_errors,
            "omission_errors": omission_errors,
            "average_reaction_time_ms": round(mean_correct_rt, 2),
            "recommendations": recs
        }
        
        self.repository.save_result(session_id, composite_score, analytics)
        return {
            "status": "success", 
            "scorePercentage": composite_score, 
            "metrics": analytics,
            "analytics": analytics,
            "recommendations": recs
        }

    def result(self, session_id: str) -> dict:
        result = self.repository.result(session_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Processing Speed result has not been generated.")
        return {"moduleId": "processing-speed", "score": result.score_percentage, "analytics": result.payload}

    def _next_trial(self, session_id: str, number: int) -> dict:
        trial = generate_trial(number, self._difficulty.get(session_id, 1))
        self._trials[session_id] = trial
        return trial

    @staticmethod
    def _question_payload(trial: dict) -> dict:
        return {key: value for key, value in trial.items() if key != "correct_answer"}

