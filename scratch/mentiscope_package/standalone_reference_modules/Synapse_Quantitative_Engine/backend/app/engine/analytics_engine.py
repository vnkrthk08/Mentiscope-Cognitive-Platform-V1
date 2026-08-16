"""
==========================================================
Analytics Engine
==========================================================
Computes assessment analytics from StudentResponse records.
"""

from statistics import mean


class AnalyticsEngine:

    @staticmethod
    def compute(responses):

        total = len(responses)

        if total == 0:

            return {

                "common_metrics": {

                    "questions_attempted": 0,
                    "correct_answers": 0,
                    "incorrect_answers": 0,
                    "accuracy": 0,
                    "average_reaction_time": 0,
                    "average_hover_time": 0,
                    "average_idle_time": 0,
                    "average_confidence": 0,
                    "average_answer_changes": 0,
                    "hint_dependency": 0,
                    "highest_level_reached": 0,
                    "engagement_score": 0,
                    "decision_stability": 0,
                },

                "gq_metrics": {

                    "pattern_recognition_score": 0,
                    "arithmetic_reasoning_score": 0,
                    "quantitative_comparison_score": 0,
                    "problem_solving_score": 0,
                    "confidence_index": 0,
                    "learning_curve": 0,
                    "difficulty_progression": [],
                }
            }

        # -------------------------------------------------
        # Basic Counts
        # -------------------------------------------------

        correct = sum(r.correct for r in responses)

        incorrect = total - correct

        accuracy = (correct / total) * 100

        # -------------------------------------------------
        # Timing
        # -------------------------------------------------

        average_reaction = mean(
            r.reaction_time_ms for r in responses
        )

        average_hover = mean(
            r.hover_duration_ms for r in responses
        )

        average_idle = mean(
            r.idle_time_ms for r in responses
        )

        # -------------------------------------------------
        # Behaviour
        # -------------------------------------------------

        average_confidence = mean(
            r.confidence_score for r in responses
        )

        average_changes = mean(
            r.answer_changes for r in responses
        )

        hints = sum(
            r.hint_used for r in responses
        )

        highest_level = max(
            r.difficulty_level for r in responses
        )

        difficulty_progression = [
            r.difficulty_level
            for r in responses
        ]

        # -------------------------------------------------
        # Derived Scores
        # -------------------------------------------------

        hint_dependency = (
            hints / total
        ) * 100

        engagement_score = max(
            0,
            100
            - (average_idle / 100)
        )

        decision_stability = max(
            0,
            100
            - (average_changes * 10)
        )

        confidence_index = (
            average_confidence / 5
        ) * 100

        learning_curve = (
            accuracy
            + confidence_index
        ) / 2

        # -------------------------------------------------
        # GQ Domain Scores
        # -------------------------------------------------
        # Placeholder until you implement
        # question-type-based scoring.

        pattern_score = accuracy

        arithmetic_score = accuracy

        comparison_score = accuracy

        problem_solving_score = accuracy

        # -------------------------------------------------
        # Output
        # -------------------------------------------------

        return {

            "common_metrics": {

                "questions_attempted": total,

                "correct_answers": correct,

                "incorrect_answers": incorrect,

                "accuracy": round(accuracy, 2),

                "average_reaction_time": round(
                    average_reaction,
                    2,
                ),

                "average_hover_time": round(
                    average_hover,
                    2,
                ),

                "average_idle_time": round(
                    average_idle,
                    2,
                ),

                "average_confidence": round(
                    average_confidence,
                    2,
                ),

                "average_answer_changes": round(
                    average_changes,
                    2,
                ),

                "hint_dependency": round(
                    hint_dependency,
                    2,
                ),

                "highest_level_reached": highest_level,

                "engagement_score": round(
                    engagement_score,
                    2,
                ),

                "decision_stability": round(
                    decision_stability,
                    2,
                ),
            },

            "gq_metrics": {

                "pattern_recognition_score": round(
                    pattern_score,
                    2,
                ),

                "arithmetic_reasoning_score": round(
                    arithmetic_score,
                    2,
                ),

                "quantitative_comparison_score": round(
                    comparison_score,
                    2,
                ),

                "problem_solving_score": round(
                    problem_solving_score,
                    2,
                ),

                "confidence_index": round(
                    confidence_index,
                    2,
                ),

                "learning_curve": round(
                    learning_curve,
                    2,
                ),

                "difficulty_progression": difficulty_progression,
            }
        }