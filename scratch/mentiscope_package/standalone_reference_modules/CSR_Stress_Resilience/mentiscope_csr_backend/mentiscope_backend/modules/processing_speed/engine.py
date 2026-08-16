"""Pure task engine ported from the Processing Speed module."""
from random import choice, randint, sample, shuffle

SYMBOLS = "▲▼◆●■★✦◀▶"
LETTERS = "ABCDEFGHJKLMNPQRSTUVWXY"
DIGITS = "23456789"
MODULE_GENERATORS = {1: ("symbol",), 2: ("letters", "digits", "mixed"), 3: ("letters", "digits", "mixed"), 4: ("letters", "digits", "mixed")}


def _random_string(kind: str) -> str:
    if kind == "symbol":
        return "".join(choice(SYMBOLS) for _ in range(choice((2, 3))))
    if kind == "letters":
        return "".join(choice(LETTERS) for _ in range(4))
    if kind == "digits":
        return "".join(choice(DIGITS) for _ in range(4))
    return "".join(sample(LETTERS, 2) + sample(DIGITS, 2))


def _mutate(value: str) -> str:
    index = randint(0, len(value) - 1)
    original = value[index]
    pool = DIGITS if original in DIGITS else SYMBOLS if original in SYMBOLS else LETTERS
    replacement = choice(pool)
    while replacement == original:
        replacement = choice(pool)
    return value[:index] + replacement + value[index + 1 :]


def generate_trial(trial_number: int, difficulty_level: int) -> dict:
    stage = min(4, ((trial_number - 1) // 5) + 1)
    target = _random_string(choice(MODULE_GENERATORS[stage]))
    values = [target]
    use_mutations = stage == 3 or (stage == 4 and difficulty_level >= 2)
    while len(values) < 5:
        candidate = _mutate(target) if use_mutations else _random_string(choice(MODULE_GENERATORS[stage]))
        if candidate not in values:
            values.append(candidate)
    answer = choice(values)
    values.append(answer)
    shuffle(values)
    return {
        "id": f"processing-speed-{trial_number}",
        "text": "Select the string that appears twice.",
        "story": "Perceptual Speed: scan the six strings and identify the exact duplicate as quickly and accurately as possible.",
        "options": values,
        "correct_answer": answer,
        "difficulty_level": difficulty_level,
        "stage": stage,
    }
