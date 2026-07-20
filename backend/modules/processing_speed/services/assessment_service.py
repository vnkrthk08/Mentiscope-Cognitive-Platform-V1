from statistics import mean

from fastapi import HTTPException

from ..engine import generate_trial
from ..repositories import ProcessingSpeedRepository


class ProcessingSpeedAssessmentService:
    _trials: dict[str, dict] = {}
    _difficulty: dict[str, int] = {}

    def __init__(self, repository: ProcessingSpeedRepository):
        self.repository = repository

    def start(self, session_id: str, student_id: str | None) -> dict:
        self.repository.ensure_session(session_id, student_id)
        self._difficulty.setdefault(session_id, 1)
        trial = self._next_trial(session_id, 1)
        return {"status": "success", "totalQuestions": 20, "question": self._question_payload(trial)}

    def answer(self, session_id: str, question_id: str, answer: str, duration_ms: int) -> dict:
        trial = self._trials.get(session_id)
        if trial is None or trial["id"] != question_id:
            raise HTTPException(status_code=409, detail="No active Processing Speed item matches this response.")
        correct = trial["correct_answer"] == answer
        self.repository.record_answer(session_id, question_id, answer, correct, duration_ms, trial["difficulty_level"])
        difficulty = self._difficulty.get(session_id, 1)
        self._difficulty[session_id] = max(1, min(10, difficulty + (1 if correct and duration_ms < 2500 else -1 if not correct else 0)))
        next_trial = self._next_trial(session_id, int(question_id.rsplit("-", 1)[1]) + 1)
        return {"status": "success", "isCorrect": correct, "feedback": "Duplicate identified." if correct else "Response recorded.", "nextQuestion": self._question_payload(next_trial)}

    def finish(self, session_id: str) -> dict:
        responses = self.repository.responses(session_id)
        answered = len(responses)
        correct = sum(response.correct for response in responses)
        accuracy = (correct / answered * 100) if answered else 0
        avg_latency = round(mean([response.reaction_time_ms for response in responses])) if responses else 0
        speed_component = max(0, min(100, round(100 * (1 - max(0, avg_latency - 500) / 3500)))) if answered else 0
        score = round(accuracy * 0.7 + speed_component * 0.3)
        analytics = {"correct_responses": correct, "commission_errors": answered - correct, "omission_errors": max(0, 20 - answered), "average_reaction_time_ms": avg_latency, "speed_accuracy_tradeoff": score}
        self.repository.save_result(session_id, score, analytics)
        return {"status": "success", "scorePercentage": score, "analytics": analytics}

    def result(self, session_id: str) -> dict:
        result = self.repository.result(session_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Processing Speed result has not been generated.")
        return {"moduleId": "processing-speed", "score": result.score_percentage, "analytics": result.payload}

    def _next_trial(self, session_id: str, number: int) -> dict:
        trial = generate_trial(number, self._difficulty.get(session_id, 1))
        self._trials[session_id] = trial
        return trial

    @staticmethod
    def _question_payload(trial: dict) -> dict:
        return {key: value for key, value in trial.items() if key != "correct_answer"}
