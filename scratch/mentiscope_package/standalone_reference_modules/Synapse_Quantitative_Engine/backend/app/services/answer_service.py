from app.engine.adaptive_engine import AdaptiveEngine
from app.engine.assessment_engine import AssessmentEngine

from app.models.student_response import StudentResponse


from app.repositories.response_repository import ResponseRepository
from app.repositories.session_repository import SessionRepository

from app.services.event_service import EventService
from app.models.question_instance import QuestionInstance
from app.repositories.question_repository import QuestionRepository

class AnswerService:

    @staticmethod
    def submit_answer(db, request):

        # ---------------------------------------
        # Load Question
        # ---------------------------------------

        question = QuestionRepository.get_by_question_id(
            db,
            request.question_id,
        )

        if question is None:
            raise ValueError("Question not found")

        # ---------------------------------------
        # Load Assessment Session
        # ---------------------------------------

        session = SessionRepository.get_by_session_id(
            db,
            request.session_id,
        )

        if session is None:
            raise ValueError("Assessment session not found")

        # ---------------------------------------
        # Validate Answer
        # ---------------------------------------

        correct = (
            str(request.response)
            == str(question.correct_answer)
        )

        # ---------------------------------------
        # Save Student Response
        # ---------------------------------------

        ResponseRepository.create(

            db,

            StudentResponse(
                session_id=session.id,
                
                question_id=question.question_id,

                response=str(request.response),

                correct=correct,

                reaction_time_ms=request.metrics.reaction_time_ms,

                hover_duration_ms=request.metrics.hover_duration_ms,

                idle_time_ms=request.metrics.idle_time_ms,

                drag_distance=request.metrics.drag_distance,

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

            "correct": correct,

            "next_level": next_level,

            "next_question": next_question,
        }