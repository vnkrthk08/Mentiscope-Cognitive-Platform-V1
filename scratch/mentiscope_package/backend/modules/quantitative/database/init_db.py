"""
==========================================================
Database Initialization
==========================================================
"""

from modules.quantitative.database.base import Base
from modules.quantitative.database.database import engine

# Import ALL models so SQLAlchemy registers them
from modules.quantitative.models.session import AssessmentSession
from modules.quantitative.models.question_template import QuestionTemplate
from modules.quantitative.models.question_instance import QuestionInstance
from modules.quantitative.models.student_response import StudentResponse
from modules.quantitative.models.event_log import EventLog
from modules.quantitative.models.analytics import Analytics
from modules.quantitative.models.result import AssessmentResult


def create_database():
    """
    Create all database tables.
    """

    Base.metadata.create_all(bind=engine)

    print("✅ Database tables created successfully.")


if __name__ == "__main__":
    create_database()