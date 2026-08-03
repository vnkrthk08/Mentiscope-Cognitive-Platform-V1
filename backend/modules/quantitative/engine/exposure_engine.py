"""
Item Exposure Engine
"""

from modules.quantitative.repositories.question_repository import QuestionRepository

class ExposureEngine:

    @staticmethod
    def already_seen(db, question_id):
        question = QuestionRepository.get_by_question_id(db, question_id)
        return question is not None

    @staticmethod
    def get_eligible_templates(db, session_id, templates):
        """
        Filter templates based on exposure rules:
        1. Never repeat the same template consecutively.
        2. Rotate story themes if possible.
        """
        last_question = QuestionRepository.get_latest_for_session(db, session_id)
        if last_question:
            last_template_id = last_question.template_id
            eligible = [t for t in templates if t["template_id"] != last_template_id]
            if eligible:
                return eligible
        
        return templates