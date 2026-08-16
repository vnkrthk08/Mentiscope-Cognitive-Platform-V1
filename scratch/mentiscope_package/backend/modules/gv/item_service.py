from __future__ import annotations

from typing import Any

from backend.modules.gv.item_bank.items import ItemRecord, get_item_and_key, safe_sequence


class ItemNotFoundError(ValueError):
    pass


class InvalidResponseError(ValueError):
    pass


def get_safe_sequence(session_id: str, difficulty: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return safe_sequence(session_id, difficulty)


def evaluate_response(
    *, session_id: str, difficulty: int, item_id: str, response: dict[str, Any]
) -> tuple[bool, str | None, dict[str, Any]]:
    record: ItemRecord | None = get_item_and_key(session_id, difficulty, item_id)
    if record is None:
        raise ItemNotFoundError(f"Unknown Gv item: {item_id}")

    answer_key = record.answer_key
    response_type = answer_key["response_type"]
    if response_type == "single_choice":
        selected = response.get("selected_option_id")
        valid_ids = {option["option_id"] for option in record.safe["options"]}
        if not isinstance(selected, str) or selected not in valid_ids:
            raise InvalidResponseError("selected_option_id is missing or invalid")
        correct = selected == answer_key["correct_option_id"]
        distractor_type = answer_key["distractor_types"].get(selected)
        return correct, distractor_type, {
            "accuracy": 100.0 if correct else 0.0,
            "first_attempt_accuracy": 100.0 if correct else 0.0,
        }

    if response_type == "map_placement":
        placements = response.get("placements")
        if not isinstance(placements, dict):
            raise InvalidResponseError("placements must be an object keyed by piece_id")
        solution: dict[str, dict[str, int]] = answer_key["solution"]
        if set(placements) != set(solution):
            raise InvalidResponseError("placements must include every piece exactly once")

        slots_seen: set[int] = set()
        correct_slots = 0
        correct_rotations = 0
        for piece_id, expected in solution.items():
            submitted = placements.get(piece_id)
            if not isinstance(submitted, dict):
                raise InvalidResponseError(f"Invalid placement for {piece_id}")
            slot_index = submitted.get("slot_index")
            rotation = submitted.get("rotation", 0)
            if not isinstance(slot_index, int) or not isinstance(rotation, int):
                raise InvalidResponseError("slot_index and rotation must be integers")
            if rotation % 90 != 0:
                raise InvalidResponseError("rotation must use 90-degree increments")
            if slot_index in slots_seen:
                raise InvalidResponseError("Each slot can contain only one piece")
            slots_seen.add(slot_index)
            if slot_index == expected["slot_index"]:
                correct_slots += 1
            if rotation % 360 == expected["rotation"]:
                correct_rotations += 1

        total = max(len(solution), 1)
        placement_accuracy = correct_slots / total * 100.0
        rotation_accuracy = correct_rotations / total * 100.0
        piece_selection_accuracy = placement_accuracy
        correct = correct_slots == total and correct_rotations == total
        return correct, None, {
            "piece_count": total,
            "correct_slots": correct_slots,
            "correct_rotations": correct_rotations,
            "piece_selection_accuracy": piece_selection_accuracy,
            "spatial_placement_accuracy": placement_accuracy,
            "mental_rotation_accuracy": rotation_accuracy,
            "accuracy": (placement_accuracy + rotation_accuracy) / 2.0,
        }

    raise InvalidResponseError(f"Unsupported response type: {response_type}")
