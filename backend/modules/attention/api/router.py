import time
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

try:
    from database import get_db
    from core_models import SavedAssessmentSession
except ImportError:
    from ....database import get_db
    from ....core_models import SavedAssessmentSession

from ..models import AttentionSession, AttentionEvent, AttentionScore
from ..schemas import (
    AttentionStartRequest, AttentionStartResponse,
    AttentionAnswerRequest, AttentionAnswerResponse,
    AttentionFinishRequest, AttentionFinishResponse
)
from ..scorer import (
    score_sustained, score_selective, score_divided, score_executive,
    score_overall, estimate_percentile
)

router = APIRouter()

@router.post("/start", response_model=AttentionStartResponse)
def start_attention(payload: AttentionStartRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id or f"sess_att_{int(time.time()*1000)}"
    stu_id = payload.studentId or payload.student_id or "stud_candidate"

    existing = db.query(AttentionSession).filter(AttentionSession.session_id == sess_id).first()
    if not existing:
        sess = AttentionSession(
            session_id=sess_id,
            student_id=stu_id,
            status="in_progress",
            start_time=time.time()
        )
        db.add(sess)
        db.commit()

    return AttentionStartResponse(
        status="success",
        sessionId=sess_id,
        moduleId="attention",
        moduleName="Adaptive Shape Attention Task (ASAT)",
        construct="Attention & Executive Control",
        submodules=["sustained", "selective", "divided", "executive"],
        totalTrials=112
    )

@router.post("/answer", response_model=AttentionAnswerResponse)
def answer_attention(payload: AttentionAnswerRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id
    if not sess_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    event = AttentionEvent(
        session_id=sess_id,
        submodule=payload.submodule,
        trial_index=payload.trialIndex,
        stimulus=payload.stimulus,
        response=payload.response,
        is_correct=1 if payload.isCorrect else 0,
        reaction_time_ms=payload.reactionTimeMs,
        timestamp=time.time()
    )
    db.add(event)
    db.commit()

    return AttentionAnswerResponse(status="success", recorded=True)

@router.post("/finish", response_model=AttentionFinishResponse)
def finish_attention(payload: AttentionFinishRequest, db: Session = Depends(get_db)):
    sess_id = payload.sessionId or payload.session_id
    stu_id = payload.studentId or payload.student_id or "stud_candidate"
    if not sess_id:
        raise HTTPException(status_code=400, detail="Missing sessionId")

    sess = db.query(AttentionSession).filter(AttentionSession.session_id == sess_id).first()
    if sess:
        sess.status = "completed"
        sess.end_time = time.time()
        sess.completion_time_sec = int(sess.end_time - sess.start_time)
        db.commit()

    # Query events from database
    events = db.query(AttentionEvent).filter(AttentionEvent.session_id == sess_id).all()

    # If submodule scores provided by frontend scoring engine, prefer them or compute from events
    client_subscores = payload.submoduleScores or {}
    client_results = payload.moduleResults or {}

    sustained_score = client_subscores.get("sustained")
    selective_score = client_subscores.get("selective")
    divided_score = client_subscores.get("divided")
    executive_score = client_subscores.get("executive")

    if sustained_score is None or selective_score is None or divided_score is None or executive_score is None:
        # Calculate from logged events
        sub_events: Dict[str, list] = {"sustained": [], "selective": [], "divided": [], "executive": []}
        for ev in events:
            if ev.submodule in sub_events:
                sub_events[ev.submodule].append(ev)

        # Sustained
        sust = sub_events["sustained"]
        sust_hits = sum(1 for e in sust if e.is_correct and e.response == "SPACE")
        sust_rts = [e.reaction_time_ms for e in sust if e.reaction_time_ms > 0]
        sust_res = score_sustained(
            hits=sust_hits,
            total_targets=max(1, len(sust) // 3),
            rt_list=sust_rts,
            total_distractors=max(1, len(sust) - (len(sust) // 3)),
            false_alarms=sum(1 for e in sust if not e.is_correct)
        )
        sustained_score = sustained_score or sust_res["score"]

        # Selective
        sel = sub_events["selective"]
        sel_hits = sum(1 for e in sel if e.is_correct)
        sel_rts = [e.reaction_time_ms for e in sel if e.reaction_time_ms > 0]
        sel_res = score_selective(
            correct_clicks=sel_hits,
            total_targets=max(1, len(sel)),
            wrong_clicks=sum(1 for e in sel if not e.is_correct),
            total_distractors=max(1, len(sel) * 4),
            rt_list=sel_rts
        )
        selective_score = selective_score or sel_res["score"]

        # Divided
        div = sub_events["divided"]
        div_hits = sum(1 for e in div if e.is_correct)
        div_rts = [e.reaction_time_ms for e in div if e.reaction_time_ms > 0]
        div_res = score_divided(
            correct_presses=div_hits,
            total_targets=max(1, len(div) // 4),
            false_presses=sum(1 for e in div if not e.is_correct),
            total_non_targets=max(1, len(div) - (len(div) // 4)),
            rt_list=div_rts
        )
        divided_score = divided_score or div_res["score"]

        # Executive
        exec_ev = sub_events["executive"]
        exec_hits = sum(1 for e in exec_ev if e.is_correct)
        exec_rts = [e.reaction_time_ms for e in exec_ev if e.reaction_time_ms > 0]
        exec_res = score_executive(
            rt_before_switch=exec_rts[0] if exec_rts else 400.0,
            rt_after_switch=exec_rts[-1] if len(exec_rts) > 1 else 450.0,
            switch_errors=sum(1 for e in exec_ev if not e.is_correct),
            total_after_switch=max(1, len(exec_ev) // 2),
            rt_list=exec_rts
        )
        executive_score = executive_score or exec_res["score"]

    overall = score_overall(
        sustained=sustained_score or 75.0,
        selective=selective_score or 75.0,
        divided=divided_score or 75.0,
        executive=executive_score or 75.0
    )
    percentile = estimate_percentile(overall)

    metrics_payload = {
        "overallScore": overall,
        "percentile": percentile,
        "submoduleScores": {
            "sustained": sustained_score,
            "selective": selective_score,
            "divided": divided_score,
            "executive": executive_score
        },
        "details": client_results
    }

    # Save to attention_scores table
    existing_score = db.query(AttentionScore).filter(AttentionScore.session_id == sess_id).first()
    if existing_score:
        existing_score.overall_score = overall
        existing_score.sustained_score = sustained_score
        existing_score.selective_score = selective_score
        existing_score.divided_score = divided_score
        existing_score.executive_score = executive_score
        existing_score.percentile = percentile
        existing_score.metrics_json = metrics_payload
    else:
        att_score = AttentionScore(
            session_id=sess_id,
            student_id=stu_id,
            overall_score=overall,
            sustained_score=sustained_score,
            selective_score=selective_score,
            divided_score=divided_score,
            executive_score=executive_score,
            percentile=percentile,
            metrics_json=metrics_payload
        )
        db.add(att_score)

    # CRITICAL: Sync directly to SavedAssessmentSession in mentiscope.db so report gets live score immediately!
    existing_sess = db.query(SavedAssessmentSession).filter(SavedAssessmentSession.session_id == sess_id).first()
    if existing_sess and existing_sess.payload:
        data = dict(existing_sess.payload)
        mod_scores = dict(data.get("moduleScores", {}))
        mod_scores["attention"] = overall
        data["moduleScores"] = mod_scores
        mod_metrics = dict(data.get("moduleMetrics", {}))
        mod_metrics["attention"] = metrics_payload
        data["moduleMetrics"] = mod_metrics
        if len(mod_scores) > 0:
            data["overallScore"] = round(sum(mod_scores.values()) / len(mod_scores))
        existing_sess.payload = data
    elif existing_sess:
        existing_sess.payload = {
            "sessionId": sess_id,
            "studentId": stu_id,
            "moduleScores": {"attention": overall},
            "moduleMetrics": {"attention": metrics_payload},
            "overallScore": round(overall),
            "status": "completed"
        }
    else:
        new_sess = SavedAssessmentSession(
            session_id=sess_id,
            student_id=stu_id,
            payload={
                "sessionId": sess_id,
                "studentId": stu_id,
                "moduleScores": {"attention": overall},
                "moduleMetrics": {"attention": metrics_payload},
                "overallScore": round(overall),
                "status": "completed"
            }
        )
        db.add(new_sess)

    db.commit()

    return AttentionFinishResponse(
        status="success",
        sessionId=sess_id,
        scorePercentage=overall,
        percentile=percentile,
        metrics=metrics_payload
    )

@router.get("/result/{session_id}")
def get_attention_result(session_id: str, db: Session = Depends(get_db)):
    score = db.query(AttentionScore).filter(AttentionScore.session_id == session_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="Result not found for session")
    return {
        "status": "success",
        "sessionId": score.session_id,
        "studentId": score.student_id,
        "overallScore": score.overall_score,
        "percentile": score.percentile,
        "submoduleScores": {
            "sustained": score.sustained_score,
            "selective": score.selective_score,
            "divided": score.divided_score,
            "executive": score.executive_score
        },
        "metrics": score.metrics_json
    }
