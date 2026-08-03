"""
==========================================================
Question Engine
==========================================================
"""

import random
from modules.quantitative.engine.item_bank import ItemBank
from modules.quantitative.engine.template_engine import TemplateEngine
from modules.quantitative.engine.exposure_engine import ExposureEngine

class QuestionEngine:

    @staticmethod
    def generate_question(level: int, db=None, session_id=None):
        templates = ItemBank.load()

        if not templates:
            raise ValueError("Question bank is empty.")

        # Try to filter by exposure rules if db and session_id are provided
        if db and session_id:
            templates = ExposureEngine.get_eligible_templates(db, session_id, templates)

        candidates = [t for t in templates if t["difficulty"] == level]

        current_level = level
        while not candidates and current_level > 1:
            current_level -= 1
            candidates = [t for t in templates if t["difficulty"] == current_level]

        if not candidates:
            candidates = templates

        selected_template = random.choice(candidates)
        return TemplateEngine.generate(selected_template)

    @staticmethod
    def generate_first_question(level: int):
        return QuestionEngine.generate_question(level)