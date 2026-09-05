import logging
from typing import Any, Dict, List
from app.domain.exceptions.scenario_exceptions import ScenarioValidationError

logger = logging.getLogger(__name__)

FRAMEWORK_BLOCKLIST = [
    "working memory construct",
    "working memory ability",
    "attention construct",
    "attention ability",
    "reasoning construct",
    "reasoning ability",
    "listening comprehension construct",
    "cognitive construct",
    "psychometric",
    "evaluated by",
    "measures your",
    "target construct",
    "internal scoring",
    "assessment framework",
]

REQUIRED_CONSTRUCT_SET = {"WORKING MEMORY", "ATTENTION", "LISTENING COMPREHENSION", "REASONING"}
VALID_QUESTION_TYPES = {"RECALL", "INFERENCE", "DETAIL", "SEQUENCING", "COMPREHENSION"}


class ScenarioValidator:
    """Validates scenario raw dictionary definitions against structural, construct, timing, asset, and psychometric framework leakage rules."""

    def validate(self, raw_data: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        scenario_id = raw_data.get("id", raw_data.get("scenario_id", "UNKNOWN"))

        # 1. Required Top-Level Fields
        required_fields = ["id", "title", "narrative", "version", "audio_asset", "listening_module", "speaking_module"]
        for field in required_fields:
            if field not in raw_data or not raw_data[field]:
                errors.append(f"Missing required top-level field '{field}'.")

        # 2. Audio Asset Validation
        audio_asset = raw_data.get("audio_asset", {})
        if isinstance(audio_asset, dict):
            if "url" not in audio_asset or not audio_asset["url"]:
                errors.append("audio_asset.url is required.")
            if "duration_seconds" not in audio_asset or audio_asset["duration_seconds"] <= 0:
                errors.append("audio_asset.duration_seconds must be > 0.")
        else:
            errors.append("audio_asset must be a dictionary.")

        # 3. Listening Questions Validation
        listening_mod = raw_data.get("listening_module", {})
        questions = listening_mod.get("questions", []) if isinstance(listening_mod, dict) else []
        if not isinstance(questions, list) or len(questions) != 4:
            errors.append(f"Scenario must contain exactly 4 listening questions in listening_module.questions (found {len(questions) if isinstance(questions, list) else 0}).")
        
        narrative_text = str(raw_data.get("narrative", "") or raw_data.get("listening_narration", "")).lower()

        seen_constructs = set()
        for idx, q in enumerate(questions if isinstance(questions, list) else []):
            if not isinstance(q, dict):
                errors.append(f"Listening question at index {idx} is not a dictionary.")
                continue

            qid = q.get("id") or q.get("question_id", f"LQ_{idx+1}")
            prompt = str(q.get("prompt") or q.get("question_text") or "")
            options = q.get("options", [])
            target_construct = str(q.get("target_construct", "")).strip()

            if not prompt:
                errors.append(f"Question '{qid}' missing prompt text.")

            if len(options) < 2:
                errors.append(f"Question '{qid}' must contain at least 2 options.")

            correct_idx = q.get("correct_option_index")
            if correct_idx is None or not (0 <= correct_idx < len(options)):
                errors.append(f"Question '{qid}' correct_option_index {correct_idx} out of bounds.")

            # Rule 1: Construct Coverage & Duplicates
            norm_construct = target_construct.upper().replace("_", " ").replace("LISTEN COMPREHENSION", "LISTENING COMPREHENSION")
            if not norm_construct:
                errors.append(f"Question '{qid}' missing target_construct.")
            elif norm_construct in seen_constructs:
                errors.append(f"Duplicate target construct '{target_construct}' found in question '{qid}'. Each scenario's 4 listening questions must have unique constructs.")
            else:
                seen_constructs.add(norm_construct)

            # Rule 2: Required Metadata Fields
            required_meta = ["secondary_constructs", "question_type", "cognitive_objective", "difficulty", "expected_evidence", "weight"]
            for mf in required_meta:
                if mf not in q or q[mf] is None:
                    errors.append(f"Question '{qid}' missing required metadata field '{mf}'.")

            q_type = str(q.get("question_type", "")).upper()
            if q_type and q_type not in VALID_QUESTION_TYPES:
                errors.append(f"Question '{qid}' has invalid question_type '{q.get('question_type')}'. Must be one of: Recall, Inference, Detail, Sequencing, Comprehension.")

            # Rule 3: Distractor Rationale Coverage
            expected_ev = q.get("expected_evidence", {})
            if isinstance(expected_ev, dict):
                dist_rat = expected_ev.get("distractor_rationale", {})
                if not isinstance(dist_rat, dict) or len(dist_rat) == 0:
                    errors.append(f"Question '{qid}' expected_evidence.distractor_rationale must cover at least one incorrect option.")
            else:
                errors.append(f"Question '{qid}' expected_evidence must be a dictionary.")

            # Rule 4: Hard Reject on Framework Leakage & Construct Names (Blocklist)
            combined_text = (prompt + " " + " ".join([str(o) for o in options])).lower()
            for term in FRAMEWORK_BLOCKLIST:
                if term in combined_text:
                    errors.append(f"Hard Reject: Question '{qid}' or its options contain forbidden framework/construct term '{term}'.")

            # Rule 5: Soft-warn on Reasoning long verbatim substring
            if norm_construct == "REASONING" and prompt and narrative_text:
                clean_p = prompt.lower()
                for i in range(len(clean_p) - 24):
                    sub = clean_p[i:i+25]
                    if sub in narrative_text and not sub.isspace():
                        logger.warning(f"Scenario '{scenario_id}' question '{qid}' Reasoning prompt contains long verbatim substring from narrative: '{sub}'.")
                        break

            # Rule 6: Ethical/Conduct Distractor Soft Warning
            conduct_keywords = ["blame teammate", "blame others", "ignore responsibility", "cheat", "forge signature"]
            for ck in conduct_keywords:
                if any(ck in str(o).lower() for o in options):
                    logger.warning(f"Scenario '{scenario_id}' question '{qid}' option contains behavioral/ethical judgment distractor '{ck}'. Listening questions should focus on cognitive processing.")

            # Rule 7: Narrative Relevance & Entity Grounding Check
            combined_q_text = (prompt + " " + " ".join([str(o) for o in options])).lower()
            alien_terms = ["safety standards", "municipal inspectors", "commercial advertisement contracts", "off-site venue transfer"]
            for alien in alien_terms:
                if alien in combined_q_text and alien not in narrative_text and alien not in subcategory:
                    errors.append(f"Hard Reject: Question '{qid}' contains ungrounded cross-domain boilerplate term '{alien}' not present in narrative.")

        # Verify exact construct set
        if seen_constructs != REQUIRED_CONSTRUCT_SET:
            missing_c = REQUIRED_CONSTRUCT_SET - seen_constructs
            if missing_c:
                errors.append(f"Scenario listening questions must cover all 4 constructs: Working Memory, Attention, Listening Comprehension, Reasoning. Missing: {', '.join(missing_c)}.")

        # 4. Speaking Prompts Validation
        speaking_mod = raw_data.get("speaking_module", {})
        prompts = speaking_mod.get("prompts", []) if isinstance(speaking_mod, dict) else []
        if not prompts:
            errors.append("Scenario must contain at least one speaking prompt in speaking_module.prompts.")
        else:
            p_ids = set()
            for idx, p in enumerate(prompts):
                if not isinstance(p, dict):
                    errors.append(f"Speaking prompt at index {idx} is not a dictionary.")
                    continue
                pid = p.get("id")
                if not pid:
                    errors.append(f"Speaking prompt at index {idx} missing 'id'.")
                elif pid in p_ids:
                    errors.append(f"Duplicate speaking prompt ID detected: '{pid}'.")
                else:
                    p_ids.add(pid)

                if "title" not in p or not p["title"]:
                    errors.append(f"Prompt '{pid}' missing title.")
                if "instructions" not in p or not p["instructions"]:
                    errors.append(f"Prompt '{pid}' missing instructions.")
                if "target_constructs" not in p or not p["target_constructs"]:
                    errors.append(f"Prompt '{pid}' must target at least one construct in target_constructs.")

        if errors:
            raise ScenarioValidationError(scenario_id, errors)

        return errors
