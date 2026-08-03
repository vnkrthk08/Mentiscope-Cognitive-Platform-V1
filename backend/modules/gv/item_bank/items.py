from __future__ import annotations

import copy
import hashlib
import random
from dataclasses import dataclass
from typing import Any

from backend.modules.gv.config import SUBTEST_ORDER


@dataclass(frozen=True)
class ItemRecord:
    safe: dict[str, Any]
    answer_key: dict[str, Any]


def _shape(cells: list[list[int]], notch: list[int], color: str) -> dict[str, Any]:
    return {"cells": cells, "notch": notch, "color": color}


def _option(option_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"option_id": option_id, "payload": payload}


def _single_choice_item(
    *,
    item_id: str,
    subtest_id: str,
    subtest_name: str,
    prompt: str,
    difficulty: int,
    primary_ability: str,
    secondary_ability: str | None,
    expected_time: int,
    stimulus: dict[str, Any],
    options: list[dict[str, Any]],
    correct_option_id: str,
    distractor_types: dict[str, str],
    practice: bool = False,
) -> ItemRecord:
    safe = {
        "item_id": item_id,
        "subtest_id": subtest_id,
        "subtest_name": subtest_name,
        "prompt": prompt,
        "difficulty_level": difficulty,
        "primary_ability": primary_ability,
        "secondary_ability": secondary_ability,
        "expected_time_seconds": expected_time,
        "response_type": "single_choice",
        "practice": practice,
        "stimulus": stimulus,
        "options": options,
    }
    return ItemRecord(
        safe=safe,
        answer_key={
            "response_type": "single_choice",
            "correct_option_id": correct_option_id,
            "distractor_types": distractor_types,
        },
    )


def _rotation_items() -> list[ItemRecord]:
    shapes = {
        "f": _shape([[0, 0], [1, 0], [2, 0], [0, 1], [0, 2], [1, 2]], [2, 0], "#0d9488"),
        "l": _shape([[0, 0], [0, 1], [0, 2], [0, 3], [1, 3], [2, 3]], [2, 3], "#b45309"),
        "z": _shape([[0, 0], [1, 0], [1, 1], [2, 1], [2, 2], [3, 2]], [0, 0], "#4338ca"),
        "s": _shape([[1, 0], [2, 0], [3, 0], [0, 1], [1, 1], [0, 2]], [3, 0], "#0369a1"),
    }

    specs = [
        ("GV_MR_PRACTICE", "f", 0, [("MRP_A", 90, False), ("MRP_B", 180, True), ("MRP_C", 270, True)], "MRP_A", True, 1),
        ("GV_MR_001", "l", 0, [("MR1_A", 90, True), ("MR1_B", 180, False), ("MR1_C", 270, True), ("MR1_D", 0, True)], "MR1_B", False, 2),
        ("GV_MR_002", "z", 0, [("MR2_A", 180, True), ("MR2_B", 270, True), ("MR2_C", 90, False), ("MR2_D", 0, True)], "MR2_C", False, 3),
        ("GV_MR_003", "s", 90, [("MR3_A", 0, True), ("MR3_B", 270, False), ("MR3_C", 180, True), ("MR3_D", 90, True)], "MR3_B", False, 3),
    ]
    records: list[ItemRecord] = []
    for item_id, shape_name, target_rotation, opts, correct_id, practice, difficulty in specs:
        options = [
            _option(oid, {"shape": shapes[shape_name], "rotation": rot, "mirror": mirror})
            for oid, rot, mirror in opts
        ]
        distractors = {
            oid: ("correct" if oid == correct_id else "mirrored_distractor")
            for oid, _, _ in opts
        }
        records.append(
            _single_choice_item(
                item_id=item_id,
                subtest_id="mental_rotation",
                subtest_name="Mental Rotation",
                prompt=(
                    "Which figure is the same shape, only rotated? Mirror images do not count."
                    if practice
                    else "Select the rotated copy of the figure on the left."
                ),
                difficulty=difficulty,
                primary_ability="SR",
                secondary_ability="Vz",
                expected_time=30,
                stimulus={"shape": shapes[shape_name], "rotation": target_rotation, "mirror": False},
                options=options,
                correct_option_id=correct_id,
                distractor_types=distractors,
                practice=practice,
            )
        )
    return records


def _folding_items() -> list[ItemRecord]:
    specs: list[dict[str, Any]] = [
        {
            "item_id": "GV_PF_PRACTICE",
            "practice": True,
            "difficulty": 1,
            "folds": [{"axis": "vertical", "direction": "right"}],
            "punched": [[0, 1]],
            "options": {
                "PFP_A": [[0, 1], [3, 1]],
                "PFP_B": [[0, 1]],
                "PFP_C": [[0, 2], [3, 2]],
            },
            "correct": "PFP_A",
        },
        {
            "item_id": "GV_PF_001",
            "difficulty": 2,
            "folds": [{"axis": "horizontal", "direction": "down"}],
            "punched": [[1, 0]],
            "options": {
                "PF1_A": [[1, 0], [2, 3]],
                "PF1_B": [[1, 3]],
                "PF1_C": [[1, 0], [1, 3]],
                "PF1_D": [[1, 0], [1, 3], [2, 0]],
            },
            "correct": "PF1_C",
        },
        {
            "item_id": "GV_PF_002",
            "difficulty": 3,
            "folds": [
                {"axis": "vertical", "direction": "right"},
                {"axis": "horizontal", "direction": "down"},
            ],
            "punched": [[0, 0]],
            "options": {
                "PF2_A": [[0, 0], [3, 0]],
                "PF2_B": [[0, 0], [3, 0], [0, 3], [3, 3]],
                "PF2_C": [[0, 0], [0, 3]],
                "PF2_D": [[1, 1], [2, 1], [1, 2], [2, 2]],
            },
            "correct": "PF2_B",
        },
        {
            "item_id": "GV_PF_003",
            "difficulty": 3,
            "folds": [{"axis": "vertical", "direction": "right"}],
            "punched": [[1, 2]],
            "options": {
                "PF3_A": [[1, 2]],
                "PF3_B": [[0, 2], [3, 2]],
                "PF3_C": [[1, 2], [1, 1]],
                "PF3_D": [[1, 2], [2, 2]],
            },
            "correct": "PF3_D",
        },
    ]
    records: list[ItemRecord] = []
    for spec in specs:
        correct = spec["correct"]
        options = [_option(oid, {"holes": holes}) for oid, holes in spec["options"].items()]
        distractor_labels = ["missing_reflection", "wrong_axis", "extra_hole"]
        distractors: dict[str, str] = {}
        idx = 0
        for oid in spec["options"]:
            if oid == correct:
                distractors[oid] = "correct"
            else:
                distractors[oid] = distractor_labels[idx % len(distractor_labels)]
                idx += 1
        records.append(
            _single_choice_item(
                item_id=spec["item_id"],
                subtest_id="paper_folding",
                subtest_name="Paper Folding",
                prompt=(
                    "The paper is folded and punched. Choose the pattern after it is fully unfolded."
                    if spec.get("practice")
                    else "Choose the unfolded hole pattern."
                ),
                difficulty=spec["difficulty"],
                primary_ability="Vz",
                secondary_ability="SR",
                expected_time=40,
                stimulus={"folds": spec["folds"], "punched": spec["punched"], "grid_size": 4},
                options=options,
                correct_option_id=correct,
                distractor_types=distractors,
                practice=bool(spec.get("practice")),
            )
        )
    return records


def _hidden_figure_items() -> list[ItemRecord]:
    # Coordinates use a 0..100 viewBox. The target segment pattern is embedded
    # in one option while the remaining segments create visual interference.
    target_a = [[[10, 80], [40, 20]], [[40, 20], [70, 80]], [[25, 55], [55, 55]]]
    target_b = [[[15, 20], [15, 80]], [[15, 80], [70, 80]], [[40, 40], [70, 80]]]
    target_c = [[[20, 20], [80, 20]], [[50, 20], [50, 80]], [[20, 80], [80, 80]]]

    def complex_option(option_id: str, target: list[list[list[int]]], offset: int, embed: bool) -> dict[str, Any]:
        base = [
            [[5 + offset, 10], [95 - offset, 90]],
            [[5, 90 - offset], [95, 15 + offset]],
            [[10, 50], [90, 50]],
            [[50, 5], [50, 95]],
            [[20, 15], [80, 75]],
            [[20, 85], [80, 25]],
        ]
        if embed:
            base.extend(target)
        else:
            base.extend([[[12, 75], [38, 25]], [[38, 25], [76, 74]], [[24, 60], [62, 48]]])
        return _option(option_id, {"segments": base})

    specs = [
        ("GV_HF_PRACTICE", target_a, "HFP", "HFP_B", True, 1),
        ("GV_HF_001", target_b, "HF1", "HF1_D", False, 2),
        ("GV_HF_002", target_c, "HF2", "HF2_A", False, 3),
        ("GV_HF_003", target_a, "HF3", "HF3_C", False, 4),
    ]
    records: list[ItemRecord] = []
    for item_id, target, option_prefix, correct, practice, difficulty in specs:
        suffixes = ("_A", "_B", "_C") if practice else ("_A", "_B", "_C", "_D")
        option_ids = [option_prefix + suffix for suffix in suffixes]
        options = [complex_option(oid, target, i * 2, oid == correct) for i, oid in enumerate(option_ids)]
        distractors = {oid: ("correct" if oid == correct else "feature_similar") for oid in option_ids}
        records.append(
            _single_choice_item(
                item_id=item_id,
                subtest_id="hidden_figures",
                subtest_name="Hidden Figures",
                prompt=(
                    "Find the simple target shape inside one of the complex figures."
                    if practice
                    else "Which complex figure contains the target shape exactly?"
                ),
                difficulty=difficulty,
                primary_ability="CF",
                secondary_ability="SS",
                expected_time=45,
                stimulus={"target_segments": target},
                options=options,
                correct_option_id=correct,
                distractor_types=distractors,
                practice=practice,
            )
        )
    return records


CELL_TYPES = ("grass", "road", "water", "building", "park", "sand")
GLYPHS = (None, "tree", "building_small", "building_tall", "landmark", "water_wave")


def _paint_map(width: int, height: int, rng: random.Random) -> tuple[list[list[str]], list[list[str | None]]]:
    cells = [["grass" for _ in range(width)] for _ in range(height)]
    glyphs: list[list[str | None]] = [[None for _ in range(width)] for _ in range(height)]
    river_y = rng.randrange(1, max(2, height - 1))
    for x in range(width):
        cells[river_y][x] = "water"
        glyphs[river_y][x] = "water_wave" if x % 2 == 0 else None
    road_x = rng.randrange(1, max(2, width - 1))
    for y in range(height):
        if cells[y][road_x] != "water":
            cells[y][road_x] = "road"
    road_y = rng.randrange(0, height)
    for x in range(width):
        if cells[road_y][x] != "water":
            cells[road_y][x] = "road"
    if cells[road_y][road_x] == "road":
        glyphs[road_y][road_x] = "landmark"
    for _ in range(max(2, width * height // 8)):
        x, y = rng.randrange(width), rng.randrange(height)
        if cells[y][x] == "grass":
            cells[y][x] = rng.choice(["park", "building", "sand"])
            glyphs[y][x] = rng.choice(["tree", "building_small", "building_tall"])
    return cells, glyphs


def _mystery_map_item(
    *,
    item_id: str,
    seed: str,
    cols: int,
    rows: int,
    piece_size: int,
    difficulty: int,
    practice: bool,
) -> ItemRecord:
    rng = random.Random(int(hashlib.sha256(f"{seed}:{item_id}".encode()).hexdigest()[:16], 16))
    width, height = cols * piece_size, rows * piece_size
    cells, glyphs = _paint_map(width, height, rng)
    pieces: list[dict[str, Any]] = []
    solution: dict[str, dict[str, int]] = {}
    for row in range(rows):
        for col in range(cols):
            slot = row * cols + col
            piece_id = f"{item_id}_P{slot + 1}"
            piece_cells = [
                cells[row * piece_size + dy][col * piece_size : col * piece_size + piece_size]
                for dy in range(piece_size)
            ]
            piece_glyphs = [
                glyphs[row * piece_size + dy][col * piece_size : col * piece_size + piece_size]
                for dy in range(piece_size)
            ]
            rotation = rng.choice([0, 90, 180, 270]) if not practice else 0
            pieces.append(
                {
                    "piece_id": piece_id,
                    "cells": piece_cells,
                    "glyphs": piece_glyphs,
                    "initial_rotation": rotation,
                }
            )
            solution[piece_id] = {"slot_index": slot, "rotation": 0}
    rng.shuffle(pieces)
    safe = {
        "item_id": item_id,
        "subtest_id": "mystery_map",
        "subtest_name": "Mystery Map Builder",
        "prompt": "Study the map, then rebuild it by placing every tile in its original position.",
        "difficulty_level": difficulty,
        "primary_ability": "CS",
        "secondary_ability": "SR,Vz,CF,SS",
        "expected_time_seconds": 75 + 15 * difficulty,
        "response_type": "map_placement",
        "practice": practice,
        "stimulus": {
            "map": cells,
            "glyphs": glyphs,
            "cols": cols,
            "rows": rows,
            "piece_size": piece_size,
            "study_seconds": 8 if practice else max(5, 10 - difficulty),
            "pieces": pieces,
        },
        "options": [],
    }
    return ItemRecord(
        safe=safe,
        answer_key={"response_type": "map_placement", "solution": solution},
    )


def build_item_bank(session_id: str, difficulty: int) -> dict[str, list[ItemRecord]]:
    records = _rotation_items() + _folding_items() + _hidden_figure_items()
    records.extend(
        [
            _mystery_map_item(
                item_id="GV_MM_PRACTICE",
                seed=session_id,
                cols=2,
                rows=2,
                piece_size=2,
                difficulty=1,
                practice=True,
            ),
            _mystery_map_item(
                item_id="GV_MM_001",
                seed=session_id,
                cols=2,
                rows=2,
                piece_size=2,
                difficulty=max(1, min(difficulty, 2)),
                practice=False,
            ),
            _mystery_map_item(
                item_id="GV_MM_002",
                seed=session_id,
                cols=3,
                rows=2,
                piece_size=2,
                difficulty=max(2, min(difficulty + 1, 4)),
                practice=False,
            ),
            _mystery_map_item(
                item_id="GV_MM_003",
                seed=session_id,
                cols=3,
                rows=3,
                piece_size=2,
                difficulty=max(3, min(difficulty + 2, 5)),
                practice=False,
            ),
        ]
    )
    grouped: dict[str, list[ItemRecord]] = {subtest: [] for subtest in SUBTEST_ORDER}
    for record in records:
        grouped[record.safe["subtest_id"]].append(record)
    return grouped


def get_item_and_key(session_id: str, difficulty: int, item_id: str) -> ItemRecord | None:
    bank = build_item_bank(session_id, difficulty)
    for records in bank.values():
        for record in records:
            if record.safe["item_id"] == item_id:
                return record
    return None


def safe_sequence(session_id: str, difficulty: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    bank = build_item_bank(session_id, difficulty)
    practice: list[dict[str, Any]] = []
    scored: list[dict[str, Any]] = []
    for subtest in SUBTEST_ORDER:
        for record in bank[subtest]:
            target = practice if record.safe["practice"] else scored
            target.append(copy.deepcopy(record.safe))
    return practice, scored
