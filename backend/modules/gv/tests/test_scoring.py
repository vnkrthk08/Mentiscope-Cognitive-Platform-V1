from __future__ import annotations

from backend.modules.gv.item_service import InvalidResponseError, evaluate_response
from backend.modules.gv.item_bank.items import build_item_bank


def test_mystery_map_partial_scoring_and_rotation_validation():
    session_id = "SCORE_TEST_SESSION"
    bank = build_item_bank(session_id, 2)
    record = next(item for item in bank["mystery_map"] if not item.safe["practice"])
    solution = record.answer_key["solution"]
    placements = {piece: dict(value) for piece, value in solution.items()}
    first_piece = next(iter(placements))
    placements[first_piece]["rotation"] = 90
    correct, distractor, detail = evaluate_response(
        session_id=session_id,
        difficulty=2,
        item_id=record.safe["item_id"],
        response={"placements": placements},
    )
    assert correct is False
    assert distractor is None
    assert detail["spatial_placement_accuracy"] == 100.0
    assert detail["mental_rotation_accuracy"] < 100.0


def test_invalid_option_is_rejected():
    session_id = "OPTION_TEST_SESSION"
    bank = build_item_bank(session_id, 2)
    item = next(item for item in bank["mental_rotation"] if not item.safe["practice"])
    try:
        evaluate_response(
            session_id=session_id,
            difficulty=2,
            item_id=item.safe["item_id"],
            response={"selected_option_id": "NOT_AN_OPTION"},
        )
    except InvalidResponseError:
        pass
    else:
        raise AssertionError("Invalid option was not rejected")
