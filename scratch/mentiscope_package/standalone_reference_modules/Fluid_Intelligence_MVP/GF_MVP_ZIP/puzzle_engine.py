"""Procedural puzzle and assessment generation with plausible distractors."""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Iterable
from uuid import uuid4

from card_generator import CardGenerator
from config import AppConfig, DEFAULT_CONFIG
from difficulty import DifficultyManager
from models import (
    AnswerOption, Assessment, AssessmentMetadata, Card, CognitiveAbility,
    DifficultyLevel, Example, Puzzle, Question, RuleFamily,
)
from rule_engine import (
    AttributeRule, CompositeRule, ConditionalRule, OrderingRule,
    RelationalRule, RuleStrategy, SequenceRule,
)


def _fingerprint(card: Card) -> tuple[tuple[object, ...], ...]:
    return tuple(
        (s.shape, s.color, s.fill, s.rotation, s.size, s.border, s.opacity, s.position)
        for s in card.symbols
    )


class DistractorGenerator:
    """Generate wrong answers tied to interpretable reasoning errors."""

    def __init__(self, config: AppConfig, rng: random.Random) -> None:
        self.config, self.rng = config, rng

    def generate(self, input_card: Card, correct: Card, rule: RuleStrategy, count: int = 3) -> tuple[AnswerOption, ...]:
        candidates: list[tuple[str, Card]] = []
        alternatives: tuple[tuple[str, RuleStrategy], ...] = (
            ("Applied the transformation in the opposite direction", SequenceRule("rotate_right")),
            ("Reversed the symbol order", SequenceRule("reverse")),
            ("Left the card unchanged", SequenceRule("alternate_positions")),
            ("Changed color but missed the structural rule", AttributeRule("color_shift", self.config)),
            ("Rotated shapes but preserved positions", AttributeRule("rotate_shape", self.config)),
            ("Sorted by size instead of inferring the rule", OrderingRule("size", self.config)),
        )
        seen = {_fingerprint(correct)}
        for label, alternative in alternatives:
            card = alternative.apply(input_card)
            fingerprint = _fingerprint(card)
            if fingerprint not in seen:
                candidates.append((label, card))
                seen.add(fingerprint)
            if len(candidates) == count:
                break
        attempts = 0
        while len(candidates) < count and attempts < self.config.generator.max_generation_attempts:
            attempts += 1
            symbols = list(input_card.symbols)
            index = attempts % len(symbols)
            current = symbols[index]
            color = self.config.colors[(self.config.colors.index(current.color) + attempts) % len(self.config.colors)]
            symbols[index] = replace(current, color=color, symbol_id=f"symbol_{uuid4().hex}")
            card = Card(tuple(replace(s, symbol_id=f"symbol_{uuid4().hex}") for s in symbols))
            fingerprint = _fingerprint(card)
            if fingerprint not in seen:
                candidates.append(("Applied the inferred rule to the wrong symbol", card))
                seen.add(fingerprint)
        if len(candidates) != count:
            raise RuntimeError("Unable to construct distinct plausible distractors")
        return tuple(AnswerOption(card, label) for label, card in candidates)


class PuzzleGenerator:
    """Generate complete, validated rule-discovery puzzles."""

    def __init__(self, config: AppConfig = DEFAULT_CONFIG, seed: int | None = None) -> None:
        self.config = config
        self.rng = random.Random(seed)
        self.cards = CardGenerator(config, self.rng)
        self.difficulty = DifficultyManager(config)
        self.distractors = DistractorGenerator(config, self.rng)

    def _rule_for(self, level: DifficultyLevel) -> RuleStrategy:
        sequences = ("rotate_left", "rotate_right", "reverse", "swap_ends", "alternate_positions")
        attributes = ("color_shift", "shape_shift", "fill_toggle", "rotate_shape", "border_toggle")
        relations = ("third_inherits_first_shape_second_color", "last_opposite_first_rotation", "largest_to_front", "alternate_copy_previous_fill", "fewest_sides_changes_color")
        if level is DifficultyLevel.EASY:
            if self.rng.random() < 0.55:
                return SequenceRule(self.rng.choice(sequences))
            return AttributeRule(self.rng.choice(attributes), self.config)
        if level is DifficultyLevel.MEDIUM:
            return CompositeRule((SequenceRule(self.rng.choice(sequences)), AttributeRule(self.rng.choice(attributes), self.config)))
        if level is DifficultyLevel.HARD:
            child = self.rng.choice((SequenceRule("reverse"), AttributeRule("fill_toggle", self.config)))
            return ConditionalRule("first_is_color", child, self.rng.choice(self.config.colors))
        return CompositeRule((RelationalRule(self.rng.choice(relations), self.config), RelationalRule(self.rng.choice(relations), self.config)))

    def _meaningful_pair(self, symbol_count: int, rule: RuleStrategy) -> tuple[Card, Card]:
        for _ in range(self.config.generator.max_generation_attempts):
            source = self.cards.generate(symbol_count)
            output = rule.apply(source)
            if _fingerprint(source) != _fingerprint(output):
                return source, output
        raise RuntimeError("Unable to generate a card demonstrating the selected rule")

    @staticmethod
    def _abilities(rule: RuleStrategy) -> tuple[CognitiveAbility, ...]:
        mapping = {
            RuleFamily.SEQUENCE: (CognitiveAbility.PATTERN_RECOGNITION, CognitiveAbility.INDUCTIVE_REASONING),
            RuleFamily.ATTRIBUTE: (CognitiveAbility.PATTERN_RECOGNITION, CognitiveAbility.ABSTRACT_REASONING),
            RuleFamily.ORDERING: (CognitiveAbility.INDUCTIVE_REASONING,),
            RuleFamily.LOGICAL: (CognitiveAbility.DEDUCTIVE_REASONING, CognitiveAbility.LOGICAL_REASONING),
            RuleFamily.COMPOSITE: (CognitiveAbility.INDUCTIVE_REASONING, CognitiveAbility.LOGICAL_REASONING),
            RuleFamily.RELATIONAL: (CognitiveAbility.ABSTRACT_REASONING, CognitiveAbility.LOGICAL_REASONING),
        }
        return mapping[rule.family]

    def generate(self, level: DifficultyLevel) -> Puzzle:
        """Generate examples, question, answer, and three diagnostic distractors."""

        settings = self.difficulty.settings_for(level)
        rule = self._rule_for(level)
        examples = tuple(
            Example(*self._meaningful_pair(settings.symbol_count, rule))
            for _ in range(settings.example_count)
        )
        question_input, correct_card = self._meaningful_pair(settings.symbol_count, rule)
        correct = AnswerOption(correct_card)
        options = list(self.distractors.generate(question_input, correct_card, rule)) + [correct]
        self.rng.shuffle(options)
        question = Question(question_input, tuple(options), correct.option_id)
        return Puzzle(
            examples, question, rule.to_spec(), level, self._abilities(rule),
            estimated_time_seconds=settings.time_limit_seconds,
        )


class AssessmentBuilder:
    """Builder for reproducible, progressively difficult assessment forms."""

    def __init__(self, config: AppConfig = DEFAULT_CONFIG, seed: int | None = None) -> None:
        self.config, self.seed = config, seed
        self._title, self._version = "Fluid Intelligence Assessment", "1.0.0"
        self._levels: list[DifficultyLevel] = []

    def with_identity(self, title: str, version: str) -> "AssessmentBuilder":
        self._title, self._version = title, version
        return self

    def with_difficulties(self, levels: Iterable[DifficultyLevel]) -> "AssessmentBuilder":
        self._levels = list(levels)
        if not self._levels:
            raise ValueError("At least one difficulty is required")
        return self

    def with_progression(self, puzzle_count: int | None = None) -> "AssessmentBuilder":
        count = puzzle_count or self.config.generator.default_puzzle_count
        self._levels = list(DifficultyManager(self.config).build_plan(count))
        return self

    def build(self) -> Assessment:
        if not self._levels:
            self.with_progression()
        generator = PuzzleGenerator(self.config, self.seed)
        metadata = AssessmentMetadata(self._title, self._version, generator_seed=self.seed)
        return Assessment(metadata, tuple(generator.generate(level) for level in self._levels))


__all__ = ["AssessmentBuilder", "DistractorGenerator", "PuzzleGenerator"]
