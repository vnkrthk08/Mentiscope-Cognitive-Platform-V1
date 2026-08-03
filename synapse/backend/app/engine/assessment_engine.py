"""
Assessment Engine
"""

from app.engine.question_engine import QuestionEngine

class AssessmentEngine:

    @staticmethod
    def start(level: int, db=None, session_id=None):
        return QuestionEngine.generate_question(level, db, session_id)