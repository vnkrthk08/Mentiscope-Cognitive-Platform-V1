"""
Module 8.5: Dialogue Editor (AIIS v20.1 Architecture).
Maintains a registry of 40+ natural opening templates. Rewrites raw generated question text to compress wording,
strip robotic lead-in phrases ('Regarding your choice to...', 'You mentioned...'), and enforce template rotation.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class EditedDialogueResult:
    edited_question_text: str
    opening_template_used: str
    robotic_phrases_stripped: List[str]
    compression_ratio: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edited_question_text": self.edited_question_text,
            "opening_template_used": self.opening_template_used,
            "robotic_phrases_stripped": self.robotic_phrases_stripped,
            "compression_ratio": round(self.compression_ratio, 2),
        }


class DialogueEditor:
    """Module 8.5: Dialogue Editor with 40+ Opening Templates & Wording Compressor."""

    OPENING_TEMPLATES: List[str] = [
        "What led you to...",
        "Looking back...",
        "One thing caught my attention...",
        "Help me understand...",
        "Suppose circumstances shifted slightly...",
        "What was most on your mind when...",
        "If you were in that position again...",
        "Walk me through your thinking when...",
        "What specific risk were you aiming to avoid when...",
        "How did you evaluate the compromise when...",
        "If a teammate questioned your approach...",
        "What made safety your primary focus when...",
        "What key factor tipped your decision toward...",
        "Looking at the situation overall...",
        "What alternative paths crossed your mind when...",
        "How would you handle things if...",
        "When time started running out...",
        "What priority guided you as...",
        "Reflecting on the trade-offs...",
        "What potential hazard concerned you most when...",
        "If you had a few extra minutes...",
        "What led you to choose...",
        "Looking back at that moment...",
        "One key consideration here is...",
        "How did you weigh the options when...",
        "If another team member suggested...",
        "What outcome were you most focused on when...",
        "When facing that deadline...",
        "What assumption did you test before...",
        "Reflecting on your strategy...",
        "What potential risk stood out most when...",
        "If the constraints were different...",
        "What principal reason prompted you to...",
        "Looking at the trade-off between speed and safety...",
        "What led you to prioritize...",
        "When you decided to act...",
        "How did you address the uncertainty as...",
        "If circumstances required you to adapt...",
        "What key lesson did you draw from...",
        "When evaluating the available choices...",
        "What critical factor influenced you as...",
    ]

    CONNECTOR_TEMPLATES: List[str] = [
        "involving {details}",
        "regarding {details}",
        "concerning {details}",
        "with respect to {details}",
        "when you brought up {details}",
        "around {details}",
    ]

    ROBOTIC_PATTERNS: List[str] = [
        r"regarding your choice to ['\"`]?.*?\b",
        r"regarding your decision to ['\"`]?.*?\b",
        r"regarding your approach to ['\"`]?.*?\b",
        r"regarding your decision\b",
        r"regarding your approach\b",
        r"regarding your choice\b",
        r"regarding choice to\b",
        r"you noted that you would\b",
        r"earlier you mentioned your decision to ['\"`]?.*?\b",
        r"you said that you would\b",
        r"you mentioned your decision to\b",
        r"as you stated earlier that\b",
        r"when considering \w+ and \w+\b",
        r"in terms of your choice to\b",
        r"with respect to your decision to\b",
    ]

    @staticmethod
    def extract_details_from_text(text: str) -> List[Dict[str, str]]:
        """
        Extract 1-2 concrete details from text.
        Returns list of {"text": str, "type": "proper_noun"|"person_name"|"quantity_role"|"adj_noun"|"verb_obj"|"domain_concept"}.
        """
        COMMON_CAPS = {
            "I", "The", "A", "An", "This", "That", "We", "You", "He", "She",
            "It", "My", "Our", "Your", "They", "What", "How", "Why", "When",
            "Where", "If", "But", "And", "Or", "So", "Do", "Does", "Did",
            "Is", "Are", "Was", "Were", "Will", "Would", "Could", "Should",
            "Can", "May", "Might", "Shall", "Has", "Have", "Had",
            "I'm", "I've", "I'd", "I'll", "You're", "You've", "You'd", "You'll",
            "We're", "We've", "We'd", "We'll", "They're", "They've", "They'd",
            "He's", "She's", "It's", "Sir", "Ma'am", "Madam", "Mr", "Mrs", "Ms", "Dr",
            "Just", "Well", "Actually", "Sure", "Okay"
        }
        PERSON_NAMES = {"Arjun", "Arora", "Dr. Arora", "Sen", "Mrs. Sen", "Meera", "George", "Uncle George"}
        ABSTRACT_META = {"choice", "decision", "rationale", "reason", "approach", "priority", "plan", "action", "option", "thinking", "response"}
        VERB_PREDICATES = {
            "reduces", "reduced", "reducing", "increases", "increased", "increasing",
            "helps", "helped", "causes", "caused", "leads", "led", "allows", "allowed",
            "prevents", "prevented", "requires", "required", "ensures", "ensured",
            "guarantees", "guaranteed", "limits", "limited", "provides", "provided",
            "is", "was", "are", "were", "has", "had", "have", "will", "would", "could", "should", "may", "might", "can"
        }
        TRAILING_FUNCTION_WORDS = {
            "when", "because", "but", "so", "and", "if", "while", "though", "although",
            "since", "until", "unless", "where", "how", "what", "why", "that", "than",
            "then", "as", "or", "nor", "for", "to", "with", "a", "an", "the", "our",
            "their", "your", "my", "his", "her", "its", "some", "any", "all", "bit",
            "lot", "little", "much", "very", "too", "also", "just", "actually", "really",
            "already", "soon", "now", "here", "there", "well", "which", "who", "whom", "whose"
        }

        PRONOUN_OBJECTS = {"him", "her", "them", "it", "this", "that", "me", "us", "you", "himself", "herself", "themselves", "itself", "right", "now", "here", "there"}
        details: List[Dict[str, str]] = []
        lower = text.lower()
        words = text.split()

        def is_dup(cand_text: str) -> bool:
            c_norm = re.sub(r'[^a-z0-9\s]', '', cand_text.lower()).strip()
            c_words = set(c_norm.split()) - {"the", "a", "an", "our", "to", "with", "for", "and", "in", "on", "at", "of", "mr", "mrs", "dr"}
            for d in details:
                e_norm = re.sub(r'[^a-z0-9\s]', '', d["text"].lower()).strip()
                if c_norm == e_norm or c_norm in e_norm or e_norm in c_norm:
                    return True
                e_words = set(e_norm.split()) - {"the", "a", "an", "our", "to", "with", "for", "and", "in", "on", "at", "of", "mr", "mrs", "dr"}
                if c_words and e_words:
                    if len(c_words & e_words) / min(len(c_words), len(e_words)) >= 0.50:
                        return True
            return False

        # 1. Action phrases involving stakeholders/people
        # Check if stakeholder action points to a pronoun + noun (e.g. "show him the log file" -> "showing the log file")
        pro_stakeholder = re.findall(
            r'\b(?:show|showing|showed|tell|telling|told|brief|briefing|briefed)\s+(?:him|her|them)\s+(?:the\s+|a\s+|our\s+)?([a-z0-9-]{3,}(?:\s+[a-z0-9-]{3,}){0,3})\b',
            text,
            re.IGNORECASE
        )
        if pro_stakeholder:
            clean_ps = f"showing the {pro_stakeholder[0].strip()}"
            # Ensure the extracted phrase words are actually present in the source text
            ps_words = set(clean_ps.lower().split()) - {"showing", "the", "a", "an", "our"}
            src_words = set(re.findall(r'[a-z0-9-]{3,}', text.lower()))
            if ps_words and ps_words.issubset(src_words) and not is_dup(clean_ps):
                details.append({"text": clean_ps, "type": "verb_obj"})

        stakeholder_actions = re.findall(
            r'\b((?:explain|explaining|explained|brief|briefing|briefed|consult|consulting|consulted|'
            r'inform|informing|informed|notify|notifying|notified|meeting with|collaborate with|'
            r'collaborating with|aligned with|aligning with|showed|showing|communicate with|communicating with)\s+'
            r'(?:(?:to\s+|with\s+|dr\.?\s+|mrs\.?\s+|mr\.?\s+)?\w+))\b',
            text,
            re.IGNORECASE
        )
        for sa in stakeholder_actions:
            sa_clean = sa.strip().strip(".,;:!?'\"` ")
            sa_parts = sa_clean.split()
            while sa_parts and (sa_parts[-1].lower() in VERB_PREDICATES or sa_parts[-1].lower() in TRAILING_FUNCTION_WORDS or sa_parts[-1].lower() in PRONOUN_OBJECTS):
                sa_parts = sa_parts[:-1]
            sa_clean = " ".join(sa_parts).strip()
            sa_last = sa_parts[-1].lower() if sa_parts else ""
            if len(sa_parts) >= 2 and len(sa_clean) > 4 and sa_last not in PRONOUN_OBJECTS and sa_last not in TRAILING_FUNCTION_WORDS and not is_dup(sa_clean):
                details.append({"text": sa_clean, "type": "verb_obj"})
                break

        # 2. Verb + object or action
        verb_obj = re.findall(
            r'\b((?:stop|stopping|stopped|halt|halting|halted|pause|pausing|paused|delay|delaying|'
            r'deploy|deploying|deployed|cut|cutting|cutted|'
            r'reroute|re-route|rerouting|re-routing|rerouted|re-routed|'
            r'redirect|redirecting|redirected|tighten|tightening|tightened|'
            r'isolate|isolating|isolated|reduce|reducing|reduced|'
            r'shut down|shutting down|explain|explaining|explained|brief|briefing|briefed|'
            r'communicate|communicating|communicated|'
            r'test|testing|tested|prevent|preventing|prevented|avoid|avoiding|avoided|balance|balancing)\s+'
            r'(?:the\s+|a\s+|our\s+|properly|early|immediately|first|before\s+\w+)?'
            r'(?:mechanical emergency brake|emergency brake|subsea injection valve|subsea injection|'
            r'non-essential feeders|order execution|steam generator line|steam generator|reserve thrusters|'
            r'containment zone|airspace restrictions|transformer overheating|load shedding|'
            r'stepper motor mount|stepper motor|backup power module|primary telemetry sensor|'
            r'battery cells|thermal heat sinks|acrylic mount|metal bracket|current limits|'
            r'high-voltage pack|voltage pack|safety regulations|climbing speed|mount bracket|'
            r'throttle limits|motor mount|\w+(?:\s+\w+)?))\b',
            lower
        )
        for vo in verb_obj:
            vo_clean = vo.strip().strip(".,;:!?'\"` ")
            vo_parts = vo_clean.split()
            # Strip trailing predicate verbs AND trailing function/conjunction words
            while vo_parts and (vo_parts[-1].lower() in VERB_PREDICATES or vo_parts[-1].lower() in TRAILING_FUNCTION_WORDS or vo_parts[-1].lower() in PRONOUN_OBJECTS):
                vo_parts = vo_parts[:-1]
            vo_clean = " ".join(vo_parts).strip()
            vo_last = vo_parts[-1].lower() if vo_parts else ""
            vo_words = set(vo_parts)
            # Require at least 2 tokens (verb + noun/object) where the object is not a function word
            if len(vo_parts) >= 2 and len(vo_clean) > 4 and vo_last not in PRONOUN_OBJECTS and vo_last not in TRAILING_FUNCTION_WORDS and not (vo_words & ABSTRACT_META) and not is_dup(vo_clean):
                details.append({"text": vo_clean, "type": "verb_obj"})
                break

        # 3. Proper nouns (excluding conversational fillers, pronouns, and honorifics)
        KNOWN_PROPER = PERSON_NAMES | {"Navy", "Army", "Coast Guard", "Air Force", "Military", "NASA", "ISRO", "ESA", "FAA", "FDA", "OSHA", "NRC"}
        for i, w in enumerate(words):
            clean_w = w.strip(".,;:!?'\"`()")
            if clean_w in KNOWN_PROPER and not is_dup(clean_w):
                if clean_w in PERSON_NAMES:
                    details.append({"text": clean_w, "type": "person_name"})
                else:
                    details.append({"text": clean_w, "type": "proper_noun"})

        # 4. Quantity + role-noun
        qty_roles = re.findall(
            r'\b((?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+'
            r'(?:reserves?|runners?|members?|teams?|groups?|people|candidates?|'
            r'leaders?|backups?|options?|priorities?|steps?|checks?|tasks?))\b',
            lower
        )
        for qr in qty_roles:
            qr_clean = qr.strip().strip(".,;:!?'\"` ")
            if not is_dup(qr_clean):
                details.append({"text": qr_clean, "type": "quantity_role"})

        # 5. Adjective + domain-noun / key phrase (excluding abstract meta words)
        adj_nouns = re.findall(
            r'\b((?:primary|backup|reserve|key|main|lead|senior|junior|safety|'
            r'emergency|critical|initial|final|overall|immediate|biggest|major|good|clear|high-voltage|stepper|thermal|acrylic|metal)\s+'
            r'(?:runners?|members?|teams?|people|candidates?|leaders?|roles?|mount|bracket|'
            r'checks?|stops?|deployment|execution|task|'
            r'concern|robot|system|sensor|readings?|issue|problem|risk|pack|cells?|limits?))\b',
            lower
        )
        for an in adj_nouns:
            an_clean = an.strip().strip(".,;:!?'\"` ")
            if not any(m in an_clean for m in ABSTRACT_META) and not is_dup(an_clean):
                details.append({"text": an_clean, "type": "adj_noun"})

        # 6. Domain noun / concept fallback if details is empty (excluding abstract meta words)
        if not details:
            domain_terms = re.findall(
                r'\b(safety|overheating|cost overrun|cost|morale|team morale|data breach|breach|'
                r'failing|risk of failing|deadline|time constraint|budget|privacy|security|quality|'
                r'tradeoff|compromise|restrictions?|protocol|thermal runaway|current limits?)\b',
                lower
            )
            for dt in domain_terms:
                dt_clean = dt.strip().strip(".,;:!?'\"` ")
                if dt_clean not in ABSTRACT_META and not is_dup(dt_clean):
                    details.append({"text": dt_clean, "type": "domain_concept"})

        return details[:2]  # Return up to 2 distinct non-overlapping details

    @classmethod
    def join_details_safely(cls, formatted_details: List[str]) -> str:
        """Safely joins up to 2 formatted details ensuring non-duplication and verb-object semantic compatibility."""
        if not formatted_details:
            return ""
        if len(formatted_details) == 1:
            return formatted_details[0]

        d1_str = formatted_details[0]
        d2_str = formatted_details[1]

        # 1. Non-duplication check: token overlap >= 40%
        w0 = set(d1_str.lower().split()) - {"the", "a", "an", "our", "to", "with", "for", "and", "in", "on", "at", "of", "mr", "mrs", "dr"}
        w1 = set(d2_str.lower().split()) - {"the", "a", "an", "our", "to", "with", "for", "and", "in", "on", "at", "of", "mr", "mrs", "dr"}
        if w0 and w1 and (d1_str.lower() in d2_str.lower() or d2_str.lower() in d1_str.lower() or len(w0 & w1) / min(len(w0), len(w1)) >= 0.40):
            return d1_str if len(d1_str) >= len(d2_str) else d2_str

        # 2. Semantic verb-object compatibility check:
        # If d1 is a gerund action (e.g. "shutting down the high-voltage pack") and d2 is a passive measurement (e.g. "the thermal readings"),
        # joining with "and" causes the verb "shutting down" to govern "thermal readings", which is semantically invalid.
        MEASUREMENT_CONSTRAINTS = {"thermal readings", "readings", "temperature", "overheating", "speed", "limits", "voltage", "current", "telemetry"}
        d1_is_gerund = any(d1_str.lower().startswith(v) for v in ("shutting", "stopping", "halting", "cutting", "isolating", "re-routing", "rerouting", "deploying", "tightening", "briefing", "testing", "preventing", "showing"))
        d2_is_gerund = any(d2_str.lower().startswith(v) for v in ("shutting", "stopping", "halting", "cutting", "isolating", "re-routing", "rerouting", "deploying", "tightening", "briefing", "testing", "preventing", "complying", "communicating", "meeting", "showing"))

        # Both are gerund actions -> Valid parallel actions!
        if d1_is_gerund and d2_is_gerund:
            return f"{d1_str} and {d2_str}"

        # Both are component nouns -> Valid coordinate objects!
        if not d1_is_gerund and not d2_is_gerund:
            return f"{d1_str} and {d2_str}"

        # d1 is gerund action but d2 is passive measurement -> Drop d2 to avoid governing verb conflict
        d2_clean = re.sub(r'^(?:the|a|our)\s+', '', d2_str.lower()).strip()
        if d1_is_gerund and not d2_is_gerund:
            if any(m in d2_clean for m in MEASUREMENT_CONSTRAINTS):
                return d1_str
            return f"{d1_str} and {d2_str}"

        return d1_str

    @classmethod
    def format_detail(cls, detail: Dict[str, str]) -> str:
        """Transforms extracted detail dict into a smooth, natural conversational gerund or noun phrase."""
        text = detail["text"].strip()
        lower_t = text.lower()
        if lower_t.startswith(("i ", "we ", "i'd ", "i'm ", "i'll ", "i would ", "i will ", "i did ", "i chose ", "i decided ", "i stayed ", "i don't ", "not sure", "don't know", "no idea", "maybe ", "i guess ")):
            return ""

        # Clean trailing prepositions or conjunctions or predicate verbs
        text = re.sub(r'\s+(?:to|and|or|with|our|the|a|for|in|at|of|reduces|increases|helps|causes|leads|is|was)$', '', text, flags=re.IGNORECASE).strip()
        dtype = detail["type"]

        # Generalized Proper Noun / Organization / Entity Grounding
        if dtype in ("person_name", "proper_noun", "entity_name") or (len(text.split()) == 1 and text and text[0].isupper()):
            clean_ent = text.strip(".,;:!?'\"` ")
            if clean_ent in ("Arjun", "Meera", "George", "Uncle George"):
                return f"communicating with {clean_ent}"
            elif clean_ent in ("Dr. Arora", "Mrs. Sen", "Dr Arora", "Mrs Sen", "Dr. Reynolds", "Dr Reynolds"):
                return f"meeting with {clean_ent}"
            elif clean_ent in ("Navy", "Army", "Coast Guard", "Air Force", "Military"):
                return f"aligning with {clean_ent} regulations"
            elif clean_ent in ("NASA", "ISRO", "ESA", "FAA", "FDA", "OSHA", "NRC"):
                return f"complying with {clean_ent} standards"
            else:
                return f"navigating {clean_ent} constraints"

        elif dtype == "verb_obj":
            parts = text.split(maxsplit=1)
            verb = parts[0].lower()
            obj = parts[1] if len(parts) > 1 else ""

            # Prevent double-gerund stacking (e.g. "choosing deploying" -> "deploying the mechanical emergency brake")
            obj_words = obj.split()
            if obj_words:
                first_w = obj_words[0].lower()
                if first_w.endswith("ing") or first_w in ("deploy", "halt", "stop", "cut", "isolate", "brief", "tighten", "reroute", "re-route", "shut"):
                    if verb in ("choose", "choosing", "chose", "select", "selecting", "selected", "decide", "deciding", "decided", "prioritize", "prioritizing", "prioritized", "implement", "implementing", "implemented"):
                        return cls.format_detail({"text": obj, "type": "verb_obj"})

            IRREGULAR_GERUNDS = {
                "chose": "choosing",
                "choose": "choosing",
                "shut down": "shutting down",
                "re-route": "re-routing",
                "reroute": "rerouting",
                "stop": "stopping",
                "cut": "cutting",
                "set": "setting",
                "run": "running",
                "put": "putting",
                "plan": "planning",
            }

            if verb in IRREGULAR_GERUNDS:
                gerund = IRREGULAR_GERUNDS[verb]
            elif verb.endswith("e") and verb not in ("be", "see"):
                gerund = verb[:-1] + "ing"
            elif (len(verb) <= 4 and len(verb) >= 2
                  and verb[-1] not in "aeiouy" and verb[-2] in "aeiou"):
                gerund = verb + verb[-1] + "ing"
            elif verb.endswith("ed"):
                base = verb[:-2]
                gerund = base + "ing"
            else:
                gerund = verb + "ing" if not verb.endswith("ing") else verb
            return f"{gerund} {obj}".strip()
        else:
            return f"the {text}"

    def edit_dialogue(
        self,
        raw_question_text: str,
        summary_reference: str,
        target_dimension: str,
        used_openings: List[str],
    ) -> EditedDialogueResult:

        clean_raw = (raw_question_text or "").strip()
        stripped_phrases: List[str] = []

        # 1. Strip verbatim quotes and replace with rotated detail-oriented connectors
        pattern = (
            r'(?:(to|that|of|about)\s+)?'
            r"(?:"
            r"'([^']{8,}?(?:\.{3})?)'|"
            r'"([^"]{8,}?(?:\.{3})?)"'
            r")"
        )

        connector_idx = len(used_openings) % len(self.CONNECTOR_TEMPLATES)
        selected_connector_fmt = self.CONNECTOR_TEMPLATES[connector_idx]

        def replace_quoted(match: re.Match) -> str:
            preceding_prep = (match.group(1) or "").lower()
            inner = match.group(2) or match.group(3) or ""
            word_count = len(inner.strip().split())
            if word_count < 3:
                return match.group(0)

            stripped_phrases.append(match.group(0))
            details = self.extract_details_from_text(inner)

            if not details:
                if preceding_prep == "to":
                    return "to take that step"
                elif preceding_prep == "that":
                    return "that decision"
                return ""

            formatted = [self.format_detail(d) for d in details]
            detail_str = self.join_details_safely(formatted)

            # Check if there is an existing connector/preposition right before the match
            start_pos = max(0, match.start() - 25)
            text_before = clean_raw[start_pos:match.start()].strip().lower()
            last_word_before = text_before.split()[-1].strip(".,;:!'\"") if text_before.split() else ""

            if last_word_before in ("regarding", "concerning", "about", "of", "involving", "considering"):
                return detail_str

            if "what made you decide" in clean_raw.lower():
                return f"that {detail_str}"
            if "what priority guided" in clean_raw.lower() or "why did" in clean_raw.lower() or "what principal reason" in clean_raw.lower():
                return f"when evaluating {detail_str}"

            replacement = selected_connector_fmt.format(details=detail_str)

            if preceding_prep:
                if preceding_prep in replacement.lower():
                    return replacement
                elif preceding_prep == "to":
                    return f"regarding {detail_str}"
                elif preceding_prep == "that":
                    return f"that {detail_str}"
                else:
                    return f"{preceding_prep} {detail_str}"
            return replacement

        edited = re.sub(pattern, replace_quoted, clean_raw)

        # 2. Strip robotic lead-in phrases using case-insensitive regex
        for pat in self.ROBOTIC_PATTERNS:
            match = re.search(pat, edited, flags=re.IGNORECASE)
            if match:
                stripped_phrases.append(match.group(0))
                edited = edited[match.end():].strip()

        # 3. Clean leading punctuation, leftover connectors, stacked prepositions, and all ellipsis characters
        edited = re.sub(r"\b(regarding|concerning|involving|about|of|to)\s+(regarding|concerning|involving|about|of|to)\b", r"\1", edited, flags=re.IGNORECASE)
        edited = re.sub(r"^(?:regarding\s+your\s+decision\s+involving|regarding\s+your\s+choice\s+to|regarding\s+your\s+decision\s+to)\s+", "", edited, flags=re.IGNORECASE).strip()
        edited = re.sub(r"^(?:regarding\s+your\s+decision\s+to|regarding\s+your\s+decision)\s+", "", edited, flags=re.IGNORECASE).strip()
        edited = re.sub(r"^['\"\s,.:;]+", "", edited).strip()

        # Strip all literal ellipsis characters everywhere in the question text
        edited = re.sub(r'\.{3,}|\u2026', '', edited).strip()

        # Clean stacked or malformed punctuation (e.g. '.?', ',?', '??', '..')
        edited = re.sub(r'[\s.,;:!]+(\?)', r'\1', edited)
        edited = re.sub(r'\?{2,}', '?', edited)
        edited = re.sub(r'\.{2,}', '.', edited)
        edited = re.sub(r'\s{2,}', ' ', edited).strip()

        # 4. Select opening template from registry (preventing consecutive reuse)
        available = [t for t in self.OPENING_TEMPLATES if t not in used_openings[-5:]]
        selected_template = available[0] if available else self.OPENING_TEMPLATES[0]

        # 5. Apply wording compression & template formatting — enforce SINGLE opener structure
        if not edited.endswith("?"):
            edited += "?"

        question_starters = ["what", "how", "why", "if", "when", "where", "walk me", "help me", "tell me", "looking", "suppose", "reflecting", "one thing"]
        lower_edited = edited.lower()

        # Check if the question already has a natural question starter in any of its clauses
        has_natural_starter = any(
            re.search(rf'\b{qs}\b', lower_edited) for qs in question_starters
        )

        if lower_edited.startswith(("involving ", "regarding ", "concerning ", "with respect to ", "around ")):
            if has_natural_starter:
                edited = edited[0].upper() + edited[1:]
            else:
                edited = f"{selected_template} {edited[0].lower() + edited[1:]}"
        elif not has_natural_starter:
            edited = f"{selected_template} {edited[0].lower() + edited[1:]}"
        else:
            edited = edited[0].upper() + edited[1:]

        # Final cleanup of double spaces or double periods
        edited = re.sub(r'\.{2,}', '.', edited)
        edited = re.sub(r'\s{2,}', ' ', edited).strip()

        compression = round(len(edited) / max(len(clean_raw), 1), 2)

        return EditedDialogueResult(
            edited_question_text=edited,
            opening_template_used=selected_template,
            robotic_phrases_stripped=stripped_phrases,
            compression_ratio=compression,
        )
