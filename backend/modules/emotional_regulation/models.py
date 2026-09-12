import time
from sqlalchemy import Column, String, Integer, Float, Text, JSON
try:
    from database import Base
except ImportError:
    from ...database import Base

class CrisisSession(Base):
    __tablename__ = "crisis_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    student_id = Column(String, index=True, nullable=False)
    status = Column(String, default="in_progress")
    start_time = Column(Float, default=time.time)
    end_time = Column(Float, nullable=True)
    completion_time_sec = Column(Integer, default=0)

class CrisisEvent(Base):
    __tablename__ = "crisis_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True, nullable=False)
    module = Column(Integer, default=1)
    scenario_id = Column(String, nullable=True)
    event_type = Column(String, nullable=False)  # CORRECT_DECISION, WRONG_DECISION, PANIC_CLICK, TIMEOUT, etc.
    decision_time_ms = Column(Float, default=0.0)
    panic_clicks = Column(Integer, default=0)
    recovery_latency_ms = Column(Float, default=0.0)
    retry_count = Column(Integer, default=0)
    lives_at_risk = Column(Integer, default=0)
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(Float, default=time.time)

class CrisisScore(Base):
    __tablename__ = "crisis_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    student_id = Column(String, index=True, nullable=False)
    overall_score = Column(Float, default=0.0)
    recovery_resilience = Column(Float, default=0.0)
    stress_tolerance = Column(Float, default=0.0)
    adaptation_persistence = Column(Float, default=0.0)
    decision_stability = Column(Float, default=0.0)
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(Float, default=time.time)
