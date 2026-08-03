from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core_models import Base
from .database import engine

# Import Routers with Try/Except fallbacks
from .auth_router import router as auth_router
from .modules.processing_speed.api.router import router as processing_speed_router

try:
    from .modules.fluid_intelligence.api.router import router as fluid_intelligence_router
except Exception:
    fluid_intelligence_router = None

try:
    from .modules.gsm.routers.assessment import router as gsm_router
except Exception:
    gsm_router = None

try:
    from .modules.csr.api.router import router as csr_router
except Exception:
    csr_router = None

try:
    from .modules.gv.api.router import router as gv_router
except Exception:
    gv_router = None

try:
    from .modules.quantitative.api.answer import router as quantitative_answer_router
    from .modules.quantitative.api.start import router as quantitative_start_router
    from .modules.quantitative.api.finish import router as quantitative_finish_router
    from .modules.quantitative.api.result import router as quantitative_result_router
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



from typing import Any
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .core_models import SavedAssessmentSession

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

@app.get("/api/sessions/history")
def get_session_history(student_id: str, db: Session = Depends(get_db)):
    records = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.student_id == student_id).all()
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

