"""Procedural symbol generation with injectable randomness."""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Any, cast
from uuid import uuid4

from .config import AppConfig, DEFAULT_CONFIG
from .models import BorderStyle, FillStyle, Position, Symbol, SymbolSize


class SymbolGenerator:
    """Generate valid symbols from central configuration."""

    def __init__(self, config: AppConfig = DEFAULT_CONFIG, rng: random.Random | None = None) -> None:
        self.config = config
        self.rng = rng or random.Random()

    def generate(self, *, position: Position | None = None) -> Symbol:
        """Create one randomly attributed symbol."""

        return Symbol(
            shape=self.rng.choice(self.config.shapes),
            color=self.rng.choice(self.config.colors),
            fill=self.rng.choice(tuple(FillStyle)),
            rotation=self.rng.choice(self.config.rotations),
            size=self.rng.choice(tuple(SymbolSize)),
            border=self.rng.choice(tuple(BorderStyle)),
            opacity=self.rng.choice((0.6, 0.8, 1.0)),
            position=position,
        )

    def generate_distinct(self, count: int) -> tuple[Symbol, ...]:
        """Create visually distinct symbols, bounded by configured attempts."""

        if not 1 <= count <= 6:
            raise ValueError("count must be between one and six")
        symbols: list[Symbol] = []
        fingerprints: set[tuple[object, ...]] = set()
        for _ in range(self.config.generator.max_generation_attempts):
            symbol = self.generate()
            fingerprint = self.fingerprint(symbol)
            if fingerprint not in fingerprints:
                symbols.append(symbol)
                fingerprints.add(fingerprint)
            if len(symbols) == count:
                return tuple(symbols)
        raise RuntimeError("Unable to generate the requested number of distinct symbols")

    def mutate(self, symbol: Symbol, **changes: object) -> Symbol:
        """Return a copy with selected attributes changed and a fresh identity."""

        allowed = {"shape", "color", "fill", "rotation", "size", "border", "opacity", "position"}
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError(f"Unsupported symbol attributes: {sorted(unknown)}")
        return cast(
            Symbol,
            replace(cast(Any, symbol), symbol_id=f"symbol_{uuid4().hex}", **changes),
        )

    @staticmethod
    def fingerprint(symbol: Symbol) -> tuple[object, ...]:
        """Return visual attributes independent of generated identity."""

        return (
            symbol.shape, symbol.color, symbol.fill, symbol.rotation, symbol.size,
            symbol.border, symbol.opacity, symbol.position,
        )


__all__ = ["SymbolGenerator"]
