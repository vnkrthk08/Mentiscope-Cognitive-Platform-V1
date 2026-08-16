"""Pure task engine ported from Vinay Kartheek Bathala's Processing Speed (Gs) module in PROJECT_FINAL_COPY."""
import random
from typing import Dict, Any

# Standard visual symbols and alphanumeric characters pool (Ambiguous glyphs excluded)
SYMBOLS = ["■", "▲", "◆", "★", "●", "✚", "✖", "♥", "⬢", "⧓"]
ALPHANUMERIC_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_trial(trial_number: int, difficulty_level: int) -> dict:
    """
    Generates a row of 6 items (5 unique items + 1 duplicated target item)
    based on the module stage (Trials 1-5: Symbol Matching, 6-10: Alphanumeric, 11-15: Timed, 16-20: Adaptive).
    """
    stage = min(4, ((trial_number - 1) // 5) + 1)
    
    if stage == 1:
        # Module 1: Symbol Matching (len 2-3)
        str_len = 2 if difficulty_level <= 2 else 3
        pool = SYMBOLS
    elif stage == 2:
        # Module 2: Alphanumeric Comparison (len 3-4)
        str_len = 3 if difficulty_level <= 2 else 4
        pool = list(ALPHANUMERIC_CHARS)
    elif stage == 3:
        # Module 3: Timed Challenge (len 4)
        str_len = 4
        pool = list(ALPHANUMERIC_CHARS)
    else:
        # Module 4: Adaptive difficulty (Tiers 1-9)
        if difficulty_level <= 3:
            str_len = 2
        elif difficulty_level <= 6:
            str_len = 3
        else:
            str_len = 4
        pool = list(ALPHANUMERIC_CHARS) if difficulty_level >= 4 else SYMBOLS
        
    # Generate 5 unique items
    items = []
    attempts = 0
    while len(items) < 5 and attempts < 100:
        candidate = "".join(random.choices(pool, k=str_len))
        if candidate not in items:
            items.append(candidate)
        attempts += 1
        
    # Pick 1 item to duplicate as the target
    target = random.choice(items) if items else "▲▲"
    items.append(target)
    
    # Shuffle row items
    random.shuffle(items)
    
    module_names = {
        1: "Symbol Matching",
        2: "Alphanumeric Comparison",
        3: "Timed Complexity Challenge",
        4: "Adaptive Difficulty Engine"
    }
    
    return {
        "id": f"processing-speed-{trial_number}",
        "text": f"Select the string that appears twice in the row below ({module_names[stage]}).",
        "story": f"Processing Speed ({module_names[stage]}): Scan the 6 character strings and identify the duplicate pair as quickly and accurately as possible.",
        "options": items,
        "correct_answer": target,
        "difficulty_level": difficulty_level,
        "stage": stage,
    }

