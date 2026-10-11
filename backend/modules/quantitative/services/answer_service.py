from modules.quantitative.engine.adaptive_engine import AdaptiveEngine
from modules.quantitative.engine.assessment_engine import AssessmentEngine

from modules.quantitative.models.student_response import StudentResponse


from modules.quantitative.repositories.response_repository import ResponseRepository
from modules.quantitative.repositories.session_repository import SessionRepository

from modules.quantitative.services.event_service import EventService
from modules.quantitative.models.question_instance import QuestionInstance
from modules.quantitative.repositories.question_repository import QuestionRepository

class AnswerService:

    @staticmethod
    def submit_answer(db, request):

        # ---------------------------------------
        # ---------------------------------------
        # Load Assessment Session
        # ---------------------------------------

        session = SessionRepository.get_by_session_id(
            db,
            request.session_id,
        )

        if session is None:
            from datetime import datetime
            from modules.quantitative.models.session import AssessmentSession as GqSession
            from modules.quantitative.core.enums import AssessmentStatus as SessionStatus
            session = GqSession(
                student_id="stud_candidate",
                session_id=request.session_id,
                module_id="gq",
                construct="Quantitative Reasoning",
                difficulty=1,
                status=SessionStatus.IN_PROGRESS,
                started_at=datetime.utcnow()
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        # ---------------------------------------
        # Load Question
        # ---------------------------------------

        question = QuestionRepository.get_by_question_id(
            db,
            request.question_id,
        )

        GQ_KEY = {
            "gq-1": "697.5 km",
            "gq-2": "12%",
            "gq-3": "5 minutes",
            "gq-4": "7.5 degrees",
            "gq-5": "6"
        }

        if question is not None:
            correct = (str(request.response).strip().lower() == str(question.correct_answer).strip().lower())
            q_id = question.question_id
        else:
            expected = GQ_KEY.get(request.question_id, "")
            correct = (str(request.response).strip().lower() == expected.strip().lower()) if expected else bool(request.response)
            q_id = request.question_id

        # ---------------------------------------
        # Save Student Response
        # ---------------------------------------

        rt_ms = request.duration_ms or (request.metrics.reaction_time_ms if request.metrics else 1500)

        ResponseRepository.create(
            db,
            StudentResponse(
                session_id=session.id,
                question_id=q_id,
                response=str(request.response),
                correct=correct,
                reaction_time_ms=rt_ms,
                hover_duration_ms=request.metrics.hover_duration_ms if request.metrics else 0,
                idle_time_ms=request.metrics.idle_time_ms if request.metrics else 0,
                drag_distance=request.metrics.drag_distance if request.metrics else 0,

                answer_changes=request.metrics.answer_changes,

                confidence_score=request.metrics.confidence_score,

                attempt_number=request.metrics.attempt_number,

                difficulty_level=request.metrics.difficulty_level,

                module_name=request.metrics.module_name,

                hint_used=request.metrics.hint_used,
            )
        )

        # ---------------------------------------
        # Event Logging
        # ---------------------------------------

        EventService.log_event(

            db=db,

            student_id=session.student_id,

            session_id=session.session_id,

            construct=session.construct,

            task_id=question.template_id,

            item_id=question.question_id,

            event_type="ANSWER_SUBMITTED",

            response=str(request.response),

            correct=correct,

            reaction_time_ms=request.metrics.reaction_time_ms,
            
            difficulty_level=request.metrics.difficulty_level,
            
            hint_used=request.metrics.hint_used,
        )

        # ---------------------------------------
        # Adaptive Engine
        # ---------------------------------------

        next_level = AdaptiveEngine.next_level(

            current_level=question.difficulty,

            correct=correct,

            response_time=request.metrics.reaction_time_ms / 1000,
            
            hint_used=request.metrics.hint_used,
            
            attempts=request.metrics.attempt_number,
        )

        # ---------------------------------------
        # Update Session State
        # ---------------------------------------

        session.current_level = next_level
        db.commit()
        db.refresh(session)

        # ---------------------------------------
        # Generate Next Question
        # ---------------------------------------

        next_question = AssessmentEngine.start(
            level=next_level,
            db=db,
            session_id=session.session_id
        )

        QuestionRepository.create(
            db,
            QuestionInstance(
                session_id=session.id,

                question_id=next_question["question_id"],

                template_id=next_question["template_id"],

                module=next_question["module"],

                difficulty=next_question["difficulty"],

                question_json=next_question,

                correct_answer=str(
                    next_question["correct_answer"]
                    ),
                )
            )

        # TODO:
        # Save next QuestionInstance here

        # ---------------------------------------
        # Response
        # ---------------------------------------

        return {
            "status": "success",
            "correct": correct,
            "isCorrect": correct,
            "feedback": "Correct! Excellent mathematical reasoning." if correct else "Response recorded.",
            "next_level": next_level,
            "next_question": next_question,
            "nextQuestion": next_question
        }