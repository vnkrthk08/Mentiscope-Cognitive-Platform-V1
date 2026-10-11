import os
import sys
from pathlib import Path
from typing import Any

# Ensure both backend root and parent root are in sys.path for seamless imports
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
PARENT_DIR = BASE_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

try:
    from .core_models import Base, SavedAssessmentSession, StudentExamScoreRecord
    from .database import engine, get_db
    from .auth_router import router as auth_router
    from .modules.processing_speed.api.router import router as processing_speed_router
    from .admin_csv_service import (
        record_student_score,
        get_dashboard_summary_data,
        create_all_datasets_zip,
        STUDENT_SCORES_CSV_PATH,
        QUESTIONS_BANK_CSV_PATH,
        MODULE_BENCHMARKS_CSV_PATH
    )
except (ImportError, ValueError):
    from core_models import Base, SavedAssessmentSession, StudentExamScoreRecord
    from database import engine, get_db
    from auth_router import router as auth_router
    from modules.processing_speed.api.router import router as processing_speed_router
    from admin_csv_service import (
        record_student_score,
        get_dashboard_summary_data,
        create_all_datasets_zip,
        STUDENT_SCORES_CSV_PATH,
        QUESTIONS_BANK_CSV_PATH,
        MODULE_BENCHMARKS_CSV_PATH
    )

try:
    from .modules.fluid_intelligence.api.router import router as fluid_intelligence_router
except Exception:
    try:
        from modules.fluid_intelligence.api.router import router as fluid_intelligence_router
    except Exception:
        fluid_intelligence_router = None

try:
    from .modules.gsm.routers.assessment import router as gsm_router
except Exception:
    try:
        from modules.gsm.routers.assessment import router as gsm_router
    except Exception:
        gsm_router = None

try:
    from .modules.csr.api.router import router as csr_router
except Exception:
    try:
        from modules.csr.api.router import router as csr_router
    except Exception:
        csr_router = None

try:
    from .modules.attention.api.router import router as attention_router
except Exception:
    try:
        from modules.attention.api.router import router as attention_router
    except Exception:
        attention_router = None

try:
    from .modules.emotional_regulation.api.router import router as emotional_regulation_router
except Exception:
    try:
        from modules.emotional_regulation.api.router import router as emotional_regulation_router
    except Exception:
        emotional_regulation_router = None

try:
    from .modules.riasec.api.router import router as riasec_router
except Exception:
    try:
        from modules.riasec.api.router import router as riasec_router
    except Exception:
        riasec_router = None

try:
    from .modules.gv.api.router import router as gv_router
except Exception:
    try:
        from modules.gv.api.router import router as gv_router
    except Exception:
        gv_router = None

try:
    from .modules.quantitative.api.answer import router as quantitative_answer_router
    from .modules.quantitative.api.start import router as quantitative_start_router
    from .modules.quantitative.api.finish import router as quantitative_finish_router
    from .modules.quantitative.api.result import router as quantitative_result_router
except Exception:
    try:
        from modules.quantitative.api.answer import router as quantitative_answer_router
        from modules.quantitative.api.start import router as quantitative_start_router
        from modules.quantitative.api.finish import router as quantitative_finish_router
        from modules.quantitative.api.result import router as quantitative_result_router
    except Exception:
        quantitative_answer_router = None

try:
    from .modules.gc.router import router as gc_router
except Exception:
    try:
        from modules.gc.router import router as gc_router
    except Exception:
        gc_router = None

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mentiscope API - Multi-Module Cognitive Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 0. User Authentication & Profile Management
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

# 1. Processing Speed (Gs)
app.include_router(processing_speed_router, prefix="/api/modules/processing-speed", tags=["processing-speed"])
app.include_router(processing_speed_router, prefix="/api/modules/gs", tags=["gs-alias"])

# 2. Fluid Intelligence (Gf)
if fluid_intelligence_router:
    app.include_router(fluid_intelligence_router, prefix="/api/modules/gf", tags=["gf"])

# 3. Working Memory Span (Gsm)
if gsm_router:
    app.include_router(gsm_router, prefix="/api/modules/gsm", tags=["gsm"])

# 4. Attention & Executive Control (ASAT)
if attention_router:
    app.include_router(attention_router, prefix="/api/modules/attention", tags=["attention"])
    app.include_router(attention_router, prefix="/api/modules/csr", tags=["attention-legacy"])
elif csr_router:
    app.include_router(csr_router, prefix="/api/modules/csr", tags=["csr"])

# 5. Emotional Regulation Assessment (Crisis Dispatcher)
if emotional_regulation_router:
    app.include_router(emotional_regulation_router, prefix="/api/modules/emotional-regulation", tags=["emotional-regulation"])
    app.include_router(emotional_regulation_router, prefix="/api/modules/emotional_regulation", tags=["emotional-regulation-alt"])

# 6. Career Interest Assessment (RIASEC)
if riasec_router:
    app.include_router(riasec_router, prefix="/api/modules/riasec", tags=["riasec"])

# 7. Visual Processing (Gv)
if gv_router:
    app.include_router(gv_router, prefix="/api/modules/gv", tags=["gv"])

# 8. Quantitative Reasoning (Gq)
if quantitative_answer_router:
    app.include_router(quantitative_answer_router, prefix="/api/quantitative", tags=["quantitative"])
    app.include_router(quantitative_start_router, prefix="/api/quantitative", tags=["quantitative"])
    app.include_router(quantitative_finish_router, prefix="/api/quantitative", tags=["quantitative"])
    app.include_router(quantitative_result_router, prefix="/api/quantitative", tags=["quantitative"])
    # Also mount at /api/modules/gq so standard AssessmentRunner works directly
    app.include_router(quantitative_answer_router, prefix="/api/modules/gq", tags=["gq-module"])
    app.include_router(quantitative_start_router, prefix="/api/modules/gq", tags=["gq-module"])
    app.include_router(quantitative_finish_router, prefix="/api/modules/gq", tags=["gq-module"])
    app.include_router(quantitative_result_router, prefix="/api/modules/gq", tags=["gq-module"])

# 9. Crystallized Intelligence (Gc)
if gc_router:
    app.include_router(gc_router, prefix="/api/modules/gc", tags=["gc"])


@app.on_event("startup")
async def startup_event():
    try:
        from modules.gsm.database import init_db as init_gsm_db
        await init_gsm_db()
    except Exception as e:
        print("[Startup Warning] GSM DB Init:", e)

    try:
        from modules.quantitative.models.session import AssessmentSession
        from modules.quantitative.models.question_instance import QuestionInstance
        from modules.quantitative.models.student_response import StudentResponse
        from modules.quantitative.database.base import Base as QuantBase
        from modules.quantitative.database.database import engine as quant_engine
        QuantBase.metadata.create_all(bind=quant_engine)
    except Exception as e:
        print("[Startup Warning] Quantitative DB Init:", e)





@app.post("/api/sessions/save")
def save_session(payload: dict[str, Any], db: Session = Depends(get_db)):
    session_id = payload.get("sessionId")
    student_id = payload.get("studentId", "guest")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing sessionId in session payload")
    
    existing = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.session_id == session_id).first()
    if existing:
        existing.student_id = student_id
        existing.payload = payload
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(existing, "payload")
    else:
        record = SavedAssessmentSession(
            session_id=session_id,
            student_id=student_id,
            payload=payload
        )
        db.add(record)
    
    db.commit()

    # Real-time CSV sync for any completed module scores in the saved payload
    try:
        mod_scores = payload.get("moduleScores", {})
        mod_metrics = payload.get("moduleMetrics", {})
        for mid, sc in mod_scores.items():
            if sc is not None:
                record_student_score(
                    db=db,
                    session_id=session_id,
                    student_id=student_id,
                    module_id=mid,
                    score=float(sc),
                    metrics=mod_metrics.get(mid) if isinstance(mod_metrics, dict) else None
                )
    except Exception as e:
        print("[Real-time CSV session save sync warning]", e)

    return {"status": "success", "sessionId": session_id}

@app.post("/api/sessions/score")
def update_session_score(payload: dict[str, Any], db: Session = Depends(get_db)):
    session_id = payload.get("sessionId") or payload.get("session_id")
    student_id = payload.get("studentId") or payload.get("student_id") or "stud_alex_mercer"
    module_id = payload.get("moduleId") or payload.get("module_id")
    raw_score = payload.get("score")
    metrics = payload.get("metrics")

    if not session_id:
        latest = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.student_id == student_id).order_by(SavedAssessmentSession.updated_at.desc()).first()
        if not latest:
            latest = db.query(SavedAssessmentSession).order_by(SavedAssessmentSession.updated_at.desc()).first()
        if latest:
            session_id = latest.session_id
        else:
            session_id = "sess_current"

    if not module_id or raw_score is None:
        raise HTTPException(status_code=400, detail="Missing moduleId or score")

    score = float(raw_score)
    existing = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.session_id == session_id).first()

    # Real-time CSV sync and database scoring
    try:
        record_student_score(
            db=db,
            session_id=session_id,
            student_id=student_id,
            module_id=module_id,
            score=score,
            metrics=metrics
        )
    except Exception as e:
        print("[Real-time CSV score sync warning]", e)

    if existing and existing.payload:
        data = dict(existing.payload)
        mod_scores = dict(data.get("moduleScores", {}))
        mod_scores[module_id] = score
        data["moduleScores"] = mod_scores
        if metrics:
            mod_metrics = dict(data.get("moduleMetrics", {}))
            mod_metrics[module_id] = metrics
            data["moduleMetrics"] = mod_metrics
        if len(mod_scores) > 0:
            data["overallScore"] = round(sum(mod_scores.values()) / len(mod_scores))
        existing.payload = data
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(existing, "payload")
        db.commit()
        return {"status": "success", "sessionId": session_id, "moduleScores": mod_scores, "session": data}
    else:
        new_payload = {
            "sessionId": session_id,
            "studentId": student_id,
            "moduleScores": {module_id: score},
            "overallScore": round(score),
            "status": "completed",
            "startTime": payload.get("startTime") or "2026-09-04T00:00:00.000Z"
        }
        rec = SavedAssessmentSession(session_id=session_id, student_id=student_id, payload=new_payload)
        db.add(rec)
        db.commit()
        return {"status": "success", "sessionId": session_id, "moduleScores": new_payload["moduleScores"], "session": new_payload}


# -------------------------------------------------------------
# Admin Real-time CSV Dashboard & Export Endpoints
# -------------------------------------------------------------

@app.get("/api/admin/csv/dashboard-data")
def get_admin_csv_dashboard_data(db: Session = Depends(get_db)):
    """
    Returns live synchronized datasets for all 3 CSVs (Student Scores,
    Question Bank, Module Benchmarks) and real summary KPIs.
    Strictly populated with genuine student attempts — zero dummy data.
    """
    return get_dashboard_summary_data(db)


@app.get("/api/admin/csv/download/{dataset_type}")
def download_admin_csv(dataset_type: str):
    """
    Directly streams genuine CSV datasets as downloadable files.
    Options: 'student-scores', 'questions-bank', 'module-benchmarks', 'all-datasets'.
    """
    if dataset_type == "student-scores":
        if not STUDENT_SCORES_CSV_PATH.exists():
            raise HTTPException(status_code=404, detail="Student scores CSV not generated yet.")
        return FileResponse(
            path=str(STUDENT_SCORES_CSV_PATH),
            media_type="text/csv",
            filename="student_performance_records.csv",
            headers={"Content-Disposition": "attachment; filename=student_performance_records.csv"}
        )
    elif dataset_type == "questions-bank":
        if not QUESTIONS_BANK_CSV_PATH.exists():
            raise HTTPException(status_code=404, detail="Questions bank CSV not generated yet.")
        return FileResponse(
            path=str(QUESTIONS_BANK_CSV_PATH),
            media_type="text/csv",
            filename="cognitive_questions_bank.csv",
            headers={"Content-Disposition": "attachment; filename=cognitive_questions_bank.csv"}
        )
    elif dataset_type == "module-benchmarks":
        if not MODULE_BENCHMARKS_CSV_PATH.exists():
            raise HTTPException(status_code=404, detail="Module benchmarks CSV not generated yet.")
        return FileResponse(
            path=str(MODULE_BENCHMARKS_CSV_PATH),
            media_type="text/csv",
            filename="module_benchmarks_analytics.csv",
            headers={"Content-Disposition": "attachment; filename=module_benchmarks_analytics.csv"}
        )
    elif dataset_type in ("all-datasets", "all", "zip"):
        zip_buffer = create_all_datasets_zip()
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=mentiscope_all_cognitive_datasets.zip"}
        )
    else:
        raise HTTPException(status_code=400, detail=f"Invalid dataset_type '{dataset_type}'. Choose 'student-scores', 'questions-bank', 'module-benchmarks', or 'all-datasets'.")


@app.post("/api/admin/csv/record-attempt")
def admin_record_attempt(payload: dict[str, Any], db: Session = Depends(get_db)):
    """
    Explicit endpoint for frontend or external modules to append a real test attempt in real-time.
    """
    import os
    session_id = payload.get("sessionId") or payload.get("session_id") or f"sess_{os.urandom(4).hex()}"
    student_id = payload.get("studentId") or payload.get("student_id") or "candidate_guest"
    module_id = payload.get("moduleId") or payload.get("module_id")
    raw_score = payload.get("score") if payload.get("score") is not None else payload.get("scorePercentage", 0.0)
    metrics = payload.get("metrics")

    if not module_id:
        raise HTTPException(status_code=400, detail="Missing moduleId")

    record = record_student_score(
        db=db,
        session_id=session_id,
        student_id=student_id,
        module_id=module_id,
        score=float(raw_score),
        metrics=metrics,
        questions_attempted=payload.get("questionsAttempted"),
        time_spent_seconds=payload.get("timeSpentSec")
    )
    return {
        "status": "success",
        "attemptId": record.attempt_id,
        "sessionId": record.session_id,
        "score": record.score_percentage,
        "moduleName": record.module_name
    }


@app.post("/api/admin/csv/clear-records")
def clear_admin_records(db: Session = Depends(get_db)):
    """
    Clears all score attempts for clean test runs.
    """
    import csv
    from admin_csv_service import recompute_benchmarks_csv, STUDENT_SCORES_CSV_PATH, STUDENT_SCORES_HEADERS
    db.query(StudentExamScoreRecord).delete()
    db.commit()
    with open(STUDENT_SCORES_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(STUDENT_SCORES_HEADERS)
    recompute_benchmarks_csv(db)
    return {"status": "success", "message": "All student exam records cleared successfully."}


@app.get("/api/sessions/sync-external")
def sync_external_scores(session_id: str = None, student_id: str = None, db: Session = Depends(get_db)):
    """
    Checks external Module 10 database (gowtham_mentiscope.db)
    and syncs auditory_verbal scores if available.
    """
    import os
    import sqlite3
    import json

    ext_db_paths = [
        os.path.join(os.path.dirname(__file__), "modules", "auditory_verbal", "gowtham_mentiscope.db"),
        os.path.join(os.path.dirname(__file__), "gowtham_mentiscope.db"),
        "modules/auditory_verbal/gowtham_mentiscope.db",
        "backend/modules/auditory_verbal/gowtham_mentiscope.db"
    ]
    found_db = None
    for p in ext_db_paths:
        if os.path.exists(p):
            found_db = p
            break

    if not found_db:
        return {"status": "not_found", "message": "External database not located"}

    try:
        conn = sqlite3.connect(found_db)
        cur = conn.cursor()

        row = None
        if session_id:
            cur.execute("SELECT session_id, candidate_id, overall_cognitive_index, construct_scores FROM assessment_reports WHERE session_id = ? ORDER BY created_at DESC LIMIT 1", (session_id,))
            row = cur.fetchone()
        if not row and student_id:
            cur.execute("SELECT session_id, candidate_id, overall_cognitive_index, construct_scores FROM assessment_reports WHERE candidate_id = ? ORDER BY created_at DESC LIMIT 1", (student_id,))
            row = cur.fetchone()
        if not row:
            cur.execute("SELECT session_id, candidate_id, overall_cognitive_index, construct_scores FROM assessment_reports WHERE overall_cognitive_index > 0 ORDER BY created_at DESC LIMIT 1")
            row = cur.fetchone()
        conn.close()

        if not row:
            return {"status": "no_external_data", "message": "No external assessment reports found"}

        ext_sess_id, cand_id, overall_idx, raw_constructs = row
        score_val = float(overall_idx) if overall_idx is not None else 72.0

        if score_val < 10.0 and score_val > 0.0:
            score_val = score_val * 10.0
        score_val = round(score_val)

        subscores = {}
        if raw_constructs:
            try:
                subscores = json.loads(raw_constructs) if isinstance(raw_constructs, str) else raw_constructs
            except Exception:
                subscores = {}

        metrics = {
            "score": score_val,
            "constructScores": subscores,
            "externalCandidateId": cand_id,
            "externalSessionId": ext_sess_id
        }

        target_sess_id = session_id
        if not target_sess_id and student_id:
            latest = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.student_id == student_id).order_by(SavedAssessmentSession.updated_at.desc()).first()
            if latest:
                target_sess_id = latest.session_id
        if not target_sess_id:
            latest = db.query(SavedAssessmentSession).order_by(SavedAssessmentSession.updated_at.desc()).first()
            if latest:
                target_sess_id = latest.session_id

        if target_sess_id:
            sess_rec = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.session_id == target_sess_id).first()
            if sess_rec and sess_rec.payload:
                p = dict(sess_rec.payload)
                mod_scores = dict(p.get("moduleScores", {}))
                mod_scores["auditory_verbal"] = score_val
                p["moduleScores"] = mod_scores
                mod_metrics = dict(p.get("moduleMetrics", {}))
                mod_metrics["auditory_verbal"] = metrics
                p["moduleMetrics"] = mod_metrics
                p["overallScore"] = round(sum(mod_scores.values()) / len(mod_scores))
                sess_rec.payload = p
                db.commit()
                return {
                    "status": "synced",
                    "sessionId": target_sess_id,
                    "moduleId": "auditory_verbal",
                    "score": score_val,
                    "metrics": metrics,
                    "session": p
                }

        return {
            "status": "found_not_saved",
            "moduleId": "auditory_verbal",
            "score": score_val,
            "metrics": metrics
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

AV_QUESTIONS_LIST = [
    {
        "id": "av-1",
        "text": "Based on the operations audio briefing, what was the primary cause of the shipment delay at the terminal?",
        "story": "Auditory Working Memory (Verbatim Delay Recall): Listen/read the operational briefing and identify the primary causal factor.",
        "options": [
            "Port labor strike",
            "Severe weather condition",
            "Engine component failure",
            "Customs paperwork error"
        ],
        "type": "choice"
    },
    {
        "id": "av-2",
        "text": "Which cargo category was designated for emergency prioritized re-routing?",
        "story": "Selective Auditory Attention (Critical Detail Extraction): Isolate high-priority cargo specifications amidst background communications.",
        "options": [
            "Perishable medical supplies",
            "Commercial electronics",
            "Automotive replacement parts",
            "Construction steel beams"
        ],
        "type": "choice"
    },
    {
        "id": "av-3",
        "text": "What primary strategic trade-off must the logistics operations team resolve during this disruption?",
        "story": "Listening Comprehension & Synthesis: Synthesize multi-variable logistical trade-offs under operational pressure.",
        "options": [
            "Balancing emergency medical shipment deadlines against commercial delay penalties",
            "Replacing the entire port staff with temporary volunteers",
            "Selling all container inventory at discounted rates",
            "Building a new cargo terminal by the end of the day"
        ],
        "type": "choice"
    },
    {
        "id": "av-4",
        "text": "What downstream consequence is projected if secondary container inspections are skipped to save time?",
        "story": "Verbal Inference & Risk Analysis: Track procedural causality from shortcut actions to compliance risks.",
        "options": [
            "Processing speed increases initially, but customs hold risks remain higher later",
            "All port operations automatically shut down",
            "Vessels are forced to return to international waters immediately",
            "Commercial penalties are canceled by the shipping line"
        ],
        "type": "choice"
    },
    {
        "id": "av-5",
        "text": "When delivering the crisis briefing to the field team, which verbal strategy optimizes both compliance and morale?",
        "story": "Verbal Delivery & Metacognitive Communication: Select clear, transparent instructional delivery under crisis conditions.",
        "options": [
            "Clearly state safety protocols first, explain priority trade-offs, and establish verified checkpoints",
            "Instruct team members to bypass standard checks to avoid delays",
            "Withhold information about port penalties until all shipments depart",
            "Delegate critical decisions to individual drivers without central coordination"
        ],
        "type": "choice"
    }
]

AV_ANSWER_KEY = {
    "av-1": "Severe weather condition",
    "av-2": "Perishable medical supplies",
    "av-3": "Balancing emergency medical shipment deadlines against commercial delay penalties",
    "av-4": "Processing speed increases initially, but customs hold risks remain higher later",
    "av-5": "Clearly state safety protocols first, explain priority trade-offs, and establish verified checkpoints"
}
_av_answers: dict[str, dict[str, Any]] = {}

@app.post("/api/modules/auditory_verbal/start")
def start_auditory_verbal(payload: dict[str, Any], db: Session = Depends(get_db)):
    import time
    session_id = payload.get("sessionId") or payload.get("session_id") or f"sess_av_{int(time.time()*1000)}"
    _av_answers[session_id] = {}
    return {
        "status": "success",
        "sessionId": session_id,
        "moduleId": "auditory_verbal",
        "moduleName": "Auditory & Verbal Cognitive Assessment",
        "totalQuestions": len(AV_QUESTIONS_LIST),
        "questions": AV_QUESTIONS_LIST
    }

@app.post("/api/modules/auditory_verbal/answer")
def answer_auditory_verbal(payload: dict[str, Any], db: Session = Depends(get_db)):
    session_id = payload.get("sessionId") or payload.get("session_id")
    qid = payload.get("questionId") or payload.get("question_id") or ""
    ans = str(payload.get("answer", "")).strip().lower()
    expected = AV_ANSWER_KEY.get(qid, "").strip().lower()
    is_correct = bool(expected and ans == expected)
    if session_id:
        if session_id not in _av_answers:
            _av_answers[session_id] = {}
        _av_answers[session_id][qid] = {
            "answer": payload.get("answer"),
            "isCorrect": is_correct,
            "durationMs": payload.get("durationMs", 0)
        }
    return {
        "status": "success",
        "isCorrect": is_correct,
        "feedback": "Correct! Accurate auditory-verbal comprehension." if is_correct else "Response recorded."
    }

@app.post("/api/modules/auditory_verbal/finish")
def finish_auditory_verbal(payload: dict[str, Any], db: Session = Depends(get_db)):
    session_id = payload.get("sessionId") or payload.get("session_id")
    student_id = payload.get("studentId") or payload.get("student_id") or "stud_candidate"
    answers = payload.get("answers") or []
    
    recorded = _av_answers.get(session_id, {})
    for a in answers:
        qid = a.get("questionId") or a.get("question_id") or ""
        ans = str(a.get("answer", "")).strip().lower()
        expected = AV_ANSWER_KEY.get(qid, "").strip().lower()
        is_corr = a.get("isCorrect")
        if is_corr is None:
            is_corr = bool(expected and ans == expected)
        recorded[qid] = {
            "answer": a.get("answer"),
            "isCorrect": is_corr,
            "durationMs": a.get("durationMs", 0)
        }
    
    total_q = len(AV_ANSWER_KEY)
    correct_count = sum(1 for item in recorded.values() if item.get("isCorrect"))
    accuracy = round((correct_count / total_q) * 100.0, 1) if total_q > 0 else 0.0

    # Fallback to explicit external score if passed without answers
    if payload.get("scorePercentage") is not None and not answers:
        accuracy = float(payload.get("scorePercentage"))
    elif payload.get("overall_cognitive_index") is not None and not answers:
        accuracy = float(payload.get("overall_cognitive_index"))
        if 0 < accuracy < 10:
            accuracy *= 10.0

    metrics = {
        "raw_score": correct_count,
        "total_questions": total_q,
        "accuracy": accuracy,
        "listening_comprehension_score": accuracy,
        "verbal_reasoning_index": round(accuracy * 0.96, 1),
        "status": "Completed"
    }

    update_session_score({
        "sessionId": session_id,
        "studentId": student_id,
        "moduleId": "auditory_verbal",
        "score": accuracy,
        "metrics": metrics
    }, db=db)

    return {
        "status": "success",
        "scorePercentage": accuracy,
        "metrics": metrics
    }

@app.get("/api/sessions/history")
def get_session_history(student_id: str, db: Session = Depends(get_db)):
    records = db.query(SavedAssessmentSession).filter(
        SavedAssessmentSession.student_id == student_id
    ).order_by(SavedAssessmentSession.updated_at.desc()).all()
    sessions = [r.payload for r in records if r.payload]
    return {"status": "success", "sessions": sessions}

@app.delete("/api/sessions/{session_id}")
def delete_session_history(session_id: str, db: Session = Depends(get_db)):
    record = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.session_id == session_id).first()
    if record:
        db.delete(record)
        db.commit()
    return {"status": "success", "sessionId": session_id}

@app.get("/")
def root():
    return {
        "title": "Mentiscope Unified Cognitive Assessment Platform",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/api/sessions/{session_id}")
def get_session_by_id(session_id: str, db: Session = Depends(get_db)):
    record = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.session_id == session_id).first()
    if not record or not record.payload:
        raise HTTPException(status_code=404, detail="Session not found")
    return record.payload

@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "platform": "Mentiscope Cognitive Platform",
        "modules": ["processing-speed", "gf", "gsm", "attention", "emotional-regulation", "riasec", "gv", "quantitative", "auditory_verbal"]
    }


