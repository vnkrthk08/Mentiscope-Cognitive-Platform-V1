"""Procedural generation and safe cloning of symbol cards."""

from __future__ import annotations

import random
from dataclasses import replace
from uuid import uuid4

from config import AppConfig, DEFAULT_CONFIG
from models import Card, Position, Symbol
from symbol_generator import SymbolGenerator


class CardGenerator:
    """Build ordered cards while preserving domain invariants."""

    def __init__(self, config: AppConfig = DEFAULT_CONFIG, rng: random.Random | None = None) -> None:
        self.config = config
        self.rng = rng or random.Random()
        self.symbol_generator = SymbolGenerator(config, self.rng)

    def generate(self, symbol_count: int, *, positioned: bool = False) -> Card:
        """Generate a card containing three to six distinct symbols."""

        if not 3 <= symbol_count <= 6:
            raise ValueError("symbol_count must be between three and six")
        symbols = self.symbol_generator.generate_distinct(symbol_count)
        if positioned:
            symbols = tuple(
                replace(
                    symbol,
                    position=Position((index + 1) / (symbol_count + 1), 0.5),
                    symbol_id=f"symbol_{uuid4().hex}",
                )
                for index, symbol in enumerate(symbols)
            )
        return Card(symbols)

    @staticmethod
    def clone(card: Card, symbols: tuple[Symbol, ...] | None = None) -> Card:
        """Create a card with fresh card and symbol identities."""

        source = symbols if symbols is not None else card.symbols
        cloned = tuple(
            replace(symbol, symbol_id=f"symbol_{uuid4().hex}")
            for symbol in source
        )
        return Card(cloned)


__all__ = ["CardGenerator"]
