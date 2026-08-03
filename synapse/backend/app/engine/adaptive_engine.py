"""
==========================================================
Adaptive Engine
==========================================================
"""

class AdaptiveEngine:

    MAX_LEVEL = 5
    MIN_LEVEL = 1

    @staticmethod
    def calculate_performance_score(correct: bool, response_time: float, hint_used: bool, attempts: int) -> float:
        score = 0.0
        # Accuracy: 50%
        if correct:
            score += 50.0
            
        # Response Time: 20%
        if response_time < 20.0:
            score += 20.0
        elif response_time < 40.0:
            score += 10.0
            
        # Hint Usage: 10%
        if not hint_used:
            score += 10.0
            
        # Number of Attempts: 10%
        if attempts <= 1:
            score += 10.0
        elif attempts == 2:
            score += 5.0
            
        # Confidence (interaction quality): 10%
        # Simple heuristic for MVP
        score += 10.0
        
        return score

    @staticmethod
    def next_level(
        current_level: int,
        correct: bool,
        response_time: float,
        hint_used: bool,
        attempts: int = 1
    ):
        perf_score = AdaptiveEngine.calculate_performance_score(correct, response_time, hint_used, attempts)

        if perf_score >= 90:
            current_level += 2
        elif perf_score >= 75:
            current_level += 1
        elif perf_score >= 50:
            pass # stay
        elif perf_score >= 35:
            current_level -= 1
        else:
            current_level -= 2

        current_level = max(AdaptiveEngine.MIN_LEVEL, current_level)
        current_level = min(AdaptiveEngine.MAX_LEVEL, current_level)

        return current_level