"""Transparent scoring for assessment responses and cognitive subscores."""

from __future__ import annotations

from collections import defaultdict
from math import erf, sqrt
from typing import Mapping, Sequence

from .models import Assessment, CognitiveAbility, EventType, InteractionEvent, ScoreReport, Subscore


class AssessmentScorer:
    """Compute weighted raw, normalized, percentile, and confidence scores."""

    _WEIGHTS = {"easy": 1.0, "medium": 1.25, "hard": 1.6, "expert": 2.0}

    def score(
        self, assessment: Assessment, responses: Mapping[str, str],
        events: Sequence[InteractionEvent] = (),
    ) -> ScoreReport:
        if not set(responses).issubset({p.puzzle_id for p in assessment.puzzles}):
            raise ValueError("responses contains an unknown puzzle identifier")
        earned = maximum = 0.0
        ability_earned: dict[CognitiveAbility, float] = defaultdict(float)
        ability_maximum: dict[CognitiveAbility, float] = defaultdict(float)
        for puzzle in assessment.puzzles:
            weight = self._WEIGHTS[puzzle.difficulty.value]
            maximum += weight
            correct = puzzle.question.is_correct(responses.get(puzzle.puzzle_id, ""))
            earned += weight if correct else 0.0
            share = weight / len(puzzle.abilities)
            for ability in puzzle.abilities:
                ability_maximum[ability] += share
                ability_earned[ability] += share if correct else 0.0
        normalized = min(100.0, max(0.0, 100 * earned / maximum))
        percentile = self._percentile(normalized)
        confidence = self._confidence(assessment, responses, events)
        subscores = tuple(
            Subscore(
                ability,
                min(value, max(0.0, ability_earned[ability])),
                value,
                min(100.0, max(0.0, 100 * ability_earned[ability] / value)),
            )
            for ability, value in sorted(ability_maximum.items(), key=lambda item: item[0].value)
        )
        return ScoreReport(earned, maximum, normalized, percentile, confidence, subscores)

    @staticmethod
    def _percentile(normalized: float) -> float:
        """Map scores onto an MVP reference distribution pending norming data."""

        z_score = (normalized - 60.0) / 18.0
        return round(100 * 0.5 * (1 + erf(z_score / sqrt(2))), 1)

    @staticmethod
    def _confidence(assessment: Assessment, responses: Mapping[str, str], events: Sequence[InteractionEvent]) -> float:
        completion = len(responses) / len(assessment.puzzles)
        submissions = [event for event in events if event.event_type is EventType.ANSWER_SUBMITTED]
        timed = [event for event in submissions if event.reaction_time_ms is not None and event.reaction_time_ms >= 1_000]
        timing_quality = len(timed) / len(submissions) if submissions else 0.5
        changes = sum(event.event_type is EventType.OPTION_CHANGED for event in events)
        stability = max(0.0, 1.0 - changes / max(1, len(assessment.puzzles) * 2))
        return round(100 * (0.55 * completion + 0.25 * timing_quality + 0.2 * stability), 1)


__all__ = ["AssessmentScorer"]
