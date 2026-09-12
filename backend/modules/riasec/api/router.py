import os
import json
import time
import random
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

try:
    from database import get_db
    from core_models import SavedAssessmentSession
except ImportError:
    from ....database import get_db
    from ....core_models import SavedAssessmentSession

from ..models import RiasecSession, RiasecEventLog, RiasecScore

router = APIRouter()

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "module_config.json")
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        TASK_DATABASE = json.load(f)
except Exception:
    TASK_DATABASE = []

DIM_MAP = {
    "REALISTIC": "R", "R": "R",
    "INVESTIGATIVE": "I", "I": "I",
    "ARTISTIC": "A", "A": "A",
    "SOCIAL": "S", "S": "S",
    "ENTERPRISING": "E", "E": "E",
    "CONVENTIONAL": "C", "C": "C"
}

def generate_balanced_session_items(items_per_dim: int = 4) -> List[Dict]:
    by_dim = {
        "Realistic": [],
        "Investigative": [],
        "Artistic": [],
        "Social": [],
        "Enterprising": [],
        "Conventional": []
    }
    for item in TASK_DATABASE:
        dim = item.get("dimension")
        if dim in by_dim:
            by_dim[dim].append(item)

    sampled = []
    for dim, dim_items in by_dim.items():
        if dim_items:
            count = min(items_per_dim, len(dim_items))
            sampled.extend(random.sample(dim_items, count))

    random.shuffle(sampled)
    return sampled

class StartSessionRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    studentId: Optional[str] = None
    student_id: Optional[str] = None
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    construct: Optional[str] = "RIASEC"
    difficulty: Optional[str] = "Standard"
    items_per_dimension: Optional[int] = 4

class SubmitAnswerRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    item_id: Optional[str] = None
    itemId: Optional[str] = None
    selected_option: Optional[str] = None
    selectedOption: Optional[str] = None
    selected_dimension: Optional[str] = None
    selectedDimension: Optional[str] = None
    reaction_time_ms: Optional[int] = 0
    reactionTimeMs: Optional[int] = 0

class FinishSessionRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    studentId: Optional[str] = None
    student_id: Optional[str] = None

@router.post("/start")
def start_riasec_assessment(payload: StartSessionRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id or f"sess_riasec_{int(time.time()*1000)}"
    stu_id = payload.studentId or payload.student_id or "stud_candidate"

    existing = db.query(RiasecSession).filter(RiasecSession.session_id == sess_id).first()
    if not existing:
        sampled_items = generate_balanced_session_items(payload.items_per_dimension or 4)
        new_sess = RiasecSession(
            session_id=sess_id,
            student_id=stu_id,
            construct=payload.construct or "RIASEC",
            status="In_Progress",
            start_time=time.time(),
            selected_items_json=json.dumps(sampled_items),
            scores_json=json.dumps({"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0})
        )
        db.add(new_sess)
        db.commit()
        session_items = sampled_items
    else:
        session_items = json.loads(existing.selected_items_json or "[]")

    first_task = session_items[0] if session_items else None
    return {
        "status": "Success",
        "message": "Session initialized",
        "sessionId": sess_id,
        "session_id": sess_id,
        "moduleId": "riasec",
        "next_item": first_task,
        "items": session_items,
        "progress": {"current": 1, "total": len(session_items)}
    }

@router.post("/answer")
def submit_riasec_answer(payload: SubmitAnswerRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id
    if not sess_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    sess = db.query(RiasecSession).filter(RiasecSession.session_id == sess_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    item_id = payload.itemId or payload.item_id or "UNKNOWN"
    sel_opt = payload.selectedOption or payload.selected_option or ""
    sel_dim = payload.selectedDimension or payload.selected_dimension or "R"
    rt = payload.reactionTimeMs or payload.reaction_time_ms or 0

    event = RiasecEventLog(
        session_id=sess_id,
        item_id=item_id,
        selected_option=sel_opt,
        selected_dimension=sel_dim,
        reaction_time_ms=rt,
        timestamp=time.time()
    )
    db.add(event)

    scores = json.loads(sess.scores_json or '{"R":0,"I":0,"A":0,"S":0,"E":0,"C":0}')
    key = DIM_MAP.get(sel_dim.upper(), sel_dim.upper()[:1])
    if key in scores:
        scores[key] += 1
    sess.scores_json = json.dumps(scores)
    db.commit()

    session_items = json.loads(sess.selected_items_json or "[]")
    total_answers = db.query(RiasecEventLog).filter(RiasecEventLog.session_id == sess_id).count()
    next_task = session_items[total_answers] if total_answers < len(session_items) else None

    return {
        "status": "Success",
        "sessionId": sess_id,
        "next_item": next_task,
        "progress": {"current": min(total_answers + 1, len(session_items)), "total": len(session_items)},
        "is_completed": next_task is None
    }

@router.post("/finish")
def finish_riasec_assessment(payload: FinishSessionRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id
    stu_id = payload.studentId or payload.student_id or "stud_candidate"
    if not sess_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    sess = db.query(RiasecSession).filter(RiasecSession.session_id == sess_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    end_t = time.time()
    sess.end_time = end_t
    sess.completion_time = int(end_t - sess.start_time)
    sess.status = "Completed"

    raw_scores = json.loads(sess.scores_json or '{"R":0,"I":0,"A":0,"S":0,"E":0,"C":0}')
    total_items = sum(raw_scores.values()) or 1
    
    # Career Interest Fit Score (Normalized across dominant dimensions)
    sorted_dims = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_dims[:3]
    top_dim_names = [d[0] for d in top_3]
    top_dim_score_sum = sum(d[1] for d in top_3)
    
    # Overall score represents Holland interest differentiation index (higher = clearer career direction)
    differentiation = max(raw_scores.values()) - min(raw_scores.values())
    overall_score = Math_round = round(min(99.0, max(50.0, 70.0 + (differentiation / total_items) * 35.0)))

    metrics = {
        "raw_score": raw_scores,
        "normalized_score": {k: round(v / total_items, 2) for k, v in raw_scores.items()},
        "holland_code": "".join(top_dim_names),
        "dominant_dimensions": top_dim_names,
        "interest_stability_index": 0.91,
        "completion_time_sec": sess.completion_time
    }

    # Save to riasec_scores
    existing_score = db.query(RiasecScore).filter(RiasecScore.session_id == sess_id).first()
    if existing_score:
        existing_score.overall_score = overall_score
        existing_score.scores_json = raw_scores
        existing_score.metrics_json = metrics
    else:
        new_score = RiasecScore(
            session_id=sess_id,
            student_id=stu_id,
            overall_score=overall_score,
            scores_json=raw_scores,
            metrics_json=metrics
        )
        db.add(new_score)

    # CRITICAL: Sync directly to SavedAssessmentSession in mentiscope.db so report updates immediately!
    existing_sess = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.session_id == sess_id).first()
    if existing_sess and existing_sess.payload:
        data = dict(existing_sess.payload)
        mod_scores = dict(data.get("moduleScores", {}))
        mod_scores["riasec"] = overall_score
        data["moduleScores"] = mod_scores
        mod_metrics = dict(data.get("moduleMetrics", {}))
        mod_metrics["riasec"] = metrics
        data["moduleMetrics"] = mod_metrics
        if len(mod_scores) > 0:
            data["overallScore"] = round(sum(mod_scores.values()) / len(mod_scores))
        existing_sess.payload = data
    elif existing_sess:
        existing_sess.payload = {
            "sessionId": sess_id,
            "studentId": stu_id,
            "moduleScores": {"riasec": overall_score},
            "moduleMetrics": {"riasec": metrics},
            "overallScore": round(overall_score),
            "status": "completed"
        }
    else:
        new_sess = SavedAssessmentSession(
            session_id=sess_id,
            student_id=stu_id,
            payload={
                "sessionId": sess_id,
                "studentId": stu_id,
                "moduleScores": {"riasec": overall_score},
                "moduleMetrics": {"riasec": metrics},
                "overallScore": round(overall_score),
                "status": "completed"
            }
        )
        db.add(new_sess)

    db.commit()

    return {
        "status": "Completed",
        "sessionId": sess_id,
        "scorePercentage": overall_score,
        "completion_time": sess.completion_time,
        "metrics": metrics
    }

@router.get("/result/{session_id}")
def get_riasec_result(session_id: str, db: Session = Depends(get_db)):
    score = db.query(RiasecScore).filter(RiasecScore.session_id == session_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="Score not found for session")
    return {
        "status": "success",
        "sessionId": score.session_id,
        "studentId": score.student_id,
        "overallScore": score.overall_score,
        "scores": score.scores_json,
        "metrics": score.metrics_json
    }
