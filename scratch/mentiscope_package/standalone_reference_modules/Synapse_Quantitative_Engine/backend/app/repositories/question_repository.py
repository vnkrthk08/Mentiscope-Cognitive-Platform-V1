"""
==========================================================
Question Repository
==========================================================
"""

from sqlalchemy.orm import Session

from app.models.question_instance import QuestionInstance


class QuestionRepository:

    @staticmethod
    def create(
        db: Session,
        question: QuestionInstance,
    ):

        db.add(question)
        db.commit()
        db.refresh(question)

        return question

    @staticmethod
    def get_by_question_id(
        db: Session,
        question_id: str,
    ):

        return (
            db.query(QuestionInstance)
            .filter(
                QuestionInstance.question_id == question_id
            )
            .first()
        )

    @staticmethod
    def get_latest_for_session(
        db: Session,
        session_id: str,
    ):

        return (
            db.query(QuestionInstance)
            .filter(
                QuestionInstance.session_id == session_id
            )
            .order_by(
                QuestionInstance.presented_at.desc()
            )
            .first()
        )