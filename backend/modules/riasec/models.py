import time
from sqlalchemy import Column, String, Integer, Float, Text, JSON
try:
    from database import Base
except ImportError:
    from ...database import Base

class RiasecSession(Base):
    __tablename__ = "riasec_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    student_id = Column(String, index=True, nullable=False)
    construct = Column(String, default="RIASEC")
    status = Column(String, default="In_Progress")
    start_time = Column(Float, default=time.time)
    end_time = Column(Float, nullable=True)
    completion_time = Column(Integer, default=0)
    selected_items_json = Column(Text, default="[]")
    scores_json = Column(Text, default='{"R":0,"I":0,"A":0,"S":0,"E":0,"C":0}')

class RiasecEventLog(Base):
    __tablename__ = "riasec_event_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True, nullable=False)
    item_id = Column(String, nullable=False)
    selected_option = Column(String, nullable=True)
    selected_dimension = Column(String, nullable=True)
    reaction_time_ms = Column(Integer, default=0)
    timestamp = Column(Float, default=time.time)

class RiasecScore(Base):
    __tablename__ = "riasec_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    student_id = Column(String, index=True, nullable=False)
    overall_score = Column(Float, default=0.0)
    scores_json = Column(JSON, nullable=True)
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(Float, default=time.time)
