from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.modules.gv.event_service import log_server_event, persist_client_events
from backend.modules.gv.item_bank.items import build_item_bank, get_item_and_key
from backend.modules.gv.item_service import evaluate_response
from backend.modules.gv.models import GvAnswer, GvResult, GvSession
from backend.modules.gv.schemas import AnswerRequest, AnswerResponse, PracticeFeedback


class DuplicateAnswerError(ValueError):
    pass


def submit_answer(db: Session, session: GvSession, payload: AnswerRequest) -> AnswerResponse:
    if db.get(GvResult, session.session_id) is not None:
        return AnswerResponse(
            accepted=False,
            duplicate=True,
            practice_feedback=None,
            next_step="already_completed",
            current_item_index=session.current_item_index,
        )

    existing_submission = db.scalar(
        select(GvAnswer).where(GvAnswer.submission_id == payload.submission_id)
    )
    if existing_submission is not None:
        feedback = None
        if existing_submission.practice:
            feedback = PracticeFeedback(
                correct=existing_submission.correct,
                message=(
                    "Correct. Continue when you are ready."
                    if existing_submission.correct
                    else "Not quite. Review the example and try the next practice item."
                ),
            )
        return AnswerResponse(
            accepted=True,
            duplicate=True,
            practice_feedback=feedback,
            next_step="next_item",
            current_item_index=session.current_item_index,
        )

    record = get_item_and_key(session.session_id, session.difficulty, payload.item_id)
    if record is None:
        raise ValueError("Unknown Gv item")
    if bool(record.safe["practice"]) != payload.practice:
        raise ValueError("Practice flag does not match the item")

    persist_client_events(db, session, payload.events)
    correct, distractor_type, score_detail = evaluate_response(
        session_id=session.session_id,
        difficulty=session.difficulty,
        item_id=payload.item_id,
        response=payload.response,
    )

    if record.safe["subtest_id"] == "mystery_map":
        piece_selection = float(score_detail.get("piece_selection_accuracy", 0.0))
        rotation_accuracy = float(score_detail.get("mental_rotation_accuracy", 0.0))
        placement_accuracy = float(score_detail.get("spatial_placement_accuracy", 0.0))
        strategy = max(
            0.0,
            100.0
            - payload.selection_changes * 4.0
            - max(0, payload.placement_attempts - int(score_detail.get("piece_count", 0))) * 3.0,
        )
        expected_ms = int(record.safe["expected_time_seconds"]) * 1000
        elapsed_ratio = payload.time_taken_ms / max(expected_ms, 1)
        efficiency = 100.0 if elapsed_ratio <= 1 else max(50.0, 100.0 - (elapsed_ratio - 1) * 25.0)
        score_detail["strategy_error_control"] = strategy
        score_detail["efficiency_score"] = efficiency
        score_detail["mystery_map_raw_score"] = (
            0.25 * piece_selection
            + 0.25 * rotation_accuracy
            + 0.20 * placement_accuracy
            + 0.15 * strategy
            + 0.15 * efficiency
        )

    answer = GvAnswer(
        submission_id=payload.submission_id,
        session_id=session.session_id,
        item_id=payload.item_id,
        subtest_id=record.safe["subtest_id"],
        practice=payload.practice,
        response=payload.response,
        correct=correct,
        time_taken_ms=payload.time_taken_ms,
        attempt_number=payload.attempt_number,
        selection_changes=payload.selection_changes,
        rotation_attempts=payload.rotation_attempts,
        placement_attempts=payload.placement_attempts,
        time_to_first_interaction_ms=payload.time_to_first_interaction_ms,
        distractor_type=distractor_type,
        score_detail=score_detail,
        device_metadata=payload.device_metadata,
    )
    db.add(answer)
    log_server_event(
        db,
        session,
        "answer_submitted",
        subtest_id=record.safe["subtest_id"],
        item_id=payload.item_id,
        response={"practice": payload.practice, "submission_id": payload.submission_id},
        correct=correct if payload.practice else None,
        time_taken=payload.time_taken_ms / 1000.0,
    )
    if payload.practice:
        log_server_event(
            db,
            session,
            "practice_answered",
            subtest_id=record.safe["subtest_id"],
            item_id=payload.item_id,
            correct=correct,
        )
    else:
        scored_order = session.item_order or []
        if payload.item_id in scored_order:
            session.current_item_index = max(
                session.current_item_index,
                scored_order.index(payload.item_id) + 1,
            )
    session.last_activity_at = datetime.utcnow()
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        duplicate = db.scalar(
            select(GvAnswer).where(
                GvAnswer.session_id == session.session_id,
                GvAnswer.item_id == payload.item_id,
                GvAnswer.practice.is_(payload.practice),
            )
        )
        if duplicate is None:
            raise
        return AnswerResponse(
            accepted=True,
            duplicate=True,
            practice_feedback=(
                PracticeFeedback(
                    correct=duplicate.correct,
                    message=(
                        "Correct. Continue when you are ready."
                        if duplicate.correct
                        else "Not quite. Review the example and continue."
                    ),
                )
                if payload.practice
                else None
            ),
            next_step="next_item",
            current_item_index=session.current_item_index,
        )

    bank = build_item_bank(session.session_id, session.difficulty)
    scored_count = sum(1 for records in bank.values() for item in records if not item.safe["practice"])
    next_step = "finish" if not payload.practice and session.current_item_index >= scored_count else "next_item"
    return AnswerResponse(
        accepted=True,
        duplicate=False,
        practice_feedback=(
            PracticeFeedback(
                correct=correct,
                message=(
                    "Correct. Continue when you are ready."
                    if correct
                    else "Not quite. Review the shape relationship and continue."
                ),
            )
            if payload.practice
            else None
        ),
        next_step=next_step,
        current_item_index=session.current_item_index,
    )
