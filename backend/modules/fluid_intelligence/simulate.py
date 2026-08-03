"""Synthetic student simulation for pre-collection analytics validation."""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Iterator

from .analytics import AnalyticsEngine
from .config import DEFAULT_CONFIG
from .models import EventType, InteractionEvent
from .puzzle_engine import AssessmentBuilder
from .scorer import AssessmentScorer


@dataclass(frozen=True, slots=True)
class StudentProfile:
    """Latent traits controlling simulated response behavior."""

    ability: float
    persistence: float
    deliberation: float
    change_tendency: float


class StudentSimulator:
    """Generate plausible sessions using difficulty-sensitive response curves."""

    _DIFFICULTY = {"easy": 0.25, "medium": 0.45, "hard": 0.65, "expert": 0.82}

    def __init__(self, seed: int = 2026) -> None:
        self.rng = random.Random(seed)
        self.assessment = AssessmentBuilder(DEFAULT_CONFIG, seed).with_progression().build()

    def profile(self) -> StudentProfile:
        return StudentProfile(
            ability=min(1.0, max(0.0, self.rng.gauss(0.58, 0.18))),
            persistence=self.rng.uniform(0.72, 1.0),
            deliberation=self.rng.lognormvariate(0.0, 0.28),
            change_tendency=self.rng.uniform(0.05, 0.35),
        )

    def simulate(self, participant_id: str) -> dict[str, object]:
        profile = self.profile()
        responses: dict[str, str] = {}
        events: list[InteractionEvent] = []
        clock = datetime.now(UTC)
        for puzzle in self.assessment.puzzles:
            if self.rng.random() > profile.persistence:
                break
            question = puzzle.question
            baseline = self._DIFFICULTY[puzzle.difficulty.value]
            probability = 0.25 + 0.72 / (1 + pow(2.71828, -8 * (profile.ability - baseline)))
            correct = self.rng.random() < probability
            wrong = [option for option in question.options if option.option_id != question.correct_option_id]
            selected = question.correct_option if correct else self.rng.choice(wrong)
            reaction_ms = int(self.rng.uniform(18_000, puzzle.estimated_time_seconds * 900) * profile.deliberation)
            events.append(InteractionEvent(EventType.QUESTION_STARTED, self.assessment.assessment_id, participant_id, puzzle.puzzle_id, question.question_id, timestamp=clock))
            if self.rng.random() < profile.change_tendency:
                initial = self.rng.choice(wrong)
                events.append(InteractionEvent(EventType.OPTION_CLICKED, self.assessment.assessment_id, participant_id, puzzle.puzzle_id, question.question_id, initial.option_id, reaction_time_ms=reaction_ms // 2, difficulty=puzzle.difficulty, timestamp=clock + timedelta(milliseconds=reaction_ms // 2)))
                events.append(InteractionEvent(EventType.OPTION_CHANGED, self.assessment.assessment_id, participant_id, puzzle.puzzle_id, question.question_id, selected.option_id, initial.option_id, reaction_ms, puzzle.difficulty, timestamp=clock + timedelta(milliseconds=reaction_ms)))
            events.append(InteractionEvent(EventType.ANSWER_SUBMITTED, self.assessment.assessment_id, participant_id, puzzle.puzzle_id, question.question_id, selected.option_id, reaction_time_ms=reaction_ms, difficulty=puzzle.difficulty, is_correct=correct, timestamp=clock + timedelta(milliseconds=reaction_ms)))
            responses[puzzle.puzzle_id] = selected.option_id
            clock += timedelta(milliseconds=reaction_ms + self.rng.randint(500, 2_500))
        score = AssessmentScorer().score(self.assessment, responses, events)
        analytics = AnalyticsEngine().analyze(self.assessment, responses, events)
        return {
            "participant_id": participant_id,
            "profile": {"ability": profile.ability, "persistence": profile.persistence, "deliberation": profile.deliberation, "change_tendency": profile.change_tendency},
            "responses": responses,
            "events": [event.to_dict() for event in events],
            "score": score.to_dict(),
            "analytics": analytics.to_dict(),
        }

    def generate(self, count: int = 1_000) -> Iterator[dict[str, object]]:
        if count < 1:
            raise ValueError("count must be positive")
        for index in range(count):
            yield self.simulate(f"simulated_{index + 1:05d}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic Gf assessment sessions")
    parser.add_argument("--count", type=int, default=1_000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output", type=Path, default=Path("simulated_sessions.jsonl"))
    args = parser.parse_args()
    simulator = StudentSimulator(args.seed)
    with args.output.open("w", encoding="utf-8") as stream:
        for session in simulator.generate(args.count):
            stream.write(json.dumps(session, ensure_ascii=False) + "\n")
    print(f"Generated {args.count} sessions at {args.output.resolve()}")


if __name__ == "__main__":
    main()


__all__ = ["StudentProfile", "StudentSimulator"]
