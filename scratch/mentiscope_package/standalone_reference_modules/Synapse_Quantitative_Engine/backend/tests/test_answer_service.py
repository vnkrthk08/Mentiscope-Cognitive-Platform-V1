import os
import sys
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.base import Base
from app.models.question_instance import QuestionInstance
from app.models.session import AssessmentSession
from app.repositories.question_repository import QuestionRepository
from app.repositories.session_repository import SessionRepository
from app.schemas.answer import AnswerRequest
from app.services.answer_service import AnswerService


class AnswerServiceTests(unittest.TestCase):
    def test_submit_answer_updates_session_level(self):
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        SessionFactory = sessionmaker(bind=engine)
        db = SessionFactory()

        try:
            session = AssessmentSession(
                student_id='student-1',
                session_id='session-1',
                module_id='GQ01',
                construct='Gq',
                current_level=2,
            )
            session = SessionRepository.create(db, session)

            question = QuestionInstance(
                session_id=session.id,
                question_id='q-001',
                template_id='PB-T01',
                module='PatternBot',
                difficulty=2,
                question_json={'question': 'What comes next?'},
                correct_answer='10',
            )
            question = QuestionRepository.create(db, question)

            request = AnswerRequest(
                session_id=session.session_id,
                question_id=question.question_id,
                response='10',
                reaction_time_ms=9000,
                hint_used=False,
            )

            result = AnswerService.submit_answer(db, request)
            updated_session = SessionRepository.get_by_session_id(db, session.session_id)

            self.assertTrue(result['correct'])
            self.assertEqual(result['next_level'], 3)
            self.assertEqual(updated_session.current_level, 3)
        finally:
            db.close()


if __name__ == '__main__':
    unittest.main()
