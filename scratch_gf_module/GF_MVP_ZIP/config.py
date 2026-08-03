"""Central, immutable configuration for the Gf assessment platform."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from models import DifficultyLevel, RuleFamily, Shape, SymbolSize


@dataclass(frozen=True, slots=True)
class DifficultyConfig:
    """Generation constraints for one assessment difficulty."""

    symbol_count: int
    rule_count: int
    example_count: int
    allowed_families: tuple[RuleFamily, ...]
    time_limit_seconds: int

    def __post_init__(self) -> None:
        if not 3 <= self.symbol_count <= 6:
            raise ValueError("symbol_count must be between 3 and 6")
        if self.rule_count < 1 or self.example_count not in range(3, 6):
            raise ValueError("Invalid rule or example count")
        if not self.allowed_families or self.time_limit_seconds <= 0:
            raise ValueError("Difficulty requires rule families and positive time")


@dataclass(frozen=True, slots=True)
class GeneratorConfig:
    """Procedural generation limits and reproducibility settings."""

    options_per_question: int = 4
    max_generation_attempts: int = 100
    default_puzzle_count: int = 12
    allow_repeated_attributes: bool = True

    def __post_init__(self) -> None:
        if self.options_per_question != 4:
            raise ValueError("The MVP requires exactly four options")
        if self.max_generation_attempts < 10 or self.default_puzzle_count < 1:
            raise ValueError("Generator limits are too small")


@dataclass(frozen=True, slots=True)
class RendererConfig:
    """Dimensions and styling used by the SVG renderer."""

    card_width: int = 360
    card_height: int = 110
    symbol_canvas_size: int = 64
    card_corner_radius: int = 12
    card_background: str = "#FFFFFF"
    card_border: str = "#D7DFEA"
    stroke_color: str = "#1F2937"
    stroke_widths: Mapping[str, float] = field(
        default_factory=lambda: {"none": 0.0, "thin": 2.0, "thick": 4.0, "dashed": 2.5}
    )
    size_scales: Mapping[SymbolSize, float] = field(
        default_factory=lambda: {
            SymbolSize.SMALL: 0.62,
            SymbolSize.MEDIUM: 0.8,
            SymbolSize.LARGE: 1.0,
        }
    )

    def __post_init__(self) -> None:
        if min(self.card_width, self.card_height, self.symbol_canvas_size) <= 0:
            raise ValueError("Renderer dimensions must be positive")
        object.__setattr__(self, "stroke_widths", MappingProxyType(dict(self.stroke_widths)))
        object.__setattr__(self, "size_scales", MappingProxyType(dict(self.size_scales)))


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Complete application configuration injected into all services."""

    shapes: tuple[Shape, ...]
    colors: tuple[str, ...]
    rotations: tuple[int, ...]
    difficulties: Mapping[DifficultyLevel, DifficultyConfig]
    rule_weights: Mapping[RuleFamily, float]
    generator: GeneratorConfig = field(default_factory=GeneratorConfig)
    renderer: RendererConfig = field(default_factory=RendererConfig)

    def __post_init__(self) -> None:
        if len(self.shapes) < 4 or len(self.colors) < 4:
            raise ValueError("At least four shapes and colors are required")
        if not self.rotations or any(not 0 <= value < 360 for value in self.rotations):
            raise ValueError("Rotations must be in the range 0 through 359")
        missing = set(DifficultyLevel) - set(self.difficulties)
        if missing:
            raise ValueError(f"Missing difficulty configurations: {missing}")
        if any(weight < 0 for weight in self.rule_weights.values()):
            raise ValueError("Rule weights cannot be negative")
        object.__setattr__(self, "difficulties", MappingProxyType(dict(self.difficulties)))
        object.__setattr__(self, "rule_weights", MappingProxyType(dict(self.rule_weights)))


DEFAULT_CONFIG = AppConfig(
    shapes=tuple(Shape),
    colors=("#E63946", "#2563EB", "#16A34A", "#F59E0B", "#7C3AED", "#0891B2"),
    rotations=(0, 45, 90, 135, 180, 225, 270, 315),
    difficulties={
        DifficultyLevel.EASY: DifficultyConfig(3, 1, 3, (RuleFamily.SEQUENCE, RuleFamily.ATTRIBUTE), 75),
        DifficultyLevel.MEDIUM: DifficultyConfig(4, 2, 4, (RuleFamily.SEQUENCE, RuleFamily.ATTRIBUTE, RuleFamily.ORDERING), 105),
        DifficultyLevel.HARD: DifficultyConfig(5, 2, 5, (RuleFamily.LOGICAL, RuleFamily.COMPOSITE, RuleFamily.ORDERING), 150),
        DifficultyLevel.EXPERT: DifficultyConfig(5, 2, 5, (RuleFamily.RELATIONAL, RuleFamily.COMPOSITE), 210),
    },
    rule_weights={
        RuleFamily.SEQUENCE: 1.0,
        RuleFamily.ATTRIBUTE: 1.0,
        RuleFamily.ORDERING: 0.75,
        RuleFamily.LOGICAL: 0.7,
        RuleFamily.COMPOSITE: 0.8,
        RuleFamily.RELATIONAL: 1.2,
        RuleFamily.MATRIX: 0.0,
    },
)


__all__ = ["AppConfig", "DEFAULT_CONFIG", "DifficultyConfig", "GeneratorConfig", "RendererConfig"]
