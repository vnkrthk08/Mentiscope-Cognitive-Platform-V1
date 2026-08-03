"""Composable card-transformation strategies and specification factory."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Any, Callable, ClassVar, Iterable, Mapping, cast
from uuid import uuid4

from config import AppConfig, DEFAULT_CONFIG
from models import (
    BorderStyle, Card, FillStyle, RuleFamily, RuleSpec, Shape, Symbol,
    SymbolSize,
)


def _new_symbol(symbol: Symbol, **changes: object) -> Symbol:
    return cast(
        Symbol,
        replace(cast(Any, symbol), symbol_id=f"symbol_{uuid4().hex}", **changes),
    )


def _new_card(symbols: Iterable[Symbol]) -> Card:
    return Card(tuple(_new_symbol(symbol) for symbol in symbols))


class RuleStrategy(ABC):
    """Strategy interface implemented by every executable card rule."""

    name: str
    family: ClassVar[RuleFamily]

    @abstractmethod
    def apply(self, card: Card) -> Card:
        """Transform a card without mutating the input."""

    def to_spec(self) -> RuleSpec:
        return RuleSpec(self.name, self.family)


class SequenceRule(RuleStrategy):
    """Reorder or duplicate card positions using a named operation."""

    family = RuleFamily.SEQUENCE
    _OPERATIONS: ClassVar[Mapping[str, Callable[[tuple[Symbol, ...]], tuple[Symbol, ...]]]] = {
        "rotate_left": lambda s: s[1:] + s[:1],
        "rotate_right": lambda s: s[-1:] + s[:-1],
        "reverse": lambda s: tuple(reversed(s)),
        "mirror": lambda s: tuple(reversed(s)),
        "swap_ends": lambda s: s[-1:] + s[1:-1] + s[:1],
        "move_first_to_end": lambda s: s[1:] + s[:1],
        "move_last_to_front": lambda s: s[-1:] + s[:-1],
        "duplicate_first": lambda s: s + s[:1],
        "duplicate_last": lambda s: s + s[-1:],
        "alternate_positions": lambda s: s[::2] + s[1::2],
    }

    def __init__(self, operation: str) -> None:
        if operation not in self._OPERATIONS:
            raise ValueError(f"Unknown sequence operation: {operation}")
        self.name = operation

    def apply(self, card: Card) -> Card:
        if self.name.startswith("duplicate") and len(card.symbols) == 6:
            raise ValueError("Cannot duplicate a symbol on a six-symbol card")
        return _new_card(self._OPERATIONS[self.name](card.symbols))


class AttributeRule(RuleStrategy):
    """Apply one configured attribute transformation to every symbol."""

    family = RuleFamily.ATTRIBUTE

    def __init__(self, operation: str, config: AppConfig = DEFAULT_CONFIG, step: int = 1) -> None:
        valid = {"color_shift", "shape_shift", "fill_toggle", "increase_size", "decrease_size", "rotate_shape", "border_toggle", "opacity_change"}
        if operation not in valid:
            raise ValueError(f"Unknown attribute operation: {operation}")
        if step == 0:
            raise ValueError("step cannot be zero")
        self.name, self.config, self.step = operation, config, step

    @staticmethod
    def _shift(value: object, values: tuple[object, ...], step: int) -> object:
        return values[(values.index(value) + step) % len(values)]

    def _transform(self, symbol: Symbol) -> Symbol:
        if self.name == "color_shift":
            return _new_symbol(symbol, color=self._shift(symbol.color, self.config.colors, self.step))
        if self.name == "shape_shift":
            return _new_symbol(symbol, shape=self._shift(symbol.shape, self.config.shapes, self.step))
        if self.name == "fill_toggle":
            target = FillStyle.OUTLINE if symbol.fill is FillStyle.SOLID else FillStyle.SOLID
            return _new_symbol(symbol, fill=target)
        if self.name in {"increase_size", "decrease_size"}:
            sizes = tuple(SymbolSize)
            direction = 1 if self.name == "increase_size" else -1
            index = max(0, min(len(sizes) - 1, sizes.index(symbol.size) + direction))
            return _new_symbol(symbol, size=sizes[index])
        if self.name == "rotate_shape":
            return _new_symbol(symbol, rotation=(symbol.rotation + 90 * self.step) % 360)
        if self.name == "border_toggle":
            border = BorderStyle.NONE if symbol.border is not BorderStyle.NONE else BorderStyle.THIN
            return _new_symbol(symbol, border=border)
        opacity = {1.0: 0.6, 0.8: 1.0, 0.6: 0.8}.get(symbol.opacity, 1.0)
        return _new_symbol(symbol, opacity=opacity)

    def apply(self, card: Card) -> Card:
        return Card(tuple(self._transform(symbol) for symbol in card.symbols))

    def to_spec(self) -> RuleSpec:
        return RuleSpec(self.name, self.family, {"step": self.step})


class OrderingRule(RuleStrategy):
    """Sort symbols by a stable visual attribute."""

    family = RuleFamily.ORDERING

    def __init__(self, attribute: str, config: AppConfig = DEFAULT_CONFIG) -> None:
        if attribute not in {"size", "shape", "color", "rotation"}:
            raise ValueError(f"Unsupported ordering attribute: {attribute}")
        self.attribute, self.config = attribute, config
        self.name = f"sort_by_{attribute}"

    def apply(self, card: Card) -> Card:
        size_order = {value: i for i, value in enumerate(SymbolSize)}
        shape_order = {value: i for i, value in enumerate(self.config.shapes)}
        color_order = {value: i for i, value in enumerate(self.config.colors)}
        if self.attribute == "size":
            ordered = sorted(card.symbols, key=lambda symbol: size_order[symbol.size])
        elif self.attribute == "shape":
            ordered = sorted(card.symbols, key=lambda symbol: shape_order[symbol.shape])
        elif self.attribute == "color":
            ordered = sorted(card.symbols, key=lambda symbol: color_order[symbol.color])
        else:
            ordered = sorted(card.symbols, key=lambda symbol: symbol.rotation)
        return _new_card(ordered)

    def to_spec(self) -> RuleSpec:
        return RuleSpec(self.name, self.family, {"attribute": self.attribute})


class ConditionalRule(RuleStrategy):
    """Apply a child strategy only when a card-level predicate is true."""

    family = RuleFamily.LOGICAL

    def __init__(self, condition: str, child: RuleStrategy, value: str | None = None) -> None:
        valid = {"first_is_color", "last_is_shape", "majority_is_color", "any_size"}
        if condition not in valid or value is None:
            raise ValueError("Conditional rules require a supported condition and value")
        self.condition, self.child, self.value = condition, child, value
        self.name = f"if_{condition}"

    def _matches(self, card: Card) -> bool:
        if self.condition == "first_is_color":
            return card.symbols[0].color == self.value
        if self.condition == "last_is_shape":
            return card.symbols[-1].shape.value == self.value
        if self.condition == "majority_is_color":
            return sum(s.color == self.value for s in card.symbols) > len(card.symbols) / 2
        return any(s.size.value == self.value for s in card.symbols)

    def apply(self, card: Card) -> Card:
        return self.child.apply(card) if self._matches(card) else _new_card(card.symbols)

    def to_spec(self) -> RuleSpec:
        return RuleSpec(self.name, self.family, {"condition": self.condition, "value": self.value}, (self.child.to_spec(),))


class CompositeRule(RuleStrategy):
    """Apply an arbitrary non-empty chain of strategies in order."""

    name, family = "composite", RuleFamily.COMPOSITE

    def __init__(self, rules: Iterable[RuleStrategy]) -> None:
        self.rules = tuple(rules)
        if not self.rules:
            raise ValueError("CompositeRule requires at least one child")

    def apply(self, card: Card) -> Card:
        result = card
        for rule in self.rules:
            result = rule.apply(result)
        return result

    def to_spec(self) -> RuleSpec:
        return RuleSpec(self.name, self.family, children=tuple(rule.to_spec() for rule in self.rules))


class RelationalRule(RuleStrategy):
    """Transform symbols according to relationships within the card."""

    family = RuleFamily.RELATIONAL

    def __init__(self, operation: str, config: AppConfig = DEFAULT_CONFIG) -> None:
        valid = {"third_inherits_first_shape_second_color", "last_opposite_first_rotation", "largest_to_front", "alternate_copy_previous_fill", "fewest_sides_changes_color"}
        if operation not in valid:
            raise ValueError(f"Unknown relational operation: {operation}")
        self.name, self.config = operation, config

    def apply(self, card: Card) -> Card:
        symbols = list(card.symbols)
        if self.name == "third_inherits_first_shape_second_color":
            symbols[2] = _new_symbol(symbols[2], shape=symbols[0].shape, color=symbols[1].color)
        elif self.name == "last_opposite_first_rotation":
            symbols[-1] = _new_symbol(symbols[-1], rotation=(symbols[0].rotation + 180) % 360)
        elif self.name == "largest_to_front":
            rank = {size: index for index, size in enumerate(SymbolSize)}
            index = max(range(len(symbols)), key=lambda i: rank[symbols[i].size])
            symbols.insert(0, symbols.pop(index))
        elif self.name == "alternate_copy_previous_fill":
            for index in range(1, len(symbols), 2):
                symbols[index] = _new_symbol(symbols[index], fill=symbols[index - 1].fill)
        else:
            sides = {Shape.CIRCLE: 0, Shape.TRIANGLE: 3, Shape.SQUARE: 4, Shape.DIAMOND: 4, Shape.PENTAGON: 5, Shape.HEXAGON: 6, Shape.STAR: 10}
            index = min(range(len(symbols)), key=lambda i: sides[symbols[i].shape])
            color_index = (self.config.colors.index(symbols[index].color) + 1) % len(self.config.colors)
            symbols[index] = _new_symbol(symbols[index], color=self.config.colors[color_index])
        return _new_card(symbols)


class RuleFactory:
    """Construct rule strategies from stable serializable specifications."""

    def __init__(self, config: AppConfig = DEFAULT_CONFIG) -> None:
        self.config = config

    def create(self, spec: RuleSpec) -> RuleStrategy:
        params = spec.parameters
        if spec.family is RuleFamily.SEQUENCE:
            return SequenceRule(spec.name)
        if spec.family is RuleFamily.ATTRIBUTE:
            return AttributeRule(spec.name, self.config, int(params.get("step", 1)))
        if spec.family is RuleFamily.ORDERING:
            return OrderingRule(str(params.get("attribute", spec.name.removeprefix("sort_by_"))), self.config)
        if spec.family is RuleFamily.RELATIONAL:
            return RelationalRule(spec.name, self.config)
        if spec.family is RuleFamily.COMPOSITE:
            return CompositeRule(self.create(child) for child in spec.children)
        if spec.family is RuleFamily.LOGICAL:
            if len(spec.children) != 1:
                raise ValueError("A logical rule requires exactly one child")
            return ConditionalRule(str(params["condition"]), self.create(spec.children[0]), str(params["value"]))
        raise ValueError("Matrix rules are reserved for a future strategy implementation")


__all__ = ["AttributeRule", "CompositeRule", "ConditionalRule", "OrderingRule", "RelationalRule", "RuleFactory", "RuleStrategy", "SequenceRule"]
