from datetime import datetime
from typing import Dict, Any

try:
    from modules.quantitative.repositories.session_repository import SessionRepository
    from modules.quantitative.models.student_response import StudentResponse
    from modules.quantitative.models.session import AssessmentSession as GqSession
    from modules.quantitative.core.enums import AssessmentStatus as SessionStatus
    from backend.core_models import SavedAssessmentSession
    from backend.admin_csv_service import record_student_score
except (ImportError, ValueError):
    from ..repositories.session_repository import SessionRepository
    from ..models.student_response import StudentResponse
    from ..models.session import AssessmentSession as GqSession
    from ..core.enums import AssessmentStatus as SessionStatus
    from core_models import SavedAssessmentSession
    from admin_csv_service import record_student_score

GQ_ANSWER_KEY = {
    "gq-1": "697.5 km",
    "gq-2": "12%",
    "gq-3": "5 minutes",
    "gq-4": "7.5 degrees",
    "gq-5": "6"
}

class FinishService:

    @staticmethod
    def finish(db, request):
        sess_id = getattr(request, "session_id", None) or getattr(request, "sessionId", None)
        stu_id = getattr(request, "student_id", None) or getattr(request, "studentId", None) or "stud_candidate"
        answers = getattr(request, "answers", None) or []

        session = SessionRepository.get_by_session_id(db, sess_id) if sess_id else None

        if session is None and sess_id:
            session = GqSession(
                student_id=stu_id,
                session_id=sess_id,
                module_id="gq",
                construct="Quantitative Reasoning",
                difficulty=1,
                status=SessionStatus.COMPLETED,
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow()
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        elif session:
            session.status = SessionStatus.COMPLETED
            session.ended_at = datetime.utcnow()
            db.commit()

        responses = []
        if session:
            responses = db.query(StudentResponse).filter(StudentResponse.session_id == session.id).all()

        correct_count = 0
        total_q = len(responses)

        if total_q > 0:
            correct_count = sum(1 for r in responses if r.correct)
        elif answers:
            total_q = len(answers)
            for a in answers:
                qid = str(a.get("questionId") or a.get("question_id") or "").lower()
                ans_str = str(a.get("answer") or "").strip().lower()
                expected = GQ_ANSWER_KEY.get(qid, "").lower()
                if expected and ans_str == expected:
                    correct_count += 1
                elif a.get("isCorrect"):
                    correct_count += 1
        else:
            total_q = 5
            correct_count = 0

        accuracy = round((correct_count / max(1, total_q)) * 100.0, 1)
        score_percentage = accuracy

        metrics = {
            "raw_score": correct_count,
            "total_questions": total_q,
            "accuracy": accuracy,
            "scorePercentage": score_percentage,
            "adaptive_level_achieved": session.difficulty if session and hasattr(session, "difficulty") else 1,
            "status": "Completed"
        }

        # Sync directly to SavedAssessmentSession
        try:
            saved = db.get(SavedAssessmentSession, sess_id)
            if saved and saved.payload:
                p = dict(saved.payload)
                mod_scores = dict(p.get("moduleScores", {}))
                mod_scores["gq"] = score_percentage
                p["moduleScores"] = mod_scores
                mod_metrics = dict(p.get("moduleMetrics", {}))
                mod_metrics["gq"] = metrics
                p["moduleMetrics"] = mod_metrics
                if len(mod_scores) > 0:
                    p["overallScore"] = round(sum(mod_scores.values()) / len(mod_scores))
                saved.payload = p
                db.commit()
            elif saved:
                saved.payload = {
                    "sessionId": sess_id,
                    "studentId": stu_id,
                    "moduleScores": {"gq": score_percentage},
                    "moduleMetrics": {"gq": metrics},
                    "overallScore": round(score_percentage),
                    "status": "completed"
                }
                db.commit()
            else:
                new_saved = SavedAssessmentSession(
                    session_id=sess_id,
                    student_id=stu_id,
                    payload={
                        "sessionId": sess_id,
                        "studentId": stu_id,
                        "moduleScores": {"gq": score_percentage},
                        "moduleMetrics": {"gq": metrics},
                        "overallScore": round(score_percentage),
                        "status": "completed"
                    }
                )
                db.add(new_saved)
                db.commit()
        except Exception as e:
            print("[Gq sync SavedAssessmentSession warning]", e)

        # Record to real-time CSV
        try:
            record_student_score(
                db=db,
                session_id=sess_id,
                student_id=stu_id,
                module_id="gq",
                score=score_percentage,
                metrics=metrics
            )
        except Exception as e:
            print("[Gq record_student_score warning]", e)

        return {
            "status": "Completed",
            "sessionId": sess_id,
            "scorePercentage": score_percentage,
            "metrics": metrics,
            "assessment_id": session.id if session else sess_id,
            "student_id": session.student_id if session else stu_id,
            "completed_at": session.ended_at if session else datetime.utcnow()
        }