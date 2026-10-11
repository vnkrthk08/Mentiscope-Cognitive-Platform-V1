import time
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

try:
    from ....database import get_db
    from ....core_models import SavedAssessmentSession
    from ....admin_csv_service import record_student_score
except (ImportError, ValueError):
    from database import get_db
    from core_models import SavedAssessmentSession
    from admin_csv_service import record_student_score

router = APIRouter()

GSM_QUESTIONS = [
    {
        "id": "gsm-1",
        "text": "Repeat the sequence in the correct order.",
        "story": "Working Memory (Digit Span Forward): Listen or watch carefully. Remember this sequence of digits.",
        "sequence": [4, 8, 2, 9, 1],
        "type": "memory-span",
        "correct_answer": "48291",
        "hint": "Type the numbers exactly as they appeared: Four, Eight, Two, Nine, One."
    },
    {
        "id": "gsm-2",
        "text": "Repeat the sequence in REVERSE order.",
        "story": "Working Memory (Digit Span Backward): Reverse processing forces active storage manipulation.",
        "sequence": [3, 7, 5, 1, 8],
        "type": "memory-span",
        "correct_answer": "81573",
        "hint": "Take the sequence 3, 7, 5, 1, 8 and type it backwards."
    },
    {
        "id": "gsm-3",
        "text": "Remember and repeat this mixed alpha-numeric span in ascending order.",
        "story": "Alpha-Numeric Span Sort: Sort numbers first, then letters in alphabetical order.",
        "sequence": ["B", 5, "A", 2, "C", 8],
        "type": "memory-span",
        "correct_answer": "258ABC",
        "hint": "Order numbers first (2, 5, 8) then letters (A, B, C)."
    },
    {
        "id": "gsm-4",
        "text": "Look at the pattern grid. Which coordinates contained the highlighted cells?",
        "story": "Visual-Spatial Working Memory: Remember active cells on a 4x4 matrix.",
        "gridSize": 4,
        "activeGridCells": [2, 7, 13],
        "type": "grid-pattern",
        "correct_answer": "2,7,13",
        "hint": "Remember the row/column indices (zero-indexed: top-left is 0, bottom-right is 15)."
    },
    {
        "id": "gsm-5",
        "text": "Enter the sum of the first digit and the last digit from this sequence: 7, 2, 9, 4, 3",
        "story": "Active Arithmetic Memory: Hold the sequence while performing an arithmetic operation.",
        "sequence": [7, 2, 9, 4, 3],
        "options": ["9", "10", "11", "12"],
        "type": "choice",
        "correct_answer": "10",
        "hint": "Add the first digit (7) and the last digit (3)."
    }
]

class GsmStartRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    studentId: Optional[str] = None
    student_id: Optional[str] = None

class GsmAnswerRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    questionId: Optional[str] = None
    question_id: Optional[str] = None
    answer: str
    durationMs: Optional[int] = 0
    duration_ms: Optional[int] = 0

class GsmFinishRequest(BaseModel):
    sessionId: Optional[str] = None
    session_id: Optional[str] = None
    studentId: Optional[str] = None
    student_id: Optional[str] = None
    answers: Optional[List[Dict[str, Any]]] = None

_gsm_cache: Dict[str, Dict[str, Any]] = {}

@router.post("/start")
def start_gsm(payload: GsmStartRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id or f"sess_gsm_{int(time.time()*1000)}"
    _gsm_cache[sess_id] = {}
    
    clean_questions = []
    for q in GSM_QUESTIONS:
        item = dict(q)
        item.pop("correct_answer", None)
        clean_questions.append(item)

    return {
        "status": "success",
        "sessionId": sess_id,
        "moduleId": "gsm",
        "moduleName": "Working Memory (Gsm)",
        "construct": "Executive Working Memory & Span Retention",
        "totalQuestions": len(clean_questions),
        "questions": clean_questions
    }

@router.post("/answer")
def answer_gsm(payload: GsmAnswerRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id
    if not sess_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    qid = payload.questionId or payload.question_id or ""
    q_data = next((q for q in GSM_QUESTIONS if q["id"] == qid), None)

    is_correct = False
    ans_clean = str(payload.answer).replace(" ", "").replace("-", "").strip().upper()
    
    if q_data:
        target_clean = str(q_data["correct_answer"]).replace(" ", "").replace("-", "").strip().upper()
        is_correct = ans_clean == target_clean

    feedback = "Correct! Target memory chunk recalled accurately." if is_correct else "Response recorded."

    if sess_id not in _gsm_cache:
        _gsm_cache[sess_id] = {}

    _gsm_cache[sess_id][qid] = {
        "answer": payload.answer,
        "isCorrect": is_correct,
        "durationMs": payload.durationMs or payload.duration_ms or 0
    }

    return {
        "status": "success",
        "isCorrect": is_correct,
        "feedback": feedback
    }

@router.post("/finish")
def finish_gsm(payload: GsmFinishRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id
    stu_id = payload.studentId or payload.student_id or "stud_candidate"
    if not sess_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    recorded = _gsm_cache.get(sess_id, {})

    if payload.answers:
        for a in payload.answers:
            qid = str(a.get("questionId") or a.get("question_id") or "")
            ans = str(a.get("answer") or "")
            q_data = next((q for q in GSM_QUESTIONS if q["id"] == qid), None)
            is_corr = a.get("isCorrect")
            if is_corr is None and q_data:
                c1 = ans.replace(" ", "").replace("-", "").strip().upper()
                c2 = str(q_data["correct_answer"]).replace(" ", "").replace("-", "").strip().upper()
                is_corr = c1 == c2
            recorded[qid] = {
                "answer": ans,
                "isCorrect": bool(is_corr),
                "durationMs": a.get("durationMs") or a.get("duration_ms") or 0
            }

    total_q = len(GSM_QUESTIONS)
    correct_count = sum(1 for item in recorded.values() if item.get("isCorrect"))
    accuracy = round((correct_count / total_q) * 100.0, 1) if total_q > 0 else 0.0

    span_capacity = "High Span (7-9 Items)" if accuracy >= 80 else ("Moderate Span (5-6 Items)" if accuracy >= 60 else "Developing Span (3-4 Items)")

    metrics = {
        "raw_score": correct_count,
        "total_questions": total_q,
        "accuracy": accuracy,
        "span_capacity": span_capacity,
        "forward_span": recorded.get("gsm-1", {}).get("isCorrect", False),
        "backward_span": recorded.get("gsm-2", {}).get("isCorrect", False),
        "alphanumeric_sort": recorded.get("gsm-3", {}).get("isCorrect", False),
        "spatial_grid_recall": recorded.get("gsm-4", {}).get("isCorrect", False),
        "dual_task_arithmetic": recorded.get("gsm-5", {}).get("isCorrect", False),
        "status": "Completed"
    }

    # Sync to SavedAssessmentSession
    existing_sess = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.session_id == sess_id).first()
    if existing_sess and existing_sess.payload:
        data = dict(existing_sess.payload)
        mod_scores = dict(data.get("moduleScores", {}))
        mod_scores["gsm"] = accuracy
        data["moduleScores"] = mod_scores
        mod_metrics = dict(data.get("moduleMetrics", {}))
        mod_metrics["gsm"] = metrics
        data["moduleMetrics"] = mod_metrics
        if len(mod_scores) > 0:
            data["overallScore"] = round(sum(mod_scores.values()) / len(mod_scores))
        existing_sess.payload = data
        db.commit()
    elif existing_sess:
        existing_sess.payload = {
            "sessionId": sess_id,
            "studentId": stu_id,
            "moduleScores": {"gsm": accuracy},
            "moduleMetrics": {"gsm": metrics},
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
                "moduleScores": {"gsm": accuracy},
                "moduleMetrics": {"gsm": metrics},
                "overallScore": round(accuracy),
                "status": "completed"
            }
        )
        db.add(new_sess)
        db.commit()

    # Record to CSV
    try:
        record_student_score(
            db=db,
            session_id=sess_id,
            student_id=stu_id,
            module_id="gsm",
            score=accuracy,
            metrics=metrics
        )
    except Exception as e:
        print("[GSM record_student_score warning]", e)

    return {
        "status": "completed",
        "sessionId": sess_id,
        "scorePercentage": accuracy,
        "metrics": metrics
    }

@router.get("/result/{session_id}")
def get_gsm_result(session_id: str, db: Session = Depends(get_db)):
    sess = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.session_id == session_id).first()
    if not sess or not sess.payload:
        raise HTTPException(status_code=404, detail="Session not found")
    
    score = sess.payload.get("moduleScores", {}).get("gsm", 0)
    metrics = sess.payload.get("moduleMetrics", {}).get("gsm", {})
    return {
        "moduleId": "gsm",
        "score": score,
        "metrics": metrics
    }
