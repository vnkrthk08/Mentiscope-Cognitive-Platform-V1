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
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

try:
    from .core_models import Base, SavedAssessmentSession
    from .database import engine, get_db
    from .auth_router import router as auth_router
    from .modules.processing_speed.api.router import router as processing_speed_router
except (ImportError, ValueError):
    from core_models import Base, SavedAssessmentSession
    from database import engine, get_db
    from auth_router import router as auth_router
    from modules.processing_speed.api.router import router as processing_speed_router

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

# 2. Fluid Intelligence (Gf)
if fluid_intelligence_router:
    app.include_router(fluid_intelligence_router, prefix="/api/modules/gf", tags=["gf"])

# 3. Working Memory Span (Gsm)
if gsm_router:
    app.include_router(gsm_router, prefix="/api/modules/gsm", tags=["gsm"])

# 4. Cognitive Stress & Resilience (CSR)
if csr_router:
    app.include_router(csr_router, prefix="/api/modules/csr", tags=["csr"])

# 5. Visual Processing (Gv)
if gv_router:
    app.include_router(gv_router, prefix="/api/modules/gv", tags=["gv"])

# 6. Quantitative Reasoning (Gq)
if quantitative_answer_router:
    app.include_router(quantitative_answer_router, prefix="/api/quantitative", tags=["quantitative"])
    app.include_router(quantitative_start_router, prefix="/api/quantitative", tags=["quantitative"])
    app.include_router(quantitative_finish_router, prefix="/api/quantitative", tags=["quantitative"])
    app.include_router(quantitative_result_router, prefix="/api/quantitative", tags=["quantitative"])


@app.on_event("startup")
async def startup_event():
    try:
        from .modules.gsm.database import init_db as init_gsm_db
        await init_gsm_db()
    except Exception as e:
        print("[Startup Warning] GSM DB Init:", e)

    try:
        from .modules.quantitative.database.base import Base as QuantBase
        from .modules.quantitative.database.database import engine as quant_engine
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
    else:
        record = SavedAssessmentSession(
            session_id=session_id,
            student_id=student_id,
            payload=payload
        )
        db.add(record)
    
    db.commit()
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

@app.post("/api/modules/auditory_verbal/finish")
def finish_auditory_verbal(payload: dict[str, Any], db: Session = Depends(get_db)):
    session_id = payload.get("sessionId") or payload.get("session_id")
    student_id = payload.get("studentId") or payload.get("student_id") or "stud_alex_mercer"
    raw_score = payload.get("scorePercentage") or payload.get("score") or payload.get("overall_cognitive_index") or 82.0
    metrics = payload.get("metrics") or payload.get("analytics") or {}
    score = float(raw_score)
    return update_session_score({
        "sessionId": session_id,
        "studentId": student_id,
        "moduleId": "auditory_verbal",
        "score": score,
        "metrics": metrics
    }, db=db)

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

@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "platform": "Mentiscope Cognitive Platform",
        "modules": ["processing-speed", "gf", "gsm", "csr", "quantitative"]
    }

