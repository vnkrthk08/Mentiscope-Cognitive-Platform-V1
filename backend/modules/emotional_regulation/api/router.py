import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

try:
    from database import get_db
    from core_models import SavedAssessmentSession
except ImportError:
    from ....database import get_db
    from ....core_models import SavedAssessmentSession

from ..models import CrisisSession, CrisisEvent, CrisisScore
from ..scenarios import ALL_SCENARIOS
from ..scorer import calculate_crisis_score

router = APIRouter()

class CrisisStartRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    studentId: Optional[str] = None
    student_id: Optional[str] = None

class CrisisEventRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    module: int
    scenarioId: Optional[str] = None
    eventType: str  # CORRECT_DECISION, WRONG_DECISION, PANIC_CLICK, TIMEOUT
    decisionTimeMs: Optional[float] = 0.0
    panicClicks: Optional[int] = 0
    recoveryLatencyMs: Optional[float] = 0.0
    retryCount: Optional[int] = 0
    livesAtRisk: Optional[int] = 0
    metadata: Optional[Dict[str, Any]] = None

class CrisisFinishRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    studentId: Optional[str] = None
    student_id: Optional[str] = None
    scorePercentage: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None

@router.post("/start")
def start_crisis_dispatcher(payload: CrisisStartRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id or f"sess_crisis_{int(time.time()*1000)}"
    stu_id = payload.studentId or payload.student_id or "stud_candidate"

    existing = db.query(CrisisSession).filter(CrisisSession.session_id == sess_id).first()
    if not existing:
        sess = CrisisSession(
            session_id=sess_id,
            student_id=stu_id,
            status="in_progress",
            start_time=time.time()
        )
        db.add(sess)
        db.commit()

    return {
        "status": "success",
        "sessionId": sess_id,
        "moduleId": "emotional_regulation",
        "moduleName": "Crisis Dispatcher Simulation",
        "scenarios": ALL_SCENARIOS,
        "totalScenarios": len(ALL_SCENARIOS)
    }

@router.post("/answer")
@router.post("/event")
def log_crisis_event(payload: CrisisEventRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id
    if not sess_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    event = CrisisEvent(
        session_id=sess_id,
        module=payload.module,
        scenario_id=payload.scenarioId,
        event_type=payload.eventType,
        decision_time_ms=payload.decisionTimeMs or 0.0,
        panic_clicks=payload.panicClicks or 0,
        recovery_latency_ms=payload.recoveryLatencyMs or 0.0,
        retry_count=payload.retryCount or 0,
        lives_at_risk=payload.livesAtRisk or 0,
        metadata_json=payload.metadata,
        timestamp=time.time()
    )
    db.add(event)
    db.commit()

    return {"status": "success", "recorded": True}

@router.post("/finish")
def finish_crisis_dispatcher(payload: CrisisFinishRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id
    stu_id = payload.studentId or payload.student_id or "stud_candidate"
    if not sess_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    sess = db.query(CrisisSession).filter(CrisisSession.session_id == sess_id).first()
    if sess:
        sess.status = "completed"
        sess.end_time = time.time()
        sess.completion_time_sec = int(sess.end_time - sess.start_time)
        db.commit()

    # Query all events for this session
    db_events = db.query(CrisisEvent).filter(CrisisEvent.session_id == sess_id).all()
    event_dicts = [
        {
            "module": e.module,
            "scenario_id": e.scenario_id,
            "event_type": e.event_type,
            "decision_time_ms": e.decision_time_ms,
            "panic_clicks": e.panic_clicks,
            "recovery_latency_ms": e.recovery_latency_ms,
            "retry_count": e.retry_count,
            "lives_at_risk": e.lives_at_risk,
            "metadata": e.metadata_json or {},
        }
        for e in db_events
    ]

    computed = calculate_crisis_score(event_dicts)
    final_score = payload.scorePercentage if payload.scorePercentage is not None else computed["overallScore"]
    metrics_data = payload.metrics or computed

    # Save to crisis_scores
    existing_score = db.query(CrisisScore).filter(CrisisScore.session_id == sess_id).first()
    if existing_score:
        existing_score.overall_score = final_score
        existing_score.recovery_resilience = computed["recoveryResilience"]
        existing_score.stress_tolerance = computed["stressTolerance"]
        existing_score.adaptation_persistence = computed["adaptationPersistence"]
        existing_score.decision_stability = computed["decisionStability"]
        existing_score.metrics_json = metrics_data
    else:
        new_score = CrisisScore(
            session_id=sess_id,
            student_id=stu_id,
            overall_score=final_score,
            recovery_resilience=computed["recoveryResilience"],
            stress_tolerance=computed["stressTolerance"],
            adaptation_persistence=computed["adaptationPersistence"],
            decision_stability=computed["decisionStability"],
            metrics_json=metrics_data
        )
        db.add(new_score)

    # CRITICAL: Sync directly to SavedAssessmentSession in mentiscope.db for instant live report update!
    existing_sess = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.session_id == sess_id).first()
    if existing_sess and existing_sess.payload:
        data = dict(existing_sess.payload)
        mod_scores = dict(data.get("moduleScores", {}))
        mod_scores["emotional_regulation"] = final_score
        data["moduleScores"] = mod_scores
        mod_metrics = dict(data.get("moduleMetrics", {}))
        mod_metrics["emotional_regulation"] = metrics_data
        data["moduleMetrics"] = mod_metrics
        if len(mod_scores) > 0:
            data["overallScore"] = round(sum(mod_scores.values()) / len(mod_scores))
        existing_sess.payload = data
    elif existing_sess:
        existing_sess.payload = {
            "sessionId": sess_id,
            "studentId": stu_id,
            "moduleScores": {"emotional_regulation": final_score},
            "moduleMetrics": {"emotional_regulation": metrics_data},
            "overallScore": round(final_score),
            "status": "completed"
        }
    else:
        new_sess = SavedAssessmentSession(
            session_id=sess_id,
            student_id=stu_id,
            payload={
                "sessionId": sess_id,
                "studentId": stu_id,
                "moduleScores": {"emotional_regulation": final_score},
                "moduleMetrics": {"emotional_regulation": metrics_data},
                "overallScore": round(final_score),
                "status": "completed"
            }
        )
        db.add(new_sess)

    db.commit()

    return {
        "status": "success",
        "sessionId": sess_id,
        "scorePercentage": final_score,
        "metrics": metrics_data
    }

@router.get("/result/{session_id}")
def get_crisis_result(session_id: str, db: Session = Depends(get_db)):
    score = db.query(CrisisScore).filter(CrisisScore.session_id == session_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found for session")
    return {
        "status": "success",
        "sessionId": score.session_id,
        "studentId": score.student_id,
        "overallScore": score.overall_score,
        "dimensions": {
            "recoveryResilience": score.recovery_resilience,
            "stressTolerance": score.stress_tolerance,
            "adaptationPersistence": score.adaptation_persistence,
            "decisionStability": score.decision_stability,
        },
        "metrics": score.metrics_json
    }
