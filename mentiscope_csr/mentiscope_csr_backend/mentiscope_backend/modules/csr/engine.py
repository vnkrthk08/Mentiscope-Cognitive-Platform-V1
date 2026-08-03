"""Pure task engine for Classroom Scenario Recall (CSR) — Working Memory (Gsm).

Ported from the standalone HTML/JS prototype's ITEM_BANK + trial-selection logic.
Kept framework-free (no FastAPI/SQLAlchemy imports) so it can be unit tested in isolation,
mirroring the Processing Speed module's perceptual_speed.py convention.
"""
from __future__ import annotations

from random import randint

# ---------------------------------------------------------------------------
# Item bank (content ported 1:1 from csr_prototype.html ITEM_BANK)
# ---------------------------------------------------------------------------

AUDITORY_ITEMS = [
    {
        "id": "AUD-01",
        "difficulty": 1,
        "chunks": ["Take the beaker", "add 20ml of water", "heat to 60 degrees", "stir for one minute", "record the color"],
        "question": "What was the third step?",
        "answer": "heat to 60 degrees",
        "options": ["heat to 60 degrees", "add 20ml of water", "record the color", "stir for one minute"],
    },
    {
        "id": "AUD-02",
        "difficulty": 1,
        "chunks": ["Open the notebook", "write today's date", "underline the title", "list three hypotheses", "close the cover"],
        "question": "What was the second step?",
        "answer": "write today's date",
        "options": ["write today's date", "underline the title", "list three hypotheses", "close the cover"],
    },
    {
        "id": "AUD-03",
        "difficulty": 2,
        "chunks": ["Place the slide on the stage", "adjust the coarse focus", "switch to high power", "refine the fine focus", "sketch what you observe", "label the diagram"],
        "question": "What came right before switching to high power?",
        "answer": "adjust the coarse focus",
        "options": ["adjust the coarse focus", "place the slide on the stage", "sketch what you observe", "label the diagram"],
    },
    {
        "id": "AUD-04",
        "difficulty": 2,
        "chunks": ["Measure 5 grams of salt", "dissolve it in 100ml water", "filter the mixture", "heat the filtrate gently", "observe crystal formation", "weigh the dried crystals"],
        "question": "What was the fourth step?",
        "answer": "heat the filtrate gently",
        "options": ["heat the filtrate gently", "filter the mixture", "observe crystal formation", "weigh the dried crystals"],
    },
]

VISUAL_ITEMS = [
    {"id": "VIS-01", "difficulty": 1, "grid_size": 4, "cells": [1, 6, 11, 13]},
    {"id": "VIS-02", "difficulty": 1, "grid_size": 4, "cells": [0, 5, 10, 15]},
    {"id": "VIS-03", "difficulty": 2, "grid_size": 5, "cells": [2, 7, 12, 16, 21]},
    {"id": "VIS-04", "difficulty": 2, "grid_size": 5, "cells": [0, 6, 12, 18, 24]},
]

DISTRACTOR_ITEMS = [
    {"id": "DIS-01", "prompt": "7 + 5 = ?", "answer": "12", "options": ["11", "12", "13", "10"]},
    {"id": "DIS-02", "prompt": "Is 'triangle' a shape?", "answer": "yes", "options": ["yes", "no"]},
    {"id": "DIS-03", "prompt": "9 - 4 = ?", "answer": "5", "options": ["4", "5", "6", "3"]},
    {"id": "DIS-04", "prompt": "Is 'Tuesday' a color?", "answer": "no", "options": ["yes", "no"]},
    {"id": "DIS-05", "prompt": "6 + 6 = ?", "answer": "12", "options": ["12", "11", "13", "14"]},
    {"id": "DIS-06", "prompt": "Is 'oxygen' a gas?", "answer": "yes", "options": ["yes", "no"]},
]

SEQUENTIAL_ITEMS = [
    {
        "id": "SEQ-01",
        "difficulty": 1,
        "initial": ["mix", "pour", "heat", "cool"],
        "update": {"remove_index": 1, "insert": "filter"},
        "question": "Put the final steps in order after the update.",
    },
    {
        "id": "SEQ-02",
        "difficulty": 2,
        "initial": ["measure", "record", "calculate", "graph", "conclude"],
        "update": {"remove_index": 2, "insert": "verify"},
        "question": "Put the final steps in order after the update.",
    },
]

# Fixed running order for the MVP session (mirrors the prototype's moduleOrder)
MODULE_ORDER = ["auditory", "visual", "distractor", "sequential"]
ITEMS_PER_MODULE = {"auditory": 2, "visual": 2, "distractor": 4, "sequential": len(SEQUENTIAL_ITEMS)}


def expected_sequence_order(item: dict) -> list[str]:
    expected = list(item["initial"])
    expected[item["update"]["remove_index"]] = item["update"]["insert"]
    return expected


def total_trials() -> int:
    return sum(ITEMS_PER_MODULE.values())


def trial_for_position(position: int) -> tuple[str, dict, int]:
    """Given a 0-indexed overall trial position, return (task_id, item, item_index_within_task)."""
    cursor = position
    for task in MODULE_ORDER:
        count = ITEMS_PER_MODULE[task]
        if cursor < count:
            bank = {
                "auditory": AUDITORY_ITEMS,
                "visual": VISUAL_ITEMS,
                "distractor": DISTRACTOR_ITEMS,
                "sequential": SEQUENTIAL_ITEMS,
            }[task]
            item = bank[cursor % len(bank)]
            return task, item, cursor
        cursor -= count
    raise IndexError("position beyond total trial count")


def _sequential_distractor_orders(item: dict) -> list[str]:
    """Generate plausible wrong final-orderings for the sequential-recall task,
    so it can be rendered as a standard multiple-choice question by the shared
    platform runner (which has no free-text/drag-reorder input widget)."""
    expected = expected_sequence_order(item)
    candidates: list[list[str]] = []

    # 1. The pre-update order (forgetting the update happened at all).
    candidates.append(list(item["initial"]))

    # 2. Update applied, but appended at the end instead of in place.
    removed_value = item["initial"][item["update"]["remove_index"]]
    without = [s for s in item["initial"] if s != removed_value]
    candidates.append(without + [item["update"]["insert"]])

    # 3. Correct set of steps, but with the first two swapped.
    swapped = list(expected)
    if len(swapped) >= 2:
        swapped[0], swapped[1] = swapped[1], swapped[0]
    candidates.append(swapped)

    # De-duplicate against each other and against the correct answer, then take 3.
    seen = {tuple(expected)}
    distractors: list[str] = []
    for c in candidates:
        key = tuple(c)
        if key not in seen:
            seen.add(key)
            distractors.append(",".join(c))
        if len(distractors) == 3:
            break
    return distractors


def build_question_payload(task: str, item: dict, question_id: str) -> dict:
    """Translate a raw item into the platform's shared Question schema.

    type mapping:
      auditory   -> memory-span (chunks shown as a sequence, answered as multiple choice)
      visual     -> grid-pattern
      distractor -> choice
      sequential -> choice (reorder submitted as a comma-joined string, validated server-side)
    """
    if task == "auditory":
        return {
            "id": question_id,
            "text": item["question"],
            "story": "Classroom Scenario Recall — Auditory Recall: chunks are presented in sequence; hold them in mind.",
            "sequence": item["chunks"],
            "options": item["options"],
            "type": "memory-span",
            "difficulty_level": item["difficulty"],
        }
    if task == "visual":
        return {
            "id": question_id,
            "text": "Which cells were highlighted?",
            "story": "Classroom Scenario Recall — Visual Grid Memory: memorize the highlighted cells, then reselect them.",
            "gridSize": item["grid_size"],
            "activeGridCells": item["cells"],
            "type": "grid-pattern",
            "difficulty_level": item["difficulty"],
        }
    if task == "distractor":
        return {
            "id": question_id,
            "text": item["prompt"],
            "story": "Classroom Scenario Recall — Distractor Challenge: an interposed task that separates encoding from retrieval.",
            "options": item["options"],
            "type": "choice",
            "difficulty_level": 1,
        }
    if task == "sequential":
        expected = ",".join(expected_sequence_order(item))
        distractors = _sequential_distractor_orders(item)
        options = [expected] + distractors
        # Deterministic shuffle keyed on the item id so re-fetching the same
        # trial (e.g. on a client retry) yields a stable option order.
        seed = sum(ord(c) for c in item["id"])
        rotated = options[seed % len(options):] + options[:seed % len(options)]
        return {
            "id": question_id,
            "text": item["question"],
            "story": "Classroom Scenario Recall — Sequential Recall: the instruction sequence is updated mid-task; select the corrected final order.",
            "options": rotated,
            "type": "choice",
            "difficulty_level": item["difficulty"],
        }
    raise ValueError(f"unknown task {task}")


def check_answer(task: str, item: dict, answer: str) -> tuple[bool, str | None]:
    """Return (correct, error_type)."""
    if task == "auditory":
        correct = answer == item["answer"]
        return correct, None if correct else "recall_error"
    if task == "visual":
        try:
            selected = {int(x) for x in answer.split(",") if x.strip() != ""}
        except ValueError:
            selected = set()
        correct_set = set(item["cells"])
        correct = selected == correct_set
        return correct, None if correct else "position_error"
    if task == "distractor":
        correct = answer == item["answer"]
        return correct, None if correct else "interference_error"
    if task == "sequential":
        expected = expected_sequence_order(item)
        submitted = [s.strip() for s in answer.split(",") if s.strip() != ""]
        correct = submitted == expected
        return correct, None if correct else "sequence_error"
    raise ValueError(f"unknown task {task}")


def difficulty_for(item: dict, task: str) -> int:
    if task in ("auditory", "visual", "sequential"):
        return item["difficulty"]
    return 1


def random_jitter_ms() -> int:
    """Small helper retained for parity with other modules' adaptive-timing hooks (unused server-side timing)."""
    return randint(0, 0)
