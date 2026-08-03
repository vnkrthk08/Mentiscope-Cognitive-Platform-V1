"""Dependency-free SVG rendering for symbols, cards, and puzzle rows."""

from __future__ import annotations

from html import escape
from math import cos, pi, sin

from config import AppConfig, DEFAULT_CONFIG
from models import BorderStyle, Card, FillStyle, Shape, Symbol


class SVGRenderer:
    """Render accessible, transparent SVG graphics from geometric primitives."""

    def __init__(self, config: AppConfig = DEFAULT_CONFIG) -> None:
        self.config = config

    @staticmethod
    def _polygon_points(sides: int, radius: float = 24, start: float = -pi / 2) -> str:
        return " ".join(
            f"{32 + radius * cos(start + 2 * pi * i / sides):.2f},{32 + radius * sin(start + 2 * pi * i / sides):.2f}"
            for i in range(sides)
        )

    @staticmethod
    def _star_points() -> str:
        values = []
        for index in range(10):
            radius = 25 if index % 2 == 0 else 11
            angle = -pi / 2 + index * pi / 5
            values.append(f"{32 + radius * cos(angle):.2f},{32 + radius * sin(angle):.2f}")
        return " ".join(values)

    def _primitive(self, shape: Shape) -> str:
        if shape is Shape.CIRCLE:
            return '<circle cx="32" cy="32" r="24"'
        if shape is Shape.SQUARE:
            return '<rect x="9" y="9" width="46" height="46" rx="3"'
        if shape is Shape.DIAMOND:
            return f'<polygon points="{self._polygon_points(4, start=0)}"'
        if shape is Shape.STAR:
            return f'<polygon points="{self._star_points()}"'
        sides = {Shape.TRIANGLE: 3, Shape.PENTAGON: 5, Shape.HEXAGON: 6}[shape]
        return f'<polygon points="{self._polygon_points(sides)}"'

    def render_symbol(self, symbol: Symbol, *, x: float = 0, y: float = 0) -> str:
        """Return an SVG group for one symbol at the requested origin."""

        cfg = self.config.renderer
        scale = cfg.size_scales[symbol.size]
        base_stroke = cfg.stroke_widths.get(symbol.border.value, 2.0)
        stroke_width = max(2.0, base_stroke)
        fill = "none" if symbol.fill is FillStyle.OUTLINE else escape(symbol.color)
        dash = ' stroke-dasharray="6 4"' if symbol.border is BorderStyle.DASHED else ""
        pattern_id = f"hatch-{escape(symbol.symbol_id)}"
        hatch = ""
        if symbol.fill is FillStyle.HATCHED:
            hatch = (
                f'<defs><pattern id="{pattern_id}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                f'<rect width="7" height="7" fill="none"/><line x1="0" y1="0" x2="0" y2="7" stroke="{escape(symbol.color)}" stroke-width="2.5"/></pattern></defs>'
            )
            fill = f"url(#{pattern_id})"
        primitive = self._primitive(symbol.shape)
        stroke_color = escape(symbol.color) if symbol.fill is FillStyle.OUTLINE else escape(cfg.stroke_color)
        opacity = max(0.8, symbol.opacity)
        return (
            f'<g transform="translate({x:.2f} {y:.2f})">{hatch}'
            f'<g transform="rotate({symbol.rotation} 32 32) translate({32 * (1 - scale):.2f} {32 * (1 - scale):.2f}) scale({scale:.3f})">'
            f'{primitive} fill="{fill}" stroke="{stroke_color}" stroke-width="{stroke_width}" opacity="{opacity:.2f}"{dash}/></g></g>'
        )

    def render_card(self, card: Card, *, aria_label: str = "Symbol card") -> str:
        """Render a complete responsive card as standalone SVG."""

        cfg = self.config.renderer
        available = cfg.card_width - 32
        spacing = available / len(card.symbols)
        symbols = "".join(
            self.render_symbol(symbol, x=16 + index * spacing + (spacing - 64) / 2, y=(cfg.card_height - 64) / 2)
            for index, symbol in enumerate(card.symbols)
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {cfg.card_width} {cfg.card_height}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="{escape(aria_label)}" style="width:100%;height:100%;display:block">'
            f'<rect x="1" y="1" width="{cfg.card_width - 2}" height="{cfg.card_height - 2}" rx="{cfg.card_corner_radius}" fill="{escape(cfg.card_background)}" stroke="{escape(cfg.card_border)}" stroke-width="2"/>{symbols}</svg>'
        )


__all__ = ["SVGRenderer"]
