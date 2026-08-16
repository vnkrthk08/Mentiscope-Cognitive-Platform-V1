from datetime import datetime

from modules.quantitative.repositories.session_repository import SessionRepository


class FinishService:

    @staticmethod
    def finish(db, request):

        session = SessionRepository.get_by_session_id(
            db,
            request.session_id,
        )

        session.status = "COMPLETED"

        session.ended_at = datetime.utcnow()

        db.commit()

        return {

            "status": "Completed",

            "assessment_id": session.id,

            "student_id": session.student_id,

            "completed_at": session.ended_at,
        }