import time
from sqlalchemy import Column, String, Integer, Float, Text, JSON
try:
    from database import Base
except ImportError:
    from ...database import Base

class AttentionSession(Base):
    __tablename__ = "attention_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    student_id = Column(String, index=True, nullable=False)
    status = Column(String, default="in_progress")
    current_module = Column(String, default="sustained")
    start_time = Column(Float, default=time.time)
    end_time = Column(Float, nullable=True)
    completion_time_sec = Column(Integer, default=0)

class AttentionEvent(Base):
    __tablename__ = "attention_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True, nullable=False)
    submodule = Column(String, nullable=False)  # sustained, selective, divided, executive
    trial_index = Column(Integer, default=0)
    stimulus = Column(Text, nullable=True)
    response = Column(String, nullable=True)
    is_correct = Column(Integer, default=0)  # 1 or 0
    reaction_time_ms = Column(Float, default=0.0)
    timestamp = Column(Float, default=time.time)

class AttentionScore(Base):
    __tablename__ = "attention_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    student_id = Column(String, index=True, nullable=False)
    overall_score = Column(Float, default=0.0)
    sustained_score = Column(Float, default=0.0)
    selective_score = Column(Float, default=0.0)
    divided_score = Column(Float, default=0.0)
    executive_score = Column(Float, default=0.0)
    percentile = Column(Float, default=0.0)
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(Float, default=time.time)
