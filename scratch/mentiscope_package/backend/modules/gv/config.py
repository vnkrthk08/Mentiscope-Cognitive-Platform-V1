from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class GvModuleConfig:
    module_key: str = "gv"
    module_id: str = "GV_VISUAL_PROCESSING_BATTERY"
    module_name: str = "Visual Processing Battery"
    construct: str = "CHC_Gv_Visual_Processing"
    author: str = "ELURU VEDAKSHARI"
    version: str = "1.0.0"
    api_base_url: str = "/api/modules/gv"
    min_difficulty: int = 1
    max_difficulty: int = 5
    session_expiry_hours: int = 24


MODULE_CONFIG: Final = GvModuleConfig()

SUBTEST_ORDER: Final[tuple[str, ...]] = (
    "mental_rotation",
    "paper_folding",
    "hidden_figures",
    "mystery_map",
)

SUBTEST_WEIGHTS: Final[dict[str, float]] = {
    "mental_rotation": 0.25,
    "paper_folding": 0.25,
    "hidden_figures": 0.20,
    "mystery_map": 0.30,
}

REQUIRED_EVENT_TYPES: Final[set[str]] = {
    "session_started",
    "instructions_viewed",
    "practice_started",
    "practice_answered",
    "practice_completed",
    "subtest_started",
    "item_presented",
    "option_selected",
    "piece_selected",
    "distractor_selected",
    "piece_rotated",
    "piece_placed",
    "answer_submitted",
    "item_completed",
    "navigation_attempted",
    "subtest_completed",
    "assessment_finished",
    "result_viewed",
    "session_abandoned",
}
