from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.modules.gv.config import REQUIRED_EVENT_TYPES, SUBTEST_WEIGHTS
from backend.modules.gv.item_bank.items import build_item_bank
from backend.modules.gv.models import GvAnswer, GvEvent, GvSession
from backend.modules.gv.schemas import Metrics


def clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def rounded(value: float | None, digits: int = 2) -> float | None:
    return None if value is None else round(value, digits)


def _accuracy(rows: list[GvAnswer]) -> float | None:
    if not rows:
        return None
    return sum(1 for row in rows if row.correct) / len(rows) * 100.0


def _partial_accuracy(row: GvAnswer) -> float:
    detail = row.score_detail or {}
    return float(detail.get("accuracy", 100.0 if row.correct else 0.0))


def _efficiency_for_answer(row: GvAnswer, expected_seconds: float) -> float:
    elapsed = max(row.time_taken_ms / 1000.0, 0.0)
    if elapsed <= expected_seconds:
        time_component = 100.0
    elif elapsed <= expected_seconds * 2:
        time_component = 100.0 - ((elapsed / expected_seconds) - 1.0) * 25.0
    elif elapsed <= expected_seconds * 3:
        time_component = 75.0 - ((elapsed / expected_seconds) - 2.0) * 20.0
    else:
        time_component = 50.0
    # Accuracy dominates. Slow but accurate responses retain a high efficiency
    # score; timing is intentionally secondary.
    return 0.75 * _partial_accuracy(row) + 0.25 * time_component


def compute_metrics(db: Session, session: GvSession) -> Metrics:
    answers = list(
        db.scalars(
            select(GvAnswer).where(
                GvAnswer.session_id == session.session_id,
                GvAnswer.practice.is_(False),
            )
        ).all()
    )
    bank = build_item_bank(session.session_id, session.difficulty)
    safe_by_id = {
        record.safe["item_id"]: record.safe
        for records in bank.values()
        for record in records
        if not record.safe["practice"]
    }
    by_subtest: dict[str, list[GvAnswer]] = defaultdict(list)
    for answer in answers:
        by_subtest[answer.subtest_id].append(answer)

    mental_rotation_accuracy = _accuracy(by_subtest["mental_rotation"])
    paper_folding_accuracy = _accuracy(by_subtest["paper_folding"])
    hidden_figures_accuracy = _accuracy(by_subtest["hidden_figures"])

    map_rows = by_subtest["mystery_map"]
    mystery_map_accuracy = (
        mean(float((row.score_detail or {}).get("mystery_map_raw_score", _partial_accuracy(row))) for row in map_rows)
        if map_rows
        else None
    )

    subtest_scores: dict[str, float | None] = {
        "mental_rotation": mental_rotation_accuracy,
        "paper_folding": paper_folding_accuracy,
        "hidden_figures": hidden_figures_accuracy,
        "mystery_map": mystery_map_accuracy,
    }
    available_weight = sum(
        SUBTEST_WEIGHTS[key] for key, value in subtest_scores.items() if value is not None
    )
    raw_score = (
        sum(SUBTEST_WEIGHTS[key] * float(value) for key, value in subtest_scores.items() if value is not None)
        / available_weight
        if available_weight
        else 0.0
    )

    total = len(answers)
    exact_correct = sum(1 for row in answers if row.correct)
    overall_accuracy = exact_correct / total * 100.0 if total else 0.0
    first_attempt_correct = sum(
        1 for row in answers if row.correct and row.attempt_number == 1 and row.selection_changes == 0
    )
    first_attempt_accuracy = first_attempt_correct / total * 100.0 if total else 0.0
    correction_count = sum(
        row.selection_changes + max(0, row.placement_attempts - int((row.score_detail or {}).get("piece_count", 0)))
        for row in answers
    )
    average_response_time = mean(row.time_taken_ms for row in answers) / 1000.0 if answers else 0.0

    single_choice_rows = [row for row in answers if row.subtest_id != "mystery_map"]
    distractor_count = sum(1 for row in single_choice_rows if not row.correct)
    distractor_selection_rate = distractor_count / len(single_choice_rows) * 100.0 if single_choice_rows else 0.0

    rotation_attempts_total = sum(row.rotation_attempts for row in answers)
    mr_rows = by_subtest["mental_rotation"]
    mirror_count = sum(
        1 for row in mr_rows if row.distractor_type and "mirror" in row.distractor_type
    )
    mirror_confusion_rate = mirror_count / len(mr_rows) * 100.0 if mr_rows else None

    expected_time = {
        item_id: float(safe_by_id[item_id].get("expected_time_seconds", 45))
        for item_id in safe_by_id
    }
    efficiency_values = [
        _efficiency_for_answer(row, expected_time.get(row.item_id, 45.0)) for row in answers
    ]
    efficiency_score = mean(efficiency_values) if efficiency_values else 0.0

    correction_penalty = min(35.0, correction_count * 2.0)
    distractor_penalty = min(30.0, distractor_selection_rate * 0.30)
    repeated_attempt_penalty = min(20.0, sum(max(0, row.attempt_number - 1) for row in answers) * 4.0)
    strategy_error_control = clamp(100.0 - correction_penalty - distractor_penalty - repeated_attempt_penalty)

    map_piece_selection = (
        mean(float((row.score_detail or {}).get("piece_selection_accuracy", 0.0)) for row in map_rows)
        if map_rows
        else None
    )
    map_placement = (
        mean(float((row.score_detail or {}).get("spatial_placement_accuracy", 0.0)) for row in map_rows)
        if map_rows
        else None
    )
    map_rotation = (
        mean(float((row.score_detail or {}).get("mental_rotation_accuracy", 0.0)) for row in map_rows)
        if map_rows
        else None
    )

    visualization_vz = (
        mean([value for value in [paper_folding_accuracy, map_placement] if value is not None])
        if paper_folding_accuracy is not None or map_placement is not None
        else None
    )
    spatial_relations_sr = (
        mean([value for value in [mental_rotation_accuracy, map_rotation] if value is not None])
        if mental_rotation_accuracy is not None or map_rotation is not None
        else None
    )
    visual_closure_cs = map_piece_selection
    flexibility_of_closure_cf = (
        mean([value for value in [hidden_figures_accuracy, 100.0 - distractor_selection_rate] if value is not None])
        if hidden_figures_accuracy is not None
        else None
    )
    spatial_scanning_ss = (
        mean([efficiency_score, strategy_error_control, map_placement])
        if map_placement is not None
        else mean([efficiency_score, strategy_error_control])
    )

    expected_scored_count = sum(
        1 for records in bank.values() for record in records if not record.safe["practice"]
    )
    completion_quality = min(1.0, total / max(expected_scored_count, 1))

    events = list(db.scalars(select(GvEvent).where(GvEvent.session_id == session.session_id)).all())
    seen_event_types = {event.event_type for event in events}
    core_event_types = {
        "session_started",
        "instructions_viewed",
        "practice_completed",
        "item_presented",
        "answer_submitted",
        "item_completed",
        "subtest_completed",
        "assessment_finished",
    }
    event_completeness = len(seen_event_types & core_event_types) / len(core_event_types)
    response_consistency = max(0.0, 1.0 - abs(overall_accuracy - first_attempt_accuracy) / 100.0)
    randomness_index = min(1.0, distractor_selection_rate / 100.0 + correction_count / max(total * 6, 1))
    difficulty_coverage = len({safe_by_id[row.item_id]["difficulty_level"] for row in answers if row.item_id in safe_by_id}) / 5.0
    metadata = session.session_metadata or {}
    received_events = int(metadata.get("received_event_count", 0))
    duplicate_events = int(metadata.get("duplicate_event_count", 0))
    rejected_events = int(metadata.get("rejected_event_count", 0))
    duplicate_rate = duplicate_events / max(received_events, 1)
    technical_stability = clamp(100.0 - duplicate_rate * 100.0 - rejected_events * 5.0) / 100.0
    missing_answer_rate = max(0.0, 1.0 - completion_quality)
    confidence_score = clamp(
        35.0 * completion_quality
        + 20.0 * event_completeness
        + 15.0 * response_consistency
        + 10.0 * (1.0 - randomness_index)
        + 5.0 * difficulty_coverage
        + 15.0 * technical_stability
        - 20.0 * missing_answer_rate
    )

    return Metrics(
        raw_score=round(raw_score, 2),
        accuracy=round(overall_accuracy, 2),
        visualization_vz=rounded(visualization_vz),
        spatial_relations_sr=rounded(spatial_relations_sr),
        visual_closure_cs=rounded(visual_closure_cs),
        flexibility_of_closure_cf=rounded(flexibility_of_closure_cf),
        spatial_scanning_ss=rounded(spatial_scanning_ss),
        visual_memory_mv=None,
        mental_rotation_accuracy=rounded(mental_rotation_accuracy),
        paper_folding_accuracy=rounded(paper_folding_accuracy),
        hidden_figures_accuracy=rounded(hidden_figures_accuracy),
        mystery_map_accuracy=rounded(mystery_map_accuracy),
        first_attempt_accuracy=round(first_attempt_accuracy, 2),
        correction_count=correction_count,
        average_response_time=round(average_response_time, 3),
        distractor_selection_rate=round(distractor_selection_rate, 2),
        rotation_attempts_total=rotation_attempts_total,
        mirror_confusion_rate=rounded(mirror_confusion_rate),
        strategy_error_control=round(strategy_error_control, 2),
        efficiency_score=round(efficiency_score, 2),
        confidence_score=round(confidence_score, 2),
    )
