"""
==========================================================
Item Bank
==========================================================
"""

from pathlib import Path
import json


class ItemBank:
    """
    Loads assessment templates.

    Current MVP:
        Reads templates from JSON.

    Future:
        PostgreSQL
    """

    DATA_PATH = (
        Path(__file__).parent.parent
        / "data"
        / "templates.json"
    )

    @classmethod
    def load(cls):
        """Load all templates."""

        with open(cls.DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def first_template(cls):
        """Return the first template."""

        templates = cls.load()

        return templates[0]

    @classmethod
    def get_templates_by_module(cls, module: str):
        """Return all templates for a module."""

        templates = cls.load()

        return [
            t
            for t in templates
            if t["module"] == module
        ]

    @classmethod
    def get_templates_by_level(
        cls,
        module: str,
        level: int,
    ):
        """Return templates for a module and difficulty."""

        templates = cls.load()

        return [
            t
            for t in templates
            if t["module"] == module
            and t["difficulty"] == level
        ]