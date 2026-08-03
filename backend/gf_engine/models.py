"""Core domain models for the fluid-intelligence assessment platform.

The module deliberately contains no framework, rendering, or rule-engine imports.
It is the stable domain boundary shared by generators, strategies, scoring,
analytics, persistence, and user-interface adapters.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, TypeAlias
from uuid import uuid4


JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


def _identifier(prefix: str) -> str:
    """Return a compact, collision-resistant domain identifier."""

    return f"{prefix}_{uuid4().hex}"


def _utc_now() -> datetime:
    """Return an aware UTC timestamp."""

    return datetime.now(UTC)


def _require_non_empty(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


def _freeze_mapping(values: Mapping[str, Any]) -> Mapping[str, Any]:
    """Copy a mapping so mutable caller-owned state cannot leak into a model."""

    return MappingProxyType(dict(values))


def _json_value(value: Any) -> JsonValue:
    """Convert supported domain values into JSON-compatible primitives."""

    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"Unsupported JSON value: {type(value).__name__}")


class StringEnum(str, Enum):
    """String-valued enum with readable display text."""

    def __str__(self) -> str:
        return self.value


class Shape(StringEnum):
    """Geometric symbol shapes supported by the initial renderer."""

    CIRCLE = "circle"
    TRIANGLE = "triangle"
    SQUARE = "square"
    PENTAGON = "pentagon"
    HEXAGON = "hexagon"
    DIAMOND = "diamond"
    STAR = "star"


class FillStyle(StringEnum):
    """Visual fill treatment applied to a symbol."""

    SOLID = "solid"
    OUTLINE = "outline"
    HATCHED = "hatched"


class SymbolSize(StringEnum):
    """Semantic size levels independent of renderer dimensions."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class BorderStyle(StringEnum):
    """Border treatments available to SVG symbol rendering."""

    NONE = "none"
    THIN = "thin"
    THICK = "thick"
    DASHED = "dashed"


class DifficultyLevel(StringEnum):
    """Assessment difficulty bands."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class PuzzleFormat(StringEnum):
    """Puzzle layouts supported by the extensible assessment model."""

    CARD_TRANSFORMATION = "card_transformation"
    MATRIX = "matrix"


class RuleFamily(StringEnum):
    """Cognitive transformation families used for generation and analytics."""

    SEQUENCE = "sequence"
    ATTRIBUTE = "attribute"
    ORDERING = "ordering"
    LOGICAL = "logical"
    COMPOSITE = "composite"
    RELATIONAL = "relational"
    MATRIX = "matrix"


class CognitiveAbility(StringEnum):
    """Reportable reasoning dimensions measured by puzzle rules."""

    PATTERN_RECOGNITION = "pattern_recognition"
    INDUCTIVE_REASONING = "inductive_reasoning"
    DEDUCTIVE_REASONING = "deductive_reasoning"
    LOGICAL_REASONING = "logical_reasoning"
    ABSTRACT_REASONING = "abstract_reasoning"


class AssessmentStatus(StringEnum):
    """Lifecycle states of an assessment session."""

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class EventType(StringEnum):
    """Behavioral events emitted during an assessment."""

    ASSESSMENT_STARTED = "assessment_started"
    QUESTION_STARTED = "question_started"
    OPTION_CLICKED = "option_clicked"
    OPTION_CHANGED = "option_changed"
    HINT_REQUESTED = "hint_requested"
    ANSWER_SUBMITTED = "answer_submitted"
    QUESTION_COMPLETED = "question_completed"
    ASSESSMENT_COMPLETED = "assessment_completed"


@dataclass(frozen=True, slots=True)
class Position:
    """Optional normalized position of a symbol within a two-dimensional card."""

    x: float
    y: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.x <= 1.0 or not 0.0 <= self.y <= 1.0:
            raise ValueError("Position coordinates must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, JsonValue]:
        return {"x": self.x, "y": self.y}


@dataclass(frozen=True, slots=True)
class Symbol:
    """A single configurable geometric element on a card.

    Color is stored as a configuration key or CSS color rather than an enum so
    deployments can change their palette without modifying this domain module.
    """

    shape: Shape
    color: str
    fill: FillStyle = FillStyle.SOLID
    rotation: int = 0
    size: SymbolSize = SymbolSize.MEDIUM
    border: BorderStyle = BorderStyle.THIN
    opacity: float = 1.0
    position: Position | None = None
    symbol_id: str = field(default_factory=lambda: _identifier("symbol"))

    def __post_init__(self) -> None:
        _require_non_empty(self.symbol_id, "symbol_id")
        _require_non_empty(self.color, "color")
        if not 0 <= self.rotation < 360:
            raise ValueError("rotation must be in the range 0 through 359")
        if not 0.0 <= self.opacity <= 1.0:
            raise ValueError("opacity must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, JsonValue]:
        return {key: _json_value(value) for key, value in asdict(self).items()}


@dataclass(frozen=True, slots=True)
class Card:
    """An ordered collection of symbols forming a reasoning unit."""

    symbols: tuple[Symbol, ...]
    card_id: str = field(default_factory=lambda: _identifier("card"))

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbols", tuple(self.symbols))
        _require_non_empty(self.card_id, "card_id")
        if not 3 <= len(self.symbols) <= 6:
            raise ValueError("A card must contain between 3 and 6 symbols")
        if len({symbol.symbol_id for symbol in self.symbols}) != len(self.symbols):
            raise ValueError("Symbols within a card must have unique identifiers")

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "card_id": self.card_id,
            "symbols": [_json_value(symbol) for symbol in self.symbols],
        }


@dataclass(frozen=True, slots=True)
class Example:
    """A demonstrated input-to-output transformation."""

    input_card: Card
    output_card: Card
    example_id: str = field(default_factory=lambda: _identifier("example"))

    def __post_init__(self) -> None:
        _require_non_empty(self.example_id, "example_id")

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "example_id": self.example_id,
            "input_card": self.input_card.to_dict(),
            "output_card": self.output_card.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class RuleSpec:
    """Serializable recipe from which a rule strategy can be constructed.

    ``children`` supports arbitrary composite chains. Logical strategies may
    store a condition in ``parameters`` and the applied strategy in children.
    This keeps executable behavior in ``rule_engine.py`` and data in this module.
    """

    name: str
    family: RuleFamily
    parameters: Mapping[str, Any] = field(default_factory=dict)
    children: tuple["RuleSpec", ...] = ()
    rule_id: str = field(default_factory=lambda: _identifier("rule"))

    def __post_init__(self) -> None:
        _require_non_empty(self.name, "name")
        _require_non_empty(self.rule_id, "rule_id")
        object.__setattr__(self, "parameters", _freeze_mapping(self.parameters))
        object.__setattr__(self, "children", tuple(self.children))
        if self.family is RuleFamily.COMPOSITE and not self.children:
            raise ValueError("A composite rule must contain at least one child rule")

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "family": self.family.value,
            "parameters": _json_value(self.parameters),
            "children": [_json_value(child) for child in self.children],
        }


@dataclass(frozen=True, slots=True)
class AnswerOption:
    """A candidate output card and the misconception it represents."""

    card: Card
    misconception: str | None = None
    option_id: str = field(default_factory=lambda: _identifier("option"))

    def __post_init__(self) -> None:
        _require_non_empty(self.option_id, "option_id")
        if self.misconception is not None:
            _require_non_empty(self.misconception, "misconception")

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "option_id": self.option_id,
            "card": self.card.to_dict(),
            "misconception": self.misconception,
        }


@dataclass(frozen=True, slots=True)
class Question:
    """An unseen input card with four candidate transformed outputs."""

    input_card: Card
    options: tuple[AnswerOption, ...]
    correct_option_id: str
    question_id: str = field(default_factory=lambda: _identifier("question"))

    def __post_init__(self) -> None:
        object.__setattr__(self, "options", tuple(self.options))
        _require_non_empty(self.question_id, "question_id")
        _require_non_empty(self.correct_option_id, "correct_option_id")
        if len(self.options) != 4:
            raise ValueError("A question must contain exactly four options")
        option_ids = [option.option_id for option in self.options]
        if len(set(option_ids)) != len(option_ids):
            raise ValueError("Question option identifiers must be unique")
        if self.correct_option_id not in option_ids:
            raise ValueError("correct_option_id must identify one of the options")
        card_fingerprints = {
            tuple(
                (
                    symbol.shape,
                    symbol.color,
                    symbol.fill,
                    symbol.rotation,
                    symbol.size,
                    symbol.border,
                    symbol.opacity,
                    symbol.position,
                )
                for symbol in option.card.symbols
            )
            for option in self.options
        }
        if len(card_fingerprints) != len(self.options):
            raise ValueError("Question options must contain visually distinct cards")

    @property
    def correct_option(self) -> AnswerOption:
        """Return the option designated as correct."""

        return next(
            option for option in self.options
            if option.option_id == self.correct_option_id
        )

    def is_correct(self, option_id: str) -> bool:
        """Return whether ``option_id`` is the correct response."""

        return option_id == self.correct_option_id

    def to_dict(self, *, include_answer: bool = True) -> dict[str, JsonValue]:
        data: dict[str, JsonValue] = {
            "question_id": self.question_id,
            "input_card": self.input_card.to_dict(),
            "options": [_json_value(option) for option in self.options],
        }
        if include_answer:
            data["correct_option_id"] = self.correct_option_id
        return data


@dataclass(frozen=True, slots=True)
class Puzzle:
    """A complete rule-discovery item presented to a student."""

    examples: tuple[Example, ...]
    question: Question
    hidden_rule: RuleSpec
    difficulty: DifficultyLevel
    abilities: tuple[CognitiveAbility, ...]
    format: PuzzleFormat = PuzzleFormat.CARD_TRANSFORMATION
    estimated_time_seconds: int = 90
    puzzle_id: str = field(default_factory=lambda: _identifier("puzzle"))

    def __post_init__(self) -> None:
        object.__setattr__(self, "examples", tuple(self.examples))
        object.__setattr__(self, "abilities", tuple(self.abilities))
        _require_non_empty(self.puzzle_id, "puzzle_id")
        if not 3 <= len(self.examples) <= 5:
            raise ValueError("A puzzle must contain between three and five examples")
        if not self.abilities:
            raise ValueError("A puzzle must measure at least one cognitive ability")
        if len(set(self.abilities)) != len(self.abilities):
            raise ValueError("Puzzle cognitive abilities must be unique")
        if self.estimated_time_seconds <= 0:
            raise ValueError("estimated_time_seconds must be positive")

    def to_dict(self, *, include_answer: bool = True) -> dict[str, JsonValue]:
        return {
            "puzzle_id": self.puzzle_id,
            "format": self.format.value,
            "difficulty": self.difficulty.value,
            "estimated_time_seconds": self.estimated_time_seconds,
            "abilities": [ability.value for ability in self.abilities],
            "examples": [_json_value(example) for example in self.examples],
            "question": self.question.to_dict(include_answer=include_answer),
            "hidden_rule": (
                self.hidden_rule.to_dict() if include_answer else None
            ),
        }


@dataclass(frozen=True, slots=True)
class AssessmentMetadata:
    """Versioned information describing an assessment form."""

    title: str
    version: str
    target_population: str = "Class 11-12 students"
    locale: str = "en-IN"
    generator_seed: int | None = None
    created_at: datetime = field(default_factory=_utc_now)
    metadata_id: str = field(default_factory=lambda: _identifier("metadata"))

    def __post_init__(self) -> None:
        for value, name in (
            (self.title, "title"),
            (self.version, "version"),
            (self.target_population, "target_population"),
            (self.locale, "locale"),
            (self.metadata_id, "metadata_id"),
        ):
            _require_non_empty(value, name)
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

    def to_dict(self) -> dict[str, JsonValue]:
        return {key: _json_value(value) for key, value in asdict(self).items()}


@dataclass(frozen=True, slots=True)
class Subscore:
    """Score for one cognitive ability."""

    ability: CognitiveAbility
    raw_score: float
    maximum_score: float
    normalized_score: float

    def __post_init__(self) -> None:
        if self.maximum_score <= 0:
            raise ValueError("maximum_score must be positive")
        if not 0 <= self.raw_score <= self.maximum_score:
            raise ValueError("raw_score must be between zero and maximum_score")
        if not 0 <= self.normalized_score <= 100:
            raise ValueError("normalized_score must be between 0 and 100")

    def to_dict(self) -> dict[str, JsonValue]:
        return {key: _json_value(value) for key, value in asdict(self).items()}


@dataclass(frozen=True, slots=True)
class ScoreReport:
    """Overall and ability-level results produced by the scorer."""

    raw_score: float
    maximum_score: float
    normalized_score: float
    percentile: float
    confidence_score: float
    subscores: tuple[Subscore, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "subscores", tuple(self.subscores))
        if self.maximum_score <= 0:
            raise ValueError("maximum_score must be positive")
        if not 0 <= self.raw_score <= self.maximum_score:
            raise ValueError("raw_score must be between zero and maximum_score")
        for value, name in (
            (self.normalized_score, "normalized_score"),
            (self.percentile, "percentile"),
            (self.confidence_score, "confidence_score"),
        ):
            if not 0 <= value <= 100:
                raise ValueError(f"{name} must be between 0 and 100")
        abilities = [subscore.ability for subscore in self.subscores]
        if len(set(abilities)) != len(abilities):
            raise ValueError("Subscores must contain unique cognitive abilities")

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "raw_score": self.raw_score,
            "maximum_score": self.maximum_score,
            "normalized_score": self.normalized_score,
            "percentile": self.percentile,
            "confidence_score": self.confidence_score,
            "subscores": [_json_value(item) for item in self.subscores],
        }


@dataclass(frozen=True, slots=True)
class AnalyticsReport:
    """Structured behavioral metrics and generated recommendations."""

    accuracy: float
    rule_discovery_time_seconds: float
    reasoning_efficiency: float
    persistence: float
    exploration: float
    learning_curve: tuple[float, ...] = ()
    difficulty_progression: tuple[DifficultyLevel, ...] = ()
    strategy_shifts: int = 0
    error_patterns: Mapping[str, int] = field(default_factory=dict)
    recommendations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "learning_curve", tuple(self.learning_curve))
        object.__setattr__(
            self, "difficulty_progression", tuple(self.difficulty_progression)
        )
        object.__setattr__(self, "error_patterns", _freeze_mapping(self.error_patterns))
        object.__setattr__(self, "recommendations", tuple(self.recommendations))
        for value, name in (
            (self.accuracy, "accuracy"),
            (self.reasoning_efficiency, "reasoning_efficiency"),
            (self.persistence, "persistence"),
            (self.exploration, "exploration"),
        ):
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.rule_discovery_time_seconds < 0:
            raise ValueError("rule_discovery_time_seconds cannot be negative")
        if self.strategy_shifts < 0:
            raise ValueError("strategy_shifts cannot be negative")
        if any(not 0 <= point <= 1 for point in self.learning_curve):
            raise ValueError("learning_curve values must be between 0 and 1")
        if any(count < 0 for count in self.error_patterns.values()):
            raise ValueError("error pattern counts cannot be negative")

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "accuracy": self.accuracy,
            "learning_curve": list(self.learning_curve),
            "difficulty_progression": [item.value for item in self.difficulty_progression],
            "rule_discovery_time_seconds": self.rule_discovery_time_seconds,
            "strategy_shifts": self.strategy_shifts,
            "error_patterns": _json_value(self.error_patterns),
            "reasoning_efficiency": self.reasoning_efficiency,
            "persistence": self.persistence,
            "exploration": self.exploration,
            "recommendations": list(self.recommendations),
        }


@dataclass(frozen=True, slots=True)
class InteractionEvent:
    """Immutable audit record for one student interaction."""

    event_type: EventType
    assessment_id: str
    participant_id: str
    puzzle_id: str | None = None
    question_id: str | None = None
    option_id: str | None = None
    previous_option_id: str | None = None
    reaction_time_ms: int | None = None
    difficulty: DifficultyLevel | None = None
    is_correct: bool | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=_utc_now)
    event_id: str = field(default_factory=lambda: _identifier("event"))

    def __post_init__(self) -> None:
        for value, name in (
            (self.event_id, "event_id"),
            (self.assessment_id, "assessment_id"),
            (self.participant_id, "participant_id"),
        ):
            _require_non_empty(value, name)
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        if self.reaction_time_ms is not None and self.reaction_time_ms < 0:
            raise ValueError("reaction_time_ms cannot be negative")
        object.__setattr__(self, "payload", _freeze_mapping(self.payload))

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "assessment_id": self.assessment_id,
            "participant_id": self.participant_id,
            "puzzle_id": self.puzzle_id,
            "question_id": self.question_id,
            "option_id": self.option_id,
            "previous_option_id": self.previous_option_id,
            "reaction_time_ms": self.reaction_time_ms,
            "difficulty": self.difficulty.value if self.difficulty else None,
            "is_correct": self.is_correct,
            "payload": _json_value(self.payload),
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class Assessment:
    """A generated assessment form and its optional computed outcomes."""

    metadata: AssessmentMetadata
    puzzles: tuple[Puzzle, ...]
    status: AssessmentStatus = AssessmentStatus.CREATED
    score: ScoreReport | None = None
    analytics: AnalyticsReport | None = None
    completed_at: datetime | None = None
    assessment_id: str = field(default_factory=lambda: _identifier("assessment"))

    def __post_init__(self) -> None:
        object.__setattr__(self, "puzzles", tuple(self.puzzles))
        _require_non_empty(self.assessment_id, "assessment_id")
        if not self.puzzles:
            raise ValueError("An assessment must contain at least one puzzle")
        puzzle_ids = [puzzle.puzzle_id for puzzle in self.puzzles]
        if len(set(puzzle_ids)) != len(puzzle_ids):
            raise ValueError("Assessment puzzle identifiers must be unique")
        if self.completed_at is not None and self.completed_at.tzinfo is None:
            raise ValueError("completed_at must be timezone-aware")
        completed = self.status is AssessmentStatus.COMPLETED
        if completed != (self.completed_at is not None):
            raise ValueError(
                "completed_at must be set if and only if status is completed"
            )
        if (self.score is not None or self.analytics is not None) and not completed:
            raise ValueError("Scores and analytics require a completed assessment")

    def to_dict(self, *, include_answers: bool = True) -> dict[str, JsonValue]:
        """Serialize the assessment, optionally hiding answer-sensitive data."""

        return {
            "assessment_id": self.assessment_id,
            "metadata": self.metadata.to_dict(),
            "puzzles": [
                puzzle.to_dict(include_answer=include_answers)
                for puzzle in self.puzzles
            ],
            "status": self.status.value,
            "score": self.score.to_dict() if self.score else None,
            "analytics": self.analytics.to_dict() if self.analytics else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }


@dataclass(frozen=True, slots=True)
class AssessmentSession:
    """Student-specific state and event history for an assessment attempt."""

    assessment: Assessment
    participant_id: str
    events: tuple[InteractionEvent, ...] = ()
    started_at: datetime = field(default_factory=_utc_now)
    ended_at: datetime | None = None
    session_id: str = field(default_factory=lambda: _identifier("session"))

    def __post_init__(self) -> None:
        object.__setattr__(self, "events", tuple(self.events))
        for value, name in (
            (self.session_id, "session_id"),
            (self.participant_id, "participant_id"),
        ):
            _require_non_empty(value, name)
        if self.started_at.tzinfo is None:
            raise ValueError("started_at must be timezone-aware")
        if self.ended_at is not None:
            if self.ended_at.tzinfo is None:
                raise ValueError("ended_at must be timezone-aware")
            if self.ended_at < self.started_at:
                raise ValueError("ended_at cannot precede started_at")
        for event in self.events:
            if event.assessment_id != self.assessment.assessment_id:
                raise ValueError("Every event must belong to the session assessment")
            if event.participant_id != self.participant_id:
                raise ValueError("Every event must belong to the session participant")

    @property
    def duration_seconds(self) -> float | None:
        """Return elapsed session time when the session has ended."""

        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at).total_seconds()

    def to_dict(self, *, include_answers: bool = True) -> dict[str, JsonValue]:
        return {
            "session_id": self.session_id,
            "participant_id": self.participant_id,
            "assessment": self.assessment.to_dict(include_answers=include_answers),
            "events": [_json_value(event) for event in self.events],
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.duration_seconds,
        }


__all__ = [
    "AnalyticsReport",
    "AnswerOption",
    "Assessment",
    "AssessmentMetadata",
    "AssessmentSession",
    "AssessmentStatus",
    "BorderStyle",
    "Card",
    "CognitiveAbility",
    "DifficultyLevel",
    "EventType",
    "Example",
    "FillStyle",
    "InteractionEvent",
    "JsonValue",
    "Position",
    "Puzzle",
    "PuzzleFormat",
    "Question",
    "RuleFamily",
    "RuleSpec",
    "ScoreReport",
    "Shape",
    "StringEnum",
    "Subscore",
    "Symbol",
    "SymbolSize",
]
