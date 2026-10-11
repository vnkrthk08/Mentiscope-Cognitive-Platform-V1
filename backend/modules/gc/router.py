import time
import json
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

try:
    from ...database import get_db
    from ...core_models import SavedAssessmentSession
    from ...admin_csv_service import record_student_score
except (ImportError, ValueError):
    from database import get_db
    from core_models import SavedAssessmentSession
    from admin_csv_service import record_student_score

from .schemas import (
    GcStartRequest,
    GcStartResponse,
    GcAnswerRequest,
    GcAnswerResponse,
    GcFinishRequest,
    GcFinishResponse
)
from .engine import GC_QUESTIONS

router = APIRouter()

# In-memory trial answers cache
_gc_answers: Dict[str, Dict[str, Any]] = {}

@router.post("/start", response_model=GcStartResponse)
def start_gc(payload: GcStartRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id or f"sess_gc_{int(time.time()*1000)}"
    _gc_answers[sess_id] = {}
    
    # Strip correct answers from response payload
    client_questions = []
    for q in GC_QUESTIONS:
        item = dict(q)
        item.pop("correct_answer", None)
        client_questions.append(item)

    return GcStartResponse(
        status="success",
        sessionId=sess_id,
        totalQuestions=len(client_questions),
        questions=client_questions
    )

@router.post("/answer", response_model=GcAnswerResponse)
def answer_gc(payload: GcAnswerRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id
    if not sess_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    qid = payload.questionId or payload.question_id or ""
    q_data = next((q for q in GC_QUESTIONS if q["id"] == qid), None)
    
    is_correct = False
    feedback = "Response recorded."
    if q_data:
        correct_str = q_data["correct_answer"].strip().lower()
        ans_str = payload.answer.strip().lower()
        is_correct = ans_str == correct_str
        feedback = "Correct! Accurate domain knowledge application." if is_correct else f"Incorrect. The target answer was {q_data['correct_answer']}."

    if sess_id not in _gc_answers:
        _gc_answers[sess_id] = {}

    _gc_answers[sess_id][qid] = {
        "answer": payload.answer,
        "isCorrect": is_correct,
        "durationMs": payload.durationMs or payload.duration_ms or 0
    }

    return GcAnswerResponse(
        status="success",
        isCorrect=is_correct,
        feedback=feedback
    )

@router.post("/finish", response_model=GcFinishResponse)
def finish_gc(payload: GcFinishRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id
    stu_id = payload.studentId or payload.student_id or "stud_candidate"
    if not sess_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    recorded = _gc_answers.get(sess_id, {})
    
    # Ingest answers from payload if provided
    if payload.answers:
        for a in payload.answers:
            qid = a.get("questionId") or a.get("question_id") or ""
            ans = a.get("answer") or ""
            dur = a.get("durationMs") or a.get("duration_ms") or 0
            q_data = next((q for q in GC_QUESTIONS if q["id"] == qid), None)
            is_corr = a.get("isCorrect")
            if is_corr is None and q_data:
                is_corr = str(ans).strip().lower() == q_data["correct_answer"].strip().lower()
            recorded[qid] = {
                "answer": ans,
                "isCorrect": bool(is_corr),
                "durationMs": dur
            }

    total_q = len(GC_QUESTIONS)
    correct_count = sum(1 for item in recorded.values() if item.get("isCorrect"))
    accuracy = round((correct_count / total_q) * 100.0, 1) if total_q > 0 else 0.0

    # Calculate domain knowledge metrics
    domains: Dict[str, Dict[str, Any]] = {}
    for q in GC_QUESTIONS:
        d = q.get("domain", "General")
        if d not in domains:
            domains[d] = {"total": 0, "correct": 0}
        domains[d]["total"] += 1
        rec = recorded.get(q["id"])
        if rec and rec.get("isCorrect"):
            domains[d]["correct"] += 1

    domain_breakdown = {
        d: round((v["correct"] / v["total"]) * 100.0)
        for d, v in domains.items()
    }

    metrics = {
        "raw_score": correct_count,
        "total_questions": total_q,
        "accuracy": accuracy,
        "domain_breakdown": domain_breakdown,
        "verbal_comprehension_index": round(accuracy * 0.95, 1),
        "completion_status": "Completed"
    }

    # CRITICAL: Sync directly to SavedAssessmentSession in mentiscope.db
    existing_sess = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.session_id == sess_id).first()
    if existing_sess and existing_sess.payload:
        data = dict(existing_sess.payload)
        mod_scores = dict(data.get("moduleScores", {}))
        mod_scores["gc"] = accuracy
        data["moduleScores"] = mod_scores
        mod_metrics = dict(data.get("moduleMetrics", {}))
        mod_metrics["gc"] = metrics
        data["moduleMetrics"] = mod_metrics
        if len(mod_scores) > 0:
            data["overallScore"] = round(sum(mod_scores.values()) / len(mod_scores))
        existing_sess.payload = data
        db.commit()
    elif existing_sess:
        existing_sess.payload = {
            "sessionId": sess_id,
            "studentId": stu_id,
            "moduleScores": {"gc": accuracy},
            "moduleMetrics": {"gc": metrics},
            "overallScore": round(accuracy),
            "status": "completed"
        }
        db.commit()
    else:
        new_sess = SavedAssessmentSession(
            session_id=sess_id,
            student_id=stu_id,
            payload={
                "sessionId": sess_id,
                "studentId": stu_id,
                "moduleScores": {"gc": accuracy},
                "moduleMetrics": {"gc": metrics},
                "overallScore": round(accuracy),
                "status": "completed"
            }
        )
        db.add(new_sess)
        db.commit()

    # Record to real-time CSV and benchmarks
    try:
        record_student_score(
            db=db,
            session_id=sess_id,
            student_id=stu_id,
            module_id="gc",
            score=accuracy,
            metrics=metrics
        )
    except Exception as e:
        print("[GC record_student_score warning]", e)

    return GcFinishResponse(
        status="completed",
        sessionId=sess_id,
        scorePercentage=accuracy,
        metrics=metrics
    )

@router.get("/result/{session_id}")
def get_gc_result(session_id: str, db: Session = Depends(get_db)):
    sess = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.session_id == session_id).first()
    if not sess or not sess.payload:
        raise HTTPException(status_code=404, detail="Session not found")
    
    score = sess.payload.get("moduleScores", {}).get("gc", 0)
    metrics = sess.payload.get("moduleMetrics", {}).get("gc", {})
    return {
        "moduleId": "gc",
        "score": score,
        "metrics": metrics
    }
