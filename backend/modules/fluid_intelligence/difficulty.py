"""Difficulty policies and balanced assessment sequencing."""

from __future__ import annotations

from .config import AppConfig, DEFAULT_CONFIG, DifficultyConfig
from .models import DifficultyLevel


class DifficultyManager:
    """Resolve generation settings and construct progressive difficulty plans."""

    _ORDER = tuple(DifficultyLevel)

    def __init__(self, config: AppConfig = DEFAULT_CONFIG) -> None:
        self.config = config

    def settings_for(self, level: DifficultyLevel) -> DifficultyConfig:
        return self.config.difficulties[level]

    def next_level(self, current: DifficultyLevel, accuracy: float) -> DifficultyLevel:
        """Adapt one band based on recent accuracy, avoiding abrupt jumps."""

        if not 0 <= accuracy <= 1:
            raise ValueError("accuracy must be between zero and one")
        index = self._ORDER.index(current)
        if accuracy >= 0.8 and index < len(self._ORDER) - 1:
            return self._ORDER[index + 1]
        if accuracy < 0.45 and index > 0:
            return self._ORDER[index - 1]
        return current

    def build_plan(self, puzzle_count: int) -> tuple[DifficultyLevel, ...]:
        """Return a deterministic easy-to-expert progression."""

        if puzzle_count < 1:
            raise ValueError("puzzle_count must be positive")
        return tuple(
            self._ORDER[min(index * len(self._ORDER) // puzzle_count, len(self._ORDER) - 1)]
            for index in range(puzzle_count)
        )


__all__ = ["DifficultyManager"]
