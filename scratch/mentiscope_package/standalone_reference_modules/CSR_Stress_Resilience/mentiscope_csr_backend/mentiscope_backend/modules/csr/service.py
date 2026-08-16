from datetime import datetime, timezone
from statistics import mean

from fastapi import HTTPException

from . import engine
from .repository import CsrRepository
from ...core_models import SessionRecord

TASK_TO_SUBSCORE_KEY = {
    "auditory": "auditory_memory",
    "visual": "visual_memory",
    "distractor": "interference_resistance",
    "sequential": "sequential_recall",
}


class CsrAssessmentService:
    """Classroom Scenario Recall (CSR) — Working Memory (Gsm) module service.

    Mirrors ProcessingSpeedAssessmentService's shape (start/answer/finish/result)
    so the shared AssessmentRunner can drive both modules identically, while the
    per-item logic and scoring model are CSR-specific (four Gsm sub-components:
    auditory recall, visual grid memory, distractor/interference resistance,
    sequential updating).
    """

    # In-memory per-session cursor + pending trial. Mirrors the Processing Speed
    # module's approach; acceptable for a single-instance MVP deployment.
    _position: dict[str, int] = {}
    _pending: dict[str, tuple[str, dict, str]] = {}  # session_id -> (task, item, question_id)
    _module_id: dict[str, str] = {}
    _started_at: dict[str, datetime] = {}

    def __init__(self, repository: CsrRepository):
        self.repository = repository

    # ------------------------------------------------------------------
    # API surface
    # ------------------------------------------------------------------
    def start(self, session_id: str, student_id: str | None) -> dict:
        self.repository.ensure_session(session_id, student_id)
        self._position[session_id] = 0
        self._started_at[session_id] = datetime.now(timezone.utc)
        question = self._load_trial(session_id, 0)
        return {
            "status": "success",
            "totalQuestions": engine.total_trials(),
            "question": question,
        }

    def answer(self, session_id: str, question_id: str, answer: str, duration_ms: int) -> dict:
        pending = self._pending.get(session_id)
        if pending is None or pending[2] != question_id:
            raise HTTPException(status_code=409, detail="No active CSR item matches this response.")
        task, item, _ = pending

        correct, error_type = engine.check_answer(task, item, answer)
        difficulty = engine.difficulty_for(item, task)
        # Persist using the bank item's own id (e.g. AUD-01) rather than the
        # sequential question_id, so finish() can attribute responses back to
        # their Gsm sub-component via the id prefix.
        self.repository.record_answer(session_id, item["id"], answer, correct, duration_ms, difficulty)

        position = self._position.get(session_id, 0) + 1
        self._position[session_id] = position

        if position >= engine.total_trials():
            return {"status": "success", "isCorrect": correct, "feedback": self._feedback(task, correct), "nextQuestion": None}

        next_question = self._load_trial(session_id, position)
        return {"status": "success", "isCorrect": correct, "feedback": self._feedback(task, correct), "nextQuestion": next_question}

    def finish(self, session_id: str) -> dict:
        responses = self.repository.responses(session_id)
        start_time = self._started_at.get(session_id)
        end_time = datetime.now(timezone.utc)
        completion_time = int((end_time - start_time).total_seconds()) if start_time else 0

        sub_scores = self._sub_scores(session_id, responses)
        raw_score = round(sum(sub_scores.values()) / 4, 1) if sub_scores else 0.0
        normalized_score = round(100 + (raw_score - 75) * 0.6, 1)
        percentile = max(1, min(99, round(50 + (raw_score - 75) * 1.2)))

        avg_rt = round(mean([r.reaction_time_ms for r in responses])) if responses else 0
        correct_count = sum(1 for r in responses if r.correct)
        confidence_score = 0.82 if len(responses) >= 8 else 0.55

        recommendations = []
        if sub_scores.get("interference_resistance", 100) < 60:
            recommendations.append("Consider targeted attention-control exercises; interference resistance below expected band.")
        if sub_scores.get("sequential_recall", 100) < 60:
            recommendations.append("Sequential updating below expected band; monitor multi-step instruction following.")
        if not recommendations:
            recommendations.append("Performance within expected range across all Gsm sub-components.")

        metrics = {
            "raw_score": raw_score,
            "normalized_score": normalized_score,
            "percentile": percentile,
            "confidence_score": confidence_score,
            "sub_scores": sub_scores,
            "accuracy": round((correct_count / len(responses)) * 100, 1) if responses else 0.0,
            "average_reaction_time_ms": avg_rt,
            "recommendations": recommendations,
        }

        score_percentage = raw_score
        self.repository.save_result(session_id, score_percentage, metrics)

        # Mandatory metadata per platform Output Specification (guidelines §5).
        output = {
            "student_id": self._student_id_for(session_id),
            "session_id": session_id,
            "module_id": "csr",
            "module_name": "Classroom Scenario Recall (Working Memory / Gsm)",
            "construct": "Gsm",
            "status": "Completed",
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat(),
            "completion_time": completion_time,
            "timestamp": end_time.isoformat(),
            "metrics": metrics,
        }
        return {"status": "success", "scorePercentage": score_percentage, "analytics": metrics, "output": output}

    def result(self, session_id: str) -> dict:
        result = self.repository.result(session_id)
        if result is None:
            raise HTTPException(status_code=404, detail="CSR result has not been generated.")
        return {"moduleId": "csr", "score": result.score_percentage, "analytics": result.payload}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_trial(self, session_id: str, position: int) -> dict:
        task, item, index_within_task = engine.trial_for_position(position)
        question_id = f"csr-{position + 1}"
        self._pending[session_id] = (task, item, question_id)
        return engine.build_question_payload(task, item, question_id)

    @staticmethod
    def _feedback(task: str, correct: bool) -> str:
        if correct:
            return {
                "auditory": "Chunk identified correctly.",
                "visual": "Grid pattern recalled correctly.",
                "distractor": "Correct.",
                "sequential": "Correct final order.",
            }[task]
        return "Response recorded."

    def _sub_scores(self, session_id: str, responses) -> dict:
        by_task: dict[str, list] = {"auditory": [], "visual": [], "distractor": [], "sequential": []}
        # item_id prefixes map deterministically back to task (AUD-, VIS-, DIS-, SEQ-)
        prefix_to_task = {"AUD": "auditory", "VIS": "visual", "DIS": "distractor", "SEQ": "sequential"}
        for r in responses:
            prefix = r.item_id.split("-")[0]
            task = prefix_to_task.get(prefix)
            if task:
                by_task[task].append(r)

        sub_scores = {}
        for task, key in TASK_TO_SUBSCORE_KEY.items():
            items = by_task[task]
            pct = (sum(1 for r in items if r.correct) / len(items) * 100) if items else 0.0
            sub_scores[key] = round(pct, 1)
        return sub_scores

    def _student_id_for(self, session_id: str) -> str | None:
        session = self.repository.db.get(SessionRecord, session_id)
        return session.student_id if session else None
