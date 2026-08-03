"""
==========================================================
Database Initialization
==========================================================
"""

from app.database.base import Base
from app.database.database import engine

# Import ALL models so SQLAlchemy registers them
from app.models.session import AssessmentSession
from app.models.question_template import QuestionTemplate
from app.models.question_instance import QuestionInstance
from app.models.student_response import StudentResponse
from app.models.event_log import EventLog
from app.models.analytics import Analytics
from app.models.result import AssessmentResult


def create_database():
    """
    Create all database tables.
    """

    Base.metadata.create_all(bind=engine)

    print("✅ Database tables created successfully.")


if __name__ == "__main__":
    create_database()