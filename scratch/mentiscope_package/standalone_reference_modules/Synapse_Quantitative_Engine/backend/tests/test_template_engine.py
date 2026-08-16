import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.engine.template_engine import TemplateEngine


class TemplateEngineTests(unittest.TestCase):
    def test_generated_question_ids_are_unique_across_calls(self):
        template = {
            "template_id": "CB-T01",
            "module": "CompareBot",
            "difficulty": 1,
            "story_pool": ["Compare values"],
            "parameters": {"pairs": [(5, 8)]},
            "hint": "Choose the larger value",
        }

        first = TemplateEngine.generate(template)
        second = TemplateEngine.generate(template)

        self.assertNotEqual(first["question_id"], second["question_id"])


if __name__ == "__main__":
    unittest.main()
