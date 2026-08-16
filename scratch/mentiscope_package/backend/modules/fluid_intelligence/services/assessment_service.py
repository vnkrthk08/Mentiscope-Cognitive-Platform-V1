from datetime import datetime
import json
import logging

from ..puzzle_engine import AssessmentBuilder
from ..renderer import SVGRenderer
from ..scorer import AssessmentScorer
from ..analytics import AnalyticsEngine
from ..models import InteractionEvent, EventType, DifficultyLevel
from ..repositories.assessment_repository import FluidIntelligenceRepository

logger = logging.getLogger(__name__)

_assessment_cache = {}

class FluidIntelligenceAssessmentService:
    def __init__(self, repository: FluidIntelligenceRepository):
        self.repository = repository
        self.builder = AssessmentBuilder()
        self.renderer = SVGRenderer()
        self.scorer = AssessmentScorer()
        self.analytics = AnalyticsEngine()

    def _build_assessment(self, seed: str):
        if seed in _assessment_cache:
            return _assessment_cache[seed]

        import hashlib
        from ..models import AnswerOption
        int_seed = int(hashlib.md5(seed.encode()).hexdigest(), 16) % (2**32)
        assessment = self.builder.__class__(seed=int_seed).with_progression().build()

        # Fix deterministic puzzle IDs and option IDs across session lifetime
        for p_idx, puzzle in enumerate(assessment.puzzles):
            p_id = f"gf_puzzle_{p_idx+1}"
            object.__setattr__(puzzle, "puzzle_id", p_id)
            stable_options = []
            correct_opt_id = None
            for opt_idx, opt in enumerate(puzzle.question.options):
                full_opt_id = f"{p_id}_opt_{opt_idx}"
                if opt.option_id == puzzle.question.correct_option_id:
                    correct_opt_id = full_opt_id
                stable_options.append(AnswerOption(card=opt.card, misconception=opt.misconception, option_id=full_opt_id))
            object.__setattr__(puzzle.question, "options", tuple(stable_options))
            object.__setattr__(puzzle.question, "correct_option_id", correct_opt_id or f"{p_id}_opt_0")

        _assessment_cache[seed] = assessment
        return assessment

    def start(self, session_id: str, student_id: str | None) -> dict:
        self.repository.ensure_session(session_id, student_id)
        assessment = self._build_assessment(session_id)
        questions = []
        for p_idx, puzzle in enumerate(assessment.puzzles):
            examples = []
            for ex in puzzle.examples:
                examples.append({
                    "inputSvg": self.renderer.render_card(ex.input_card),
                    "outputSvg": self.renderer.render_card(ex.output_card)
                })
            options = []
            for idx, opt in enumerate(puzzle.question.options):
                options.append({
                    "id": opt.option_id,
                    "label": f"Option {chr(65 + idx)}",
                    "svgContent": self.renderer.render_card(opt.card)
                })
            q_payload = {
                "id": puzzle.puzzle_id,
                "type": "svg-matrix",
                "text": "Identify the pattern to find the missing puzzle output.",
                "story": f"Rule Family: {puzzle.hidden_rule.family.value}",
                "difficulty": puzzle.difficulty.value,
                "svgContent": self.renderer.render_card(puzzle.question.input_card),
                "examples": examples,
                "svgOptions": options,
                "correctAnswer": puzzle.question.correct_option_id
            }
            questions.append(q_payload)
        return {"status": "success", "totalQuestions": len(questions), "questions": questions}

    def answer(self, session_id: str, question_id: str, answer: str, duration_ms: int) -> dict:
        assessment = self._build_assessment(session_id)
        puzzle = next((p for p in assessment.puzzles if p.puzzle_id == question_id), None)
        is_correct = False
        difficulty = "medium"
        feedback = "Invalid puzzle."
        if puzzle:
            is_correct = puzzle.question.is_correct(answer)
            difficulty = puzzle.difficulty.value
            correct_idx = next((i for i, opt in enumerate(puzzle.question.options) if opt.option_id == puzzle.question.correct_option_id), None)
            correct_label = f"Option {chr(65 + correct_idx)}" if correct_idx is not None else "the target option"
            if is_correct:
                feedback = "Correct! The pattern matches the rule."
            else:
                feedback = f"Incorrect. The correct answer was {correct_label}."
        self.repository.record_answer(session_id, question_id, answer, is_correct, duration_ms, difficulty)
        return {"isCorrect": is_correct, "feedback": feedback}

    def finish(self, session_id: str) -> dict:
        assessment = self._build_assessment(session_id)
        raw_responses = self.repository.responses(session_id)
        raw_events = self.repository.events(session_id)
        responses_map = {r.item_id: r.response for r in raw_responses}
        events = []
        for e in raw_events:
            diff_str = e.payload.get("difficulty")
            diff_level = None
            try:
                if diff_str:
                    diff_level = DifficultyLevel(diff_str)
            except Exception:
                diff_level = DifficultyLevel.MEDIUM

            events.append(InteractionEvent(
                event_type=EventType.ANSWER_SUBMITTED,
                assessment_id=assessment.assessment_id,
                participant_id=session_id,
                puzzle_id=e.payload.get("item_id"),
                reaction_time_ms=e.payload.get("reaction_time_ms"),
                difficulty=diff_level
            ))
        score_report = self.scorer.score(assessment, responses_map, events)
        analytics_report = self.analytics.analyze(assessment, responses_map, events)
        combined_payload = {"score": score_report.to_dict(), "analytics": analytics_report.to_dict()}
        self.repository.save_result(session_id, score_report.normalized_score, combined_payload)
        return {"status": "completed", "scorePercentage": score_report.normalized_score, "metrics": combined_payload}

    def result(self, session_id: str) -> dict | None:
        result = self.repository.result(session_id)
        if not result:
            return None
        return {"moduleId": "gf", "score": result.score_percentage, "metrics": result.payload}

    def result_for_student(self, student_id: str) -> dict | None:
        result = self.repository.result_for_student(student_id)
        if not result:
            return None
        return {"moduleId": "gf", "score": result.score_percentage, "metrics": result.payload}


