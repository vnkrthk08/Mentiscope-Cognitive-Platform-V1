"""
==========================================================
Result Service
==========================================================
"""

from modules.quantitative.engine.analytics_engine import AnalyticsEngine

from modules.quantitative.repositories.event_repository import EventRepository
from modules.quantitative.repositories.response_repository import ResponseRepository
from modules.quantitative.repositories.session_repository import SessionRepository


class ResultService:

    @staticmethod
    def result(
        db,
        assessment_id,
    ):

        # ---------------------------------------------------------
        # Session
        # ---------------------------------------------------------

        session = SessionRepository.get_by_id(
            db,
            assessment_id,
        )

        if session is None:
            raise ValueError(
                "Assessment session not found"
            )

        # ---------------------------------------------------------
        # Responses
        # ---------------------------------------------------------

        responses = ResponseRepository.get_all_for_session(
            db,
            session.id,
        )

        # ---------------------------------------------------------
        # Analytics
        # ---------------------------------------------------------

        analytics = AnalyticsEngine.compute(
            responses
        )

        # ---------------------------------------------------------
        # Question History
        # ---------------------------------------------------------

        from modules.quantitative.repositories.question_repository import QuestionRepository

        history = []

        for response in responses:
            question_instance = QuestionRepository.get_by_question_id(db, response.question_id)
            question_data = question_instance.question_json if question_instance else {}
            correct_answer = question_instance.correct_answer if question_instance else ""

            history.append({

                "question_id": response.question_id,

                "module": response.module_name,

                "difficulty": response.difficulty_level,

                "correct": response.correct,

                "response": response.response,

                "correct_answer": correct_answer,

                "question_data": question_data,

                "reaction_time_ms":
                    response.reaction_time_ms,

                "hover_duration_ms":
                    response.hover_duration_ms,

                "idle_time_ms":
                    response.idle_time_ms,

                "drag_distance":
                    response.drag_distance,

                "answer_changes":
                    response.answer_changes,

                "confidence_score":
                    response.confidence_score,

                "hint_used":
                    response.hint_used,

                "answered_at":
                    response.answered_at,
            })

        # ---------------------------------------------------------
        # Events
        # ---------------------------------------------------------

        try:

            events = EventRepository.get_all_for_session(
                db,
                session.session_id,
            )

            event_list = [

                {

                    "timestamp": e.timestamp,

                    "event_type": e.event_type,

                    "task_id": e.task_id,

                    "item_id": e.item_id,

                    "correct": e.correct,

                    "reaction_time_ms":
                        e.reaction_time_ms,

                    "difficulty":
                        e.difficulty_level,

                    "metadata":
                        e.event_metadata,

                }

                for e in events
            ]

        except Exception:

            event_list = []

        # ---------------------------------------------------------
        # Recommendations
        # ---------------------------------------------------------

        accuracy = analytics[
            "common_metrics"
        ]["accuracy"]

        recommendations = {

            "strengths": [],

            "areas_for_improvement": [],

            "recommended_practice": [],
        }

        if accuracy >= 80:

            recommendations["strengths"] = [

                "Pattern Recognition",

                "Problem Solving",

                "Quantitative Reasoning",

            ]

        elif accuracy >= 60:

            recommendations["strengths"] = [

                "Logical Reasoning",

            ]

            recommendations[
                "areas_for_improvement"
            ] = [

                "Arithmetic Speed",

            ]

        else:

            recommendations[
                "areas_for_improvement"
            ] = [

                "Numerical Reasoning",

                "Pattern Recognition",

                "Problem Solving",

            ]

        recommendations[
            "recommended_practice"
        ] = [

            "Sequence reasoning",

            "Data interpretation",

            "Mental arithmetic",

            "Logical comparison",

        ]

        # ---------------------------------------------------------
        # Response
        # ---------------------------------------------------------

        return {
            "student_id": session.student_id,
            "session_id": session.session_id,
            "module_id": session.module_id,
            "module_name": "Quantitative Ability",
            "construct": session.construct,
            "status": session.status.value if hasattr(session.status, "value") else str(session.status),
            "start_time": session.started_at.isoformat() if session.started_at else None,
            "end_time": session.ended_at.isoformat() if session.ended_at else None,
            "completion_time": int((session.ended_at - session.started_at).total_seconds()) if session.ended_at else 0,
            "timestamp": session.ended_at.isoformat() if session.ended_at else None,
            "metrics": {
                **analytics["common_metrics"],
                **analytics["gq_metrics"]
            },
            "recommendations": recommendations,
            "question_history": history,
            "events": event_list
        }