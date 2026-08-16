"""
ASAT – SQLAlchemy ORM Table Models

Translated from: backend/db.js CREATE TABLE statements.
Every table, column, type, constraint, and foreign key is preserved exactly.

PostgreSQL differences from original MySQL:
  - AUTO_INCREMENT → identity columns (autoincrement=True)
  - JSON → JSONB (better indexing in PostgreSQL)
  - BOOLEAN is native (no TINYINT workaround)
  - TIMESTAMP DEFAULT CURRENT_TIMESTAMP → server_default=func.now()

NOTE: Table names and column names are kept configurable-friendly.
      If the MentiScope shared schema uses different names,
      update the __tablename__ attributes here.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text,
    ForeignKey, func,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import relationship

from app.database import Base


class Faculty(Base):
    """
    Faculty authentication table.
    Translated from: db.js → CREATE TABLE IF NOT EXISTS faculty
    """
    __tablename__ = "faculty"

    faculty_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    students = relationship("Student", back_populates="faculty")


class Student(Base):
    """
    Student demographics table.
    Translated from: db.js → CREATE TABLE IF NOT EXISTS students
    """
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, autoincrement=True)
    faculty_id = Column(
        Integer,
        ForeignKey("faculty.faculty_id", ondelete="SET NULL"),
        nullable=True,
    )
    full_name = Column(String(255), nullable=False)
    student_id_number = Column(String(100), unique=True, nullable=True)
    age = Column(Integer, nullable=True)
    grade = Column(String(50), nullable=True)
    school = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    faculty = relationship("Faculty", back_populates="students")
    sessions = relationship("Session", back_populates="student", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="student", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="student", cascade="all, delete-orphan")


class Session(Base):
    """
    Assessment session table.
    Translated from: db.js → CREATE TABLE IF NOT EXISTS sessions
    """
    __tablename__ = "sessions"

    session_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(
        Integer,
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
    )
    session_uuid = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), server_default="pending")
    start_time = Column(TIMESTAMP(timezone=True), server_default=func.now())
    end_time = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="sessions")
    events = relationship("Event", back_populates="session", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="session", cascade="all, delete-orphan")


class Event(Base):
    """
    Trial-level event log table.
    Translated from: db.js → CREATE TABLE IF NOT EXISTS events

    NOTE: The original MySQL table had a 'stimulus' column added via the
    sessions.js bulk insert, but it was not in the db.js CREATE TABLE.
    We include it here for completeness as it is used in practice.
    """
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(
        Integer,
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id = Column(
        Integer,
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    construct = Column(String(100), nullable=True)
    task_id = Column(String(100), nullable=True)
    item_id = Column(Integer, nullable=True)
    stimulus = Column(String(255), nullable=True)
    event_type = Column(String(50), nullable=True)
    response = Column(String(255), nullable=True)
    correct = Column(Boolean, nullable=True)
    reaction_time_ms = Column(Integer, nullable=True)
    error_type = Column(String(100), nullable=True)
    difficulty_level = Column(Integer, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("Session", back_populates="events")


class Score(Base):
    """
    Module scores and advanced analytics table.
    Translated from: db.js → CREATE TABLE IF NOT EXISTS scores
    """
    __tablename__ = "scores"

    score_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(
        Integer,
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
    )
    session_uuid = Column(String(255), nullable=True)

    # Per-module scores
    sustained_score = Column(Float, nullable=True)
    selective_score = Column(Float, nullable=True)
    divided_score = Column(Float, nullable=True)
    executive_score = Column(Float, nullable=True)

    # SDK-compliant outputs
    raw_score = Column(Float, nullable=True)
    normalized_score = Column(Float, nullable=True)
    percentile = Column(Integer, nullable=True)
    sub_scores = Column(JSONB, nullable=True)
    confidence_score = Column(Float, nullable=True)

    # Composite
    overall_score = Column(Float, nullable=True)
    module_results = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="scores")


class Report(Base):
    """
    Behavioral metrics and recommendations report table.
    Translated from: db.js → CREATE TABLE IF NOT EXISTS reports
    """
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(
        Integer,
        ForeignKey("students.student_id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id = Column(
        Integer,
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    behavioral_metrics = Column(JSONB, nullable=True)
    recommendations = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="reports")
    session = relationship("Session", back_populates="reports")
