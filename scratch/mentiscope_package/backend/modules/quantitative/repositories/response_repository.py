from sqlalchemy.orm import Session

from modules.quantitative.models.student_response import StudentResponse


class ResponseRepository:

    @staticmethod
    def create(
        db: Session,
        response: StudentResponse,
    ):

        db.add(response)
        db.commit()
        db.refresh(response)

        return response

    @staticmethod
    def get_all_for_session(
        db: Session,
        session_id: str,
    ):

        return (
            db.query(StudentResponse)
            .filter(
                StudentResponse.session_id == session_id
            )
            .all()
        )