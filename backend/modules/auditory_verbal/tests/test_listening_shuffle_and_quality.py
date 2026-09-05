import pytest
import json
import os

def test_grounded_scenarios_balanced_answer_distribution():
    """Verify that canonical correct option indices across 50 grounded scenarios are balanced across 0, 1, 2, 3."""
    grounded_path = os.path.join(os.path.dirname(__file__), "..", "scenarios_50_fully_grounded.json")
    with open(grounded_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 50, f"Expected 50 scenarios, found {len(data)}"

    counts = {0: 0, 1: 0, 2: 0, 3: 0}
    total_questions = 0

    for sc_id, questions in data.items():
        assert len(questions) == 4, f"Scenario {sc_id} must have exactly 4 listening questions"
        for q in questions:
            total_questions += 1
            c_idx = q["correct_option_index"]
            assert c_idx in counts, f"Invalid correct_option_index {c_idx} in {sc_id}"
            counts[c_idx] += 1
            assert len(q["options"]) == 4, f"Question {q['question_id']} must have exactly 4 options"

    assert total_questions == 200
    # Every option position (0, 1, 2, 3) should have exactly 50 (25%) occurrences
    for idx, count in counts.items():
        assert count == 50, f"Option index {idx} has count {count}, expected 50"


def test_option_length_balance_psychometrics():
    """Verify that correct answers are not disproportionately longer than distractors across questions."""
    grounded_path = os.path.join(os.path.dirname(__file__), "..", "scenarios_50_fully_grounded.json")
    with open(grounded_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    disproportionate_count = 0
    total_questions = 0

    for sc_id, questions in data.items():
        for q in questions:
            total_questions += 1
            options = q["options"]
            c_idx = q["correct_option_index"]
            correct_len = len(options[c_idx])
            distractor_lens = [len(opt) for i, opt in enumerate(options) if i != c_idx]
            avg_distractor_len = sum(distractor_lens) / len(distractor_lens)

            # Check if correct answer is > 2.5x the average distractor length
            if avg_distractor_len > 0 and correct_len > avg_distractor_len * 2.5 and (correct_len - avg_distractor_len) > 30:
                disproportionate_count += 1

    # In our balanced dataset, 0 questions should have disproportionate length cues
    assert disproportionate_count == 0, f"Found {disproportionate_count} questions with disproportionate length cues"


def test_runtime_fisher_yates_permutation_logic():
    """Verify Fisher-Yates permutation properties for option shuffling."""
    import random
    
    canonical_options = ["Option Alpha", "Option Beta", "Option Gamma", "Option Delta"]
    canonical_correct = 2 # Gamma is correct

    # Test permutation mapping
    indices = list(range(len(canonical_options)))
    random.seed(42)
    random.shuffle(indices)

    shuffled_options = [canonical_options[i] for i in indices]
    displayed_correct = indices.index(canonical_correct)

    # When candidate picks displayed_correct, it must map back to canonical_correct
    resolved_canonical = indices[displayed_correct]
    assert resolved_canonical == canonical_correct
    assert shuffled_options[displayed_correct] == "Option Gamma"
