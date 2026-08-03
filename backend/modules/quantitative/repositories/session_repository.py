"""
Session Repository
"""

from sqlalchemy.orm import Session

from modules.quantitative.models.session import AssessmentSession


class SessionRepository:

    @staticmethod
    def create(
        db: Session,
        session: AssessmentSession,
    ):
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_by_session_id(
        db: Session,
        session_id: str,
    ):
        return (
            db.query(AssessmentSession)
            .filter(
                AssessmentSession.session_id == session_id
            )
            .first()
        )
    @staticmethod
    def get_by_id(
        db: Session,
        assessment_id: str,
    ):
        session = (
            db.query(AssessmentSession)
            .filter(
                AssessmentSession.id == assessment_id
            )
            .first()
        )

        if session is None:
            session = (
                db.query(AssessmentSession)
                .filter(
                    AssessmentSession.session_id == assessment_id
                )
                .first()
            )

        return session