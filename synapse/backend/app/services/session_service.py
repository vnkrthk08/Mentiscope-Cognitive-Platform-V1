"""
Session Service
"""

from app.engine.assessment_engine import AssessmentEngine
from app.models.session import AssessmentSession
from app.repositories.session_repository import SessionRepository
from app.models.question_instance import QuestionInstance
from app.repositories.question_repository import QuestionRepository

class SessionService:

    @staticmethod
    def create_session(db, request):

        session = AssessmentSession(
            student_id=request.student_id,
            session_id=request.session_id,
            module_id=request.module_id,
            construct=request.construct,
            current_level=request.difficulty,
        )

        session = SessionRepository.create(
            db,
            session,
        )

        question = AssessmentEngine.start(
            level=request.difficulty,
            db=db,
            session_id=session.session_id
        )

        QuestionRepository.create(
            db,
            QuestionInstance(
                session_id=session.id,

                question_id=question["question_id"],

                template_id=question["template_id"],

                module=question["module"],

                difficulty=question["difficulty"],

                question_json=question,

                correct_answer=str(question["correct_answer"]),
                )
            )

        return session, question