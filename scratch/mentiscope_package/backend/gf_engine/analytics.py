"""Behavioral analytics derived from assessment events and responses."""

from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Mapping, Sequence

from models import AnalyticsReport, Assessment, EventType, InteractionEvent


class AnalyticsEngine:
    """Convert a session event stream into interpretable reasoning metrics."""

    def analyze(self, assessment: Assessment, responses: Mapping[str, str], events: Sequence[InteractionEvent]) -> AnalyticsReport:
        correctness = [
            puzzle.question.is_correct(responses.get(puzzle.puzzle_id, ""))
            for puzzle in assessment.puzzles
        ]
        accuracy = sum(correctness) / len(correctness)
        submissions = [event for event in events if event.event_type is EventType.ANSWER_SUBMITTED]
        times = [event.reaction_time_ms / 1000 for event in submissions if event.reaction_time_ms is not None]
        discovery_time = mean(times) if times else 0.0
        changes = sum(event.event_type is EventType.OPTION_CHANGED for event in events)
        hints = sum(event.event_type is EventType.HINT_REQUESTED for event in events)
        clicks = sum(event.event_type in {EventType.OPTION_CLICKED, EventType.OPTION_CHANGED} for event in events)
        persistence = min(1.0, len(responses) / len(assessment.puzzles) + 0.05 * changes)
        exploration = min(1.0, clicks / max(1, len(assessment.puzzles) * 2))
        expected_time = sum(p.estimated_time_seconds for p in assessment.puzzles) / len(assessment.puzzles)
        time_factor = min(1.0, expected_time / max(discovery_time, 1.0))
        efficiency = accuracy * time_factor
        window = max(1, len(correctness) // 4)
        learning_curve = tuple(
            sum(correctness[i:i + window]) / len(correctness[i:i + window])
            for i in range(0, len(correctness), window)
        )
        error_patterns: Counter[str] = Counter()
        for puzzle in assessment.puzzles:
            selected = responses.get(puzzle.puzzle_id)
            if selected and not puzzle.question.is_correct(selected):
                option = next((item for item in puzzle.question.options if item.option_id == selected), None)
                label = (
                    option.misconception
                    if option is not None and option.misconception
                    else "Unclassified reasoning error"
                )
                error_patterns[label] += 1
        recommendations = self._recommendations(accuracy, efficiency, hints, error_patterns)
        progression = tuple(
            event.difficulty for event in submissions if event.difficulty is not None
        ) or tuple(p.difficulty for p in assessment.puzzles)
        return AnalyticsReport(
            accuracy=accuracy,
            rule_discovery_time_seconds=round(discovery_time, 2),
            reasoning_efficiency=round(efficiency, 3),
            persistence=round(persistence, 3),
            exploration=round(exploration, 3),
            learning_curve=learning_curve,
            difficulty_progression=progression,
            strategy_shifts=changes,
            error_patterns=dict(error_patterns),
            recommendations=recommendations,
        )

    @staticmethod
    def _recommendations(accuracy: float, efficiency: float, hints: int, errors: Counter[str]) -> tuple[str, ...]:
        items: list[str] = []
        if accuracy < 0.55:
            items.append("Compare symbol positions and attributes separately before combining the inferred rules.")
        elif accuracy >= 0.8:
            items.append("Progress to multi-step relational transformations for additional challenge.")
        if efficiency < 0.45:
            items.append("Test one candidate rule against every example before evaluating the answer options.")
        if hints:
            items.append("Practice verbalizing a candidate rule internally before requesting a hint.")
        if errors:
            items.append(f"Review this recurring pattern: {errors.most_common(1)[0][0]}.")
        return tuple(items) or ("Continue practicing across varied rule families to consolidate flexible reasoning.",)


__all__ = ["AnalyticsEngine"]
