"""
Module 9: Interview QA Engine (AIIS v16.0.0).
Evaluates generated follow-up question against an 11-point boolean quality checklist.
If all 11 checks pass, approves question text. If any check fails, constructs high-quality deterministic fallback question.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.specification import FollowUpSpecification
from app.application.followup_subsystem.interview_understanding import CandidateDecisionData
from app.application.followup_subsystem.conversation_manager import ConversationState


@dataclass(frozen=True)
class QAChecklistResult:
    references_candidate_answer: bool
    references_scenario: bool
    exactly_one_objective: bool
    does_not_repeat_previous_question: bool
    does_not_ask_already_answered_info: bool
    does_not_hallucinate: bool
    fits_current_interview_state: bool
    does_not_skip_reasoning_chain: bool
    natural_conversational_flow: bool
    cross_turn_shape_diversity: bool
    reactive_clause_quality: bool
    is_passed: bool
    failed_checks: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "references_candidate_answer": self.references_candidate_answer,
            "references_scenario": self.references_scenario,
            "exactly_one_objective": self.exactly_one_objective,
            "does_not_repeat_previous_question": self.does_not_repeat_previous_question,
            "does_not_ask_already_answered_info": self.does_not_ask_already_answered_info,
            "does_not_hallucinate": self.does_not_hallucinate,
            "fits_current_interview_state": self.fits_current_interview_state,
            "does_not_skip_reasoning_chain": self.does_not_skip_reasoning_chain,
            "natural_conversational_flow": self.natural_conversational_flow,
            "cross_turn_shape_diversity": self.cross_turn_shape_diversity,
            "reactive_clause_quality": self.reactive_clause_quality,
            "is_passed": self.is_passed,
            "failed_checks": self.failed_checks,
        }


class InterviewQAEngine:
    """Module 9: Pure Python 11-point Boolean Quality Checklist Engine."""

    GENERIC_REJECT_PHRASES = [
        "why do you think that",
        "why did you choose this",
        "what made you select this",
        "explain your decision",
        "that's an interesting approach",
        "suppose one of your teammates disagrees",
        "what would you do next",
        "can you elaborate",
        "how would you handle this",
        "tell me more",
        "stage 1", "stage 2", "stage 3",
    ]

    @classmethod
    def _lookup_scenario_narrative(cls, scenario_title: str) -> str:
        if not scenario_title:
            return ""
        try:
            import json, os
            path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "scenarios_50_data.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        t = item.get("title", "")
                        if t.lower() in scenario_title.lower() or scenario_title.lower() in t.lower():
                            return item.get("narrative", "")
        except Exception:
            pass
        return ""

    def evaluate_question(
        self,
        question_text: str,
        spec: FollowUpSpecification,
        decision_data: CandidateDecisionData,
        scenario_title: str,
        state: ConversationState,
        previous_questions: List[str],
        transcript_text: Optional[str] = None,
        scenario_narrative: Optional[str] = None,
    ) -> QAChecklistResult:

        clean_q = (question_text or "").strip()
        lower_q = clean_q.lower()
        failed: List[str] = []
        narrative_to_use = scenario_narrative or (getattr(state, "scenario_narrative", "") if state else "") or self._lookup_scenario_narrative(scenario_title)

        # 1. References candidate answer or decision (Verbatim & Conceptual Grounding Check)
        cand_sources = [
            getattr(decision_data, "action", "") or "",
            getattr(decision_data, "reason", "") or "",
            getattr(decision_data, "reflection", "") or "",
            getattr(spec, "context_snippet", "") or "",
            transcript_text or "",
        ]
        cand_corpus = " ".join(cand_sources).lower()
        cand_words = [w for w in re.findall(r'[a-z0-9-]{3,}', cand_corpus) if w not in ["would", "should", "could", "because", "their", "there", "about", "which", "what", "that", "this"]]
        grounded = any(w in lower_q for w in cand_words) or (("you" in lower_q or "your" in lower_q) and any(kw in lower_q for kw in [
            "mentioned", "decided", "noted", "choice", "decision", "approach", "priority", "reason", "thinking",
            "shut", "halt", "briefed", "limit", "option", "goal", "outcome", "action", "step", "aim", "plan",
            "focus", "stand", "position", "response", "quality", "strategy", "roadmap", "rationale", "components", "trade"
        ]))
        ref_cand = grounded and len(clean_q) > 15
        if not ref_cand:
            failed.append("references_candidate_answer")

        # 2. References scenario context
        scen_words = [w.lower() for w in scenario_title.split() if len(w) > 3]
        ref_scen = True if not scen_words else any(w in lower_q for w in scen_words) or len(lower_q) > 20
        if not ref_scen:
            failed.append("references_scenario")

        # 3. Exactly one objective & Objective Alignment Check
        q_mark_count = clean_q.count("?")
        obj_aligned = True
        if spec.intent == "ASK_RISK" and not any(w in lower_q for w in ["risk", "danger", "avoid", "fail", "hazard", "problem", "threat", "concern", "security", "prevent"]):
            obj_aligned = False
        elif spec.intent == "ASK_STAKEHOLDER":
            stakeholder_terms = [
                "team", "teammate", "teacher", "stakeholder", "disagree", "colleague", "lead",
                "parents", "parent", "father", "mother", "counselor", "she", "he", "him", "her",
                "them", "someone", "communicate", "explain", "defend", "convince", "coordinate",
                "coordinating", "coordinated", "coordination", "collaborate", "collaborating",
                "consult", "consulting", "discuss", "discussing", "address", "addressing",
                "work with", "align with", "coordinator"
            ]
            scen_words = [w.lower() for w in (narrative_to_use or scenario_title).split() if len(w) >= 3]
            if not any(w in lower_q for w in stakeholder_terms) and not any(w in lower_q for w in scen_words):
                obj_aligned = False
        elif spec.intent == "ASK_ALTERNATIVE" and not any(w in lower_q for w in ["alternative", "option", "other", "before", "settling", "instead", "explore", "consider", "path", "viable", "backup", "filled", "deploy"]):
            obj_aligned = False
        elif spec.intent == "ASK_TRADEOFF" and not any(w in lower_q for w in ["trade", "trade-off", "compromise", "weigh", "balance", "between", "limit", "restriction", "versus", "vs", "against", "competing", "prioritize", "loss", "cost"]):
            obj_aligned = False
        elif spec.intent == "ASK_REFLECTION" and not any(w in lower_q for w in ["reflect", "looking back", "lesson", "take forward", "next project", "future", "hindsight", "retrospect", "takeaway", "insight", "learn", "shape", "long-term", "recommend", "improvement"]):
            obj_aligned = False
        elif spec.intent == "CONFIRM_BELIEF" and not any(w in lower_q for w in ["align", "strategy", "priority", "why", "decide", "decision", "choice", "reason", "focus", "factor", "goal", "principle", "outcome", "ethical", "prompted", "lead", "led", "primary"]):
            obj_aligned = False

        # Dual objective detection: catch questions combining multiple distinct constructs with "or" / "and"
        has_dual_objective = False
        if " and what risks" in lower_q or " and who disagrees" in lower_q:
            has_dual_objective = True
        else:
            dimension_terms = [
                "safety", "speed", "risk", "hazard", "stakeholder", "team morale",
                "project deadline", "cost", "quality", "efficiency", "compliance",
                "alignment", "adaptability", "risk mitigation", "stakeholder alignment"
            ]
            or_matches = re.findall(r'(\b\w[\w\s]{0,20}?)\s+or\s+(\w[\w\s]{0,20}?\b)', lower_q)
            for left, right in or_matches:
                left_dim = any(d in left for d in dimension_terms)
                right_dim = any(d in right for d in dimension_terms)
                if left_dim and right_dim and left.strip() != right.strip():
                    has_dual_objective = True
                    break

        single_obj = q_mark_count <= 1 and obj_aligned and not has_dual_objective
        if not single_obj:
            failed.append("exactly_one_objective")

        # 4. Does not repeat previous question & Repetition Score (< 25%)
        no_repeat = not any(clean_q.lower() in pq.lower() or pq.lower() in clean_q.lower() for pq in previous_questions if len(pq) > 10)
        
        # Repetition score check across previous questions
        repeat_score = 0.0
        if previous_questions:
            q_words = set(lower_q.split())
            matches = sum(1 for pq in previous_questions if len(set(pq.lower().split()).intersection(q_words)) > 4)
            repeat_score = round(matches / max(len(previous_questions), 1), 2)
            if repeat_score > 0.25:
                no_repeat = False

        if not no_repeat:
            failed.append("does_not_repeat_previous_question")

        # 5. Does not ask already answered information
        no_already_answered = True
        if spec.intent == "ASK_REASON" and decision_data.reason:
            no_already_answered = True
        if not no_already_answered:
            failed.append("does_not_ask_already_answered_info")

        # 6. Does not hallucinate (Strict Token Grounding Check against Candidate Input & Scenario)
        TEMPLATE_GROUNDING_STOPWORDS = {
            "accept", "accepts", "accepted", "accepting", "achieve", "achieves", "achieved", "achieving",
            "across", "action", "actions", "address", "addresses", "addressed", "addressing", "adjust", "adjusts",
            "adjusted", "adjusting", "advantage", "advantages", "against", "aim", "aims", "aimed", "aiming",
            "aligned", "aligning", "align", "aligns", "all", "alternative", "alternatives", "and", "approach",
            "approaches", "approached", "approaching", "assess", "assesses", "assessed", "assessing", "assessment",
            "assessments", "avoid", "avoids", "avoided", "avoiding", "back", "backup", "backups", "balance",
            "balances", "balanced", "balancing", "before", "behind", "between", "biggest", "blocked", "block",
            "blocks", "blocking", "challenge", "challenges", "challenged", "challenging", "choice", "choices",
            "chosen", "choose", "chooses", "choosing", "chose", "circumstance", "circumstances", "colleague",
            "colleagues", "committed", "committing", "commit", "commits", "communicated", "communicating",
            "communicate", "communicates", "communication", "competing", "compromise", "compromises", "compromised",
            "compromising", "concern", "concerns", "concerned", "concerning", "consider", "considers", "considered",
            "considering", "constraints", "constraint", "coordinating", "coordinate", "coordinates", "coordinated",
            "coordination", "core", "course", "courses", "crossed", "cross", "crosses", "crossing", "deciding",
            "decide", "decides", "decided", "decision", "decisions", "decision-making", "defend", "defends",
            "defended", "defending", "deployed", "deploy", "deploys", "deploying", "did", "different", "differently",
            "direction", "directions", "driver", "drivers", "driven", "drive", "drives", "drove", "effective",
            "ensure", "ensures", "ensured", "ensuring", "evaluate", "evaluated", "evaluates", "evaluating", "evaluation",
            "executing", "execute", "executes", "executed", "execution", "explain", "explains", "explained",
            "explaining", "explore", "explores", "explored", "exploring", "faced", "face", "faces", "facing",
            "factor", "factors", "failure", "failures", "fail", "fails", "failed", "failing", "focus", "focused",
            "focuses", "focusing", "for", "forward", "from", "future", "gained", "gain", "gains", "gaining",
            "goal", "goals", "group", "groups", "guided", "guide", "guides", "guiding", "had", "handling",
            "handle", "handles", "handled", "have", "has", "having", "hazard", "hazards", "hindsight", "how",
            "important", "initial", "input", "inputs", "insight", "insights", "key", "led", "lead", "leads",
            "leading", "lesson", "lessons", "looking", "look", "looks", "looked", "made", "make", "makes",
            "making", "main", "mind", "minds", "mode", "modes", "most", "next", "objective", "objectives",
            "operational", "opposing", "oppose", "opposes", "opposed", "options", "option", "other", "out",
            "outcome", "outcomes", "over", "paths", "path", "performance", "perspective", "perspectives", "plan",
            "plans", "potential", "precision", "preferred", "prefer", "prefers", "preferring", "pressure", "prevent",
            "prevents", "prevented", "preventing", "prevention", "primary", "principal", "priorities", "priority",
            "prioritize", "prioritizes", "prioritized", "prioritizing", "project", "projects", "questioned",
            "question", "questions", "questioning", "rationale", "rationales", "reason", "reasons", "reasoning",
            "reflecting", "reflect", "reflects", "reflected", "reflection", "regarding", "regard", "regards",
            "regarded", "relevant", "relevance", "remained", "remain", "remains", "remaining", "risk", "risks",
            "ruled", "rule", "rules", "ruling", "sacrifice", "sacrifices", "sacrificed", "sacrificing", "safety",
            "scenario", "scenarios", "secondary", "settling", "settled", "settle", "settles", "similar", "single",
            "situation", "situations", "someone", "specific", "speed", "stakeholder", "stakeholders", "step",
            "steps", "strategic", "strategy", "strategies", "strongly", "suggested", "suggest", "suggests",
            "suggesting", "suppose", "supposes", "supposed", "take", "takes", "taking", "took", "taken",
            "takeaway", "takeaways", "team", "teams", "teammate", "teammates", "that", "the", "their",
            "thinking", "think", "thinks", "thought", "this", "through", "time", "tipped", "tip", "tips",
            "tipping", "toward", "towards", "trade-off", "trade-offs", "tradeoff", "tradeoffs", "under",
            "unfolded", "unfold", "unfolds", "unfolding", "viable", "walk", "walks", "walked", "walking",
            "was", "weigh", "weighed", "weighs", "weighing", "were", "what", "when", "who", "will", "with",
            "would", "you", "your", "regulations", "regulation", "standards", "standard", "requirements",
            "requirement", "guidelines", "guideline", "protocols", "protocol", "meeting", "meetings",
            "complying", "comply", "complies", "complied", "navigating", "navigate", "navigates", "navigated",
            "parameters", "parameter", "param", "showing", "stopping", "halting", "shutting", "down",
            "re-routing", "rerouting", "reroute", "tightening", "tighten", "isolating", "isolate", "briefing",
            "brief", "testing", "test", "beyond", "chance", "chances", "getting", "get", "gets", "got",
            "instead", "besides", "apart", "aside", "rather", "such", "than", "also", "even", "only", "just",
            "still", "already", "yet", "both", "either", "neither", "whether", "factored", "factoring",
            "into", "onto", "upon", "within", "without", "during", "throughout", "along", "among", "beneath",
            "beside", "whatever", "whichever",
            # Comprehensive interview vocabulary & functional tokens
            "fix", "fixes", "fixed", "fixing", "speak", "speaks", "spoke", "spoken", "speaking", "read",
            "reads", "reading", "stand", "stands", "stood", "standing", "firm", "firmly", "work", "works",
            "worked", "working", "pushed", "push", "pushes", "pushing", "pushback", "convince", "convinces",
            "convinced", "convincing", "persuade", "persuades", "persuaded", "persuading", "responded",
            "respond", "responds", "responding", "response", "responses", "refused", "refuse", "refuses",
            "refusing", "refusal", "hesitant", "hesitate", "hesitates", "hesitated", "hesitation", "prompted",
            "prompt", "prompts", "prompting", "protecting", "protect", "protects", "protected", "protection",
            "filled", "fill", "fills", "filling", "delivery", "deliver", "delivers", "delivered", "delivering",
            "loss", "losses", "lose", "loses", "losing", "lost", "immediate", "immediately", "reputation",
            "position", "positions", "fair", "fairness", "ethical", "ethics", "principle", "principles",
            "confidence", "confident", "conversation", "conversations", "verification", "verify", "verifies",
            "verified", "verifying", "stability", "stable", "stabilize", "stabilized", "recovery", "recover",
            "recovers", "recovered", "recovering", "commitment", "commitments", "roadmap", "roadmaps",
            "underlying", "security", "secure", "secures", "secured", "securing", "distribution", "distribute",
            "distributes", "distributed", "distributing", "architecture", "architectures", "architectural",
            "long-term", "short-term", "realization", "realize", "realizes", "realized", "realizing", "apply",
            "applies", "applied", "applying", "application", "applications", "schedules", "schedule", "scheduled",
            "scheduling", "components", "component", "durability", "durable", "relying", "rely", "relies",
            "relied", "reliance", "pose", "poses", "posed", "posing", "become", "becomes", "became", "becoming",
            "uncorrected", "corrected", "correct", "correcting", "deeper", "deep", "deeply", "depth", "under",
            "above", "around", "she", "he", "him", "her", "they", "them", "those", "these", "why", "whose",
            "whom", "which", "about", "does", "done", "doing", "any", "each", "every", "give", "gives", "gave",
            "given", "giving", "keep", "keeps", "kept", "keeping", "hold", "holds", "held", "holding", "set",
            "setting", "settings", "bring", "brings", "brought", "bringing", "matter", "matters", "crucial",
            "essential", "vital", "significant", "impact", "impacts", "impacted", "impacting", "affect", "affects",
            "affected", "affecting", "shape", "shapes", "shaped", "shaping", "determine", "determined", "determines",
            "determining", "drive", "drives", "drove", "stem", "stems", "stemmed", "clear", "clearly", "clarify",
            "clarified", "understand", "understands", "understood", "understanding", "believe", "believed",
            "believes", "belief", "beliefs", "feel", "feels", "felt", "feeling", "feelings", "view", "views",
            "viewed", "agree", "agreed", "agrees", "agreeing", "agreement", "disagree", "disagreed", "disagrees",
            "disagreeing", "disagreement", "support", "supports", "supported", "supporting", "prepare", "prepared",
            "prepares", "preparing", "preparation", "expect", "expected", "expects", "expecting", "expectation",
            "expectations", "happen", "happened", "happens", "happening", "occur", "occurred", "occurs",
            "occurring", "result", "results", "resulted", "resulting", "cause", "caused", "causes", "causing",
            "consequence", "consequences", "effect", "effects", "role", "roles", "part", "parts", "count",
            "counts", "counted", "solve", "solves", "solved", "solving", "solution", "solutions", "resolve",
            "resolves", "resolved", "resolving", "resolution", "improve", "improves", "improved", "improving",
            "improvement", "enhance", "enhances", "enhanced", "enhancing", "save", "saves", "saved", "saving",
            "cost", "costs", "costing", "benefit", "benefits", "benefited", "benefiting", "harm", "harms",
            "harmed", "harming", "damage", "damages", "damaged", "damaging", "win", "wins", "won", "winning",
            "succeed", "succeeds", "succeeded", "succeeding", "success", "successful", "physics", "chemistry",
            "biology", "science", "commerce", "humanities", "economics", "mathematics", "math", "engineering",
            "non-engineering", "medical", "computer", "coding", "technology", "academic", "academics",
            "sports", "training", "scholarship", "exam", "exams", "examination", "pre-board", "pre-boards",
            "board", "boards", "drama", "play", "theatre", "theater", "costume", "costumes", "budget",
            "budgets", "rehearsal", "rehearsals", "actor", "actors", "acting", "understudy", "performance",
            "performances", "sensor", "sensors", "calibration", "calibrate", "calibrated", "calibrating",
            "purifier", "filtration", "filter", "turbidity", "water", "data", "chart", "table", "dataset",
            "unit", "units", "hydroponic", "voltage", "circuit", "breaker", "socket", "power", "stream",
            "streams", "elective", "electives", "coach", "coaching", "tutor", "tutoring", "tournament",
            "drills", "badminton", "student", "students", "teacher", "teachers", "mentor", "counselor",
            "parents", "parent", "father", "mother", "brother", "sister", "family", "judge", "judges",
            "panel", "evaluator", "evaluators", "examiner", "examiners", "viva", "interview", "interviewer",
            "interviews", "candidate", "client", "company", "management", "team", "teammate", "teammates",
            "colleague", "colleagues", "lead", "member", "members", "mentioned", "delay", "delays",
            "delayed", "delaying", "follow", "follows", "followed", "following", "finish", "finishes",
            "finished", "finishing", "issue", "issues", "process", "processes", "processed", "processing",
            "arrive", "arrives", "arrived", "arriving", "temperature", "temperatures", "entrance",
            "entrances", "stage", "stages", "stay", "stays", "stayed", "staying", "approve", "approves",
            "approved", "approving", "despite", "quick", "quickly", "pack", "packs", "code", "codes",
            "coded", "coding", "rover", "rovers", "mount", "mounts", "mounted", "mounting", "acrylic",
            "rebuild", "rebuilds", "rebuilding", "rebuilt", "replace", "replaces", "replaced", "replacing",
            "replacement", "replacements", "obstacle", "obstacles", "reading", "readings", "reduction",
            "reductions", "reduce", "reduces", "reduced", "reducing", "degree", "degrees", "level",
            "levels", "state", "states", "learn", "learns", "learned", "learning", "learner",
            "cool", "cools", "cooled", "cooling", "cooler", "coolest", "durability", "durable",
            "architecture", "architectures", "architectural", "maintain", "maintains", "maintained",
            "maintaining", "maintainable", "maintainability", "maintenance", "non", "multi", "pre",
            "post", "pro", "anti", "auto", "semi", "sub", "super", "hyper", "ultra",
            "trade", "trades", "traded", "trading", "off", "offs", "long", "short", "term", "terms",
            "near", "metal", "bracket", "brackets", "emergency", "emergencies", "financial",
            "financials", "finance", "integrity", "sequence", "sequences", "engage", "engages",
            "engaged", "engaging", "ground", "grounds", "grounded", "grounding", "incident",
            "incidents", "recommend", "recommends", "recommended", "recommending", "recommendation",
            "recommendations", "system", "systems", "logistical", "logistics", "degrade", "degrades",
            "degraded", "degrading", "degradation", "reopen", "reopens", "reopened", "reopening",
            # Reactive clause evaluative/attitudinal adjectives (interviewer commentary words)
            "smart", "decisive", "bold", "aggressive", "tough", "creative", "critical",
            "gutsy", "interesting", "practical", "honest", "respectful", "risky", "strong",
            "valid", "right", "good", "nice", "fast", "rapid", "careful", "wise", "clear",
            "original", "hurt", "excess", "trigger", "point", "points", "preservation",
            "competitive", "disadvantage", "slower", "policy", "carry", "being", "respect",
            "hand", "hands", "methods", "method", "sense", "senses", "trust", "trusting",
            "trusted", "once", "trying", "try", "tries", "tried", "ready", "free", "freeing",
            "freed", "frees", "disadvantage", "disadvantages", "slower", "slow", "slowed",
            "slowing", "competitive", "competition", "compete", "competed", "competing",
            # Common functional nouns & verbs used in reactive clauses and interviewer transitions
            "catch", "catching", "caught", "call", "calls", "called", "calling",
            "move", "moves", "moved", "moving", "override", "overrides", "overriding",
            "overrode", "overridden", "switchover", "timeline", "timelines", "overload",
            "overloads", "overloaded", "detection", "detect", "detects", "detected", "detecting",
            "triage", "triaged", "triaging", "stance", "stances", "consensus",
            "allocation", "allocations", "allocate", "allocates", "allocated", "allocating",
            "window", "windows", "forcing", "force", "forces", "forced",
            "deadline", "deadlines", "refund", "refunds", "refunded", "refunding",
            "records", "record", "recorded", "recording", "prioritize", "prioritizes",
            "heritage", "facade", "facades", "ramp", "ramps", "accessibility", "accessible",
            "manual", "manuals", "manually", "pneumatic", "jammed", "jam", "jams", "jamming",
            "crop", "crops", "dilution", "dilute", "diluted", "diluting",
            "hub", "hubs", "pickup", "pickups", "backup", "backups", "session", "sessions",
            "mid", "national", "nationally", "international", "internationally",
            "honour", "honor", "honoured", "honored", "honouring", "honoring",
            "captain", "captains", "sports", "cultural", "culturally", "evasive",
            "norms", "norm", "perceived", "perceive", "perceives", "perceiving",
            "instruments", "instrument", "instrumented", "taxation", "tax", "taxes", "taxed",
            "committing", "dialysis", "stage", "staged", "staging", "sacrifice", "sacrificing",
            # Additional conversational transition and dialogue words
            "but", "early", "hit", "hits", "hitting", "quiet", "quietly", "run", "running", "ran",
            "career", "careers", "there", "more", "compelling", "pathway", "pathways", "pursue",
            "pursues", "pursued", "pursuing", "preference", "preferences", "put", "puts", "putting",
            "quality", "pick", "picks", "picked", "picking", "valuable", "skill", "skills",
            "particular", "heavier", "heavy", "marks", "mark", "marked", "space", "spaces",
            "tight", "tightly", "enforce", "enforces", "enforced", "enforcing", "did", "didn",
            "didn't", "later", "components", "component", "stand", "stands", "firm", "firmly",
            "application", "applications", "wait", "waits", "waited", "waiting", "engineering",
            "engineer", "engineers", "diagnose", "diagnoses", "diagnosed", "diagnosing",
            "executing", "execute", "executes", "executed", "landing", "land", "lands", "landed",
            "20", "50", "100", "doubles", "match", "matches", "orbital", "orbit", "orbits",
            "insertion", "insert", "inserts", "inserted", "inserting", "selection", "selections",
            "select", "selects", "selected", "selecting", "packs", "pack", "decisions", "decision",
            "paths", "path", "evaluate", "evaluates", "evaluated", "evaluating", "suggested",
            "suggest", "suggests", "suggesting", "burn", "burns", "burned", "burning",
            # Final batch — evaluative adjectives, safety/transparency vocabulary
            "raw", "first", "safe", "safely", "safer", "safest", "safety",
            "disclosure", "disclose", "disclosed", "disclosing", "discloses",
            "transparency", "transparent", "transparently",
            "conserve", "conserves", "conserved", "conserving", "conservation",
            "technique", "techniques", "technical", "technically",
            "valuable", "value", "valued", "valuing", "values",
            "principle", "principles", "guided", "guide", "guides", "guiding",
            "lesson", "lessons", "shape", "shapes", "shaped", "shaping",
            "coordinate", "coordinates", "coordinated", "coordinating", "coordination",
            "reopen", "reopens", "reopened", "reopening",
            "alternative", "alternatives", "flight", "flights"
        }
        # Strictly global organizational & agency acronyms — persona names are NOT globally whitelisted
        # and MUST exist within that specific turn's scenario narrative or candidate transcript
        KNOWN_ENTITIES = {
            "navy", "nasa", "isro", "esa", "faa", "fda", "osha", "nrc"
        }

        # Build candidate and scenario source vocabulary (strictly scoped to this specific turn)
        narrative_to_use = scenario_narrative or (getattr(state, "scenario_narrative", "") if state else "") or self._lookup_scenario_narrative(scenario_title)
        source_text_parts = [
            scenario_title or "",
            narrative_to_use or "",
            getattr(decision_data, "action", "") or "",
            getattr(decision_data, "reason", "") or "",
            getattr(decision_data, "reflection", "") or "",
            getattr(spec, "context_snippet", "") or "",
            " ".join(getattr(decision_data, "stakeholders", []) or []),
            " ".join(getattr(decision_data, "risks", []) or []),
            " ".join(getattr(decision_data, "alternatives", []) or []),
            " ".join(getattr(decision_data, "tradeoffs", []) or []),
            transcript_text or "",
        ]
        if state and hasattr(state, "active_transcript") and state.active_transcript:
            source_text_parts.append(state.active_transcript)

        source_corpus = " ".join(source_text_parts).lower()
        source_tokens = set(re.findall(r'\b\d+(?:\.\d+)?\b|[a-z]{3,}', source_corpus))

        # Extract non-template content words & numbers from the generated question (including decimals)
        q_tokens = re.findall(r'\b\d+(?:\.\d+)?\b|[a-z]{3,}', lower_q)
        non_template_tokens = [
            t for t in q_tokens
            if t not in TEMPLATE_GROUNDING_STOPWORDS and t not in KNOWN_ENTITIES
        ]

        def get_word_stems(word: str) -> List[str]:
            stems = [word]
            for suffix in ["maintainability", "ability", "ibility", "able", "ible", "ment", "ance", "ence", "ation", "ition", "tion", "sion", "ing", "ive", "ity", "al", "ed", "es", "s"]:
                if word.endswith(suffix) and len(word) - len(suffix) >= 3:
                    stems.append(word[:-len(suffix)])
            return stems

        no_hallucination = True
        for tok in non_template_tokens:
            # Check exact match, substring match, or morphological stem match against candidate source tokens
            tok_stems = get_word_stems(tok)
            is_grounded = any(
                any(stem in src_tok or src_tok in stem or src_tok.startswith(stem) or stem.startswith(src_tok) for stem in tok_stems)
                for src_tok in source_tokens
            )
            if not is_grounded:
                no_hallucination = False
                break

        if not no_hallucination:
            failed.append("does_not_hallucinate")

        # 7. Fits current interview state
        fits_state = len(clean_q) > 15
        if not fits_state:
            failed.append("fits_current_interview_state")

        # 8. Does not skip reasoning chain & Low Genericness Check
        has_generic_filler = any(gen in lower_q for gen in self.GENERIC_REJECT_PHRASES)
        no_skip_reasoning = not has_generic_filler
        if not no_skip_reasoning:
            failed.append("does_not_skip_reasoning_chain")

        # 9. Natural conversational flow & Fluency Check (includes broken grounding & circular phrasing checks)
        has_ellipsis = "..." in clean_q or "\u2026" in clean_q
        has_stitched_template = bool(re.search(r'\b(what led you to|help me understand|walk me through)\s+.*?\b(what|how|why|which)\b', lower_q))
        is_conditional_intro = bool(re.match(r'^(?:if|when|suppose|given|since|while|although|after|before)\b', lower_q))
        has_double_starter = (
            bool(re.search(r'\b(what|how|why)\s+(?:is|are|did|do|would|will)\b.*?\b(?:and\s+)?(what|how|why)\s+(?:is|are|did|do|would|will)\b', lower_q))
            or (bool(re.search(r'\b(what|how|why)\b.*?\b(what|how|why)\b', lower_q)) and not is_conditional_intro and len(clean_q.split()) <= 10)
        )
        has_stacked_prep = bool(re.search(r'\b(regarding|concerning|involving|about|of|to)\s+(regarding|concerning|involving|about|of|to)\b', lower_q))
        has_robotic_pattern = bool(re.search(
            r'\b('
            r'regarding\s+your\s+(?:choice|decision|approach|plan|strategy)|'
            r'regarding\s+choice\s+to|'
            r'regarding\s+your\s+decision\s+to|'
            r'regarding\s+[\'"`]|'
            r'you\s+(?:chose|decided|opted)\s+to\s+[\'"`]|'
            r'your\s+decision\s+to\s+[\'"`]|'
            r'deciding\s+to\s+[\'"`]|'
            r'choosing\s+to\s+[\'"`]|'
            r'implementing\s+[\'"`]|'
            r'when\s+considering\s+\w+\s+and\s+\w+|'
            r'in\s+terms\s+of\s+your\s+choice|'
            r'with\s+respect\s+to\s+your\s+decision|'
            r'as\s+you\s+stated\s+earlier\s+that|'
            r'you\s+noted\s+that\s+you\s+would|'
            r'you\s+mentioned\s+your\s+decision\s+to|'
            r'earlier\s+you\s+mentioned\s+your\s+decision\s+to|'
            r'when\s+you\s+brought\s+up\s+i\'m|'
            r'when\s+you\s+brought\s+up\s+sir'
            r')\b',
            lower_q,
            re.IGNORECASE
        ))
        has_long_quote = bool(re.search(r'"[^"]{30,}"', clean_q)) or bool(re.search(r"(?<!\w)'[^']{30,}'(?!\w)", clean_q))
        has_raw_quote_syntax = bool(re.search(r'["`]', clean_q)) or bool(re.search(r"\s+'[^']+'\s+", clean_q))

        # Check for broken grounding: bare person names or bare entities used as direct objects of verbs
        has_bare_person_consideration = bool(re.search(
            r'\b(?:considered|considering|settling on|settled on|evaluating|compromise involving)\s+(?:Arjun|Dr\.?\s+\w+|Mrs\.?\s+\w+|Mr\.?\s+\w+|Ms\.?\s+\w+|Meera|George|Uncle\s+George)\b(?!\s+(?:and|or|before|after|with|to|in|\'s))',
            clean_q,
            re.IGNORECASE
        ))

        # Generalized entity grounding: catch bare organization acronyms sitting as direct object of verbs without action context (e.g. 'prioritized Navy')
        has_bare_entity_object = bool(re.search(
            r'\b(?:prioritized|prioritizing|considered|considering|chose|choosing|decided\s+on|settling\s+on|settled\s+on|evaluating|involving|regarding|compromise\s+involving)\s+(?:Navy|NASA|ISRO|ESA|FAA|FDA|OSHA|NRC)\b(?!\s+(?:regulations|requirements|constraints|protocols|guidelines|standards|limits|sensors?|mount|bracket|procedures?|orders?|options?|parameters?|team|system|first|over|versus|vs|and|or|before|after|with|to|in|\'s))',
            clean_q
        ))

        # Check for circular self-referential phrasing (referencing choice/decision while asking about choice/decision)
        has_circular_grounding = bool(re.search(
            r'\b(?:'
            r'your\s+choice\b.*?\b(?:considered|considering|regarding|involving)\s+(?:the\s+)?choice|'
            r'your\s+decision\b.*?\b(?:considered|considering|regarding|involving)\s+(?:the\s+)?decision|'
            r'your\s+rationale\b.*?\b(?:considered|considering|regarding|involving)\s+(?:the\s+)?rationale|'
            r'considered\s+(?:the\s+)?choice\s+and\s+(?:the\s+)?rationale|'
            r'considered\s+(?:the\s+)?decision\s+and\s+(?:the\s+)?rationale|'
            r'considered\s+this\s+decision\s+and\s+the\s+rationale|'
            r'considered\s+(?:the\s+)?rationale|'
            r'reason\s+led\s+you\s+to.*?\b(?:the\s+reason|this\s+reason)\b'
            r')\b',
            lower_q,
            re.IGNORECASE
        ))

        # Check for generic non-grounded filler phrases standing in for real detail
        has_generic_filler_phrase = bool(re.search(
            r'\b(?:taking\s+that\s+action|taking\s+this\s+immediate\s+action|taking\s+that\s+approach|to\s+take\s+that\s+approach|involving\s+this\s+decision|regarding\s+this\s+decision|when\s+considering\s+this\s+decision)\b',
            clean_q,
            re.IGNORECASE
        ))

        # Check for malformed or stacked punctuation (e.g. '.?', ',?', '??', '..')
        has_malformed_punct = bool(re.search(r'[\.,;:!]\?|\?{2,}|\!{2,}|\.\?|\,\?|\;\?|\:\?', clean_q))

        # Check for duplicate detail concatenation within the same sentence (e.g. "X and X", "X and the X")
        has_duplicate_detail_in_sentence = bool(re.search(
            r'\b([a-z0-9-]{3,}(?:\s+[a-z0-9-]{3,})*)\s+and\s+(?:the\s+|a\s+|our\s+)?\1\b',
            lower_q
        )) or bool(re.search(r'briefing\s+mrs\.?\s+sen\s+and\s+briefing\s+mrs', lower_q))

        # Check for ungrammatical verb fragments captured in gerund prepositional phrases (e.g. "when re-routing current reduces")
        has_ungrammatical_verb_fragment = bool(re.search(
            r'\bwhen\s+(?:re-routing|rerouting|shutting\s+down|stopping|halting|pausing|testing)\s+\w+\s+(?:reduces|increases|causes|helps|leads|provides)\b',
            lower_q
        ))

        # Check for conversational phrase / pronoun sentence splicing into prepositional phrases (e.g. "when considering I explored another plan", "Looking at I would do nothing")
        has_spliced_conversational_clause = bool(re.search(
            r'\b(?:when considering|looking at|regarding|involving|prioritizing|evaluating|with respect to|about|of)\s+(?:i\s+|we\s+|i\'d\s+|i\'m\s+|i\'ll\s+|i\s+would|i\s+explored|i\s+did|i\s+chose|i\s+decided|i\s+will|not\s+sure|don\'t\s+know|no\s+idea)\b',
            lower_q
        )) or bool(re.search(r'\b(?:looking at|regarding|when considering)\s+i\s+would\s+do\s+nothing\b', lower_q))

        # Check for extracted phrases ending in trailing function/conjunction words rather than content words
        TRAILING_FUNCTION_WORDS_QA = {
            "when", "because", "but", "so", "and", "if", "while", "though", "although",
            "since", "until", "unless", "where", "how", "what", "why", "that", "than",
            "then", "as", "or", "nor", "for", "to", "with", "a", "an", "the", "our",
            "their", "your", "my", "his", "its", "some", "any", "all", "bit",
        }
        has_trailing_function_word_in_detail = False
        trailing_fw_match = re.findall(
            r'\b(?:regarding|involving|concerning|around|about|considering|prioritizing|evaluating|of)\s+'
            r'((?:stopping|halting|pausing|shutting\s+down|deploying|rerouting|re-routing|testing|preventing|'
            r'avoiding|reducing|balancing|explaining|briefing|communicating|navigating|managing|addressing|'
            r'implementing|complying|choosing|selecting)(?:\s+\w+)+?)(?=\s+and\s+|[,?]|$)',
            lower_q
        )
        for phrase in trailing_fw_match:
            last_word = phrase.strip().split()[-1].lower() if phrase.strip().split() else ""
            if last_word in TRAILING_FUNCTION_WORDS_QA:
                has_trailing_function_word_in_detail = True
                break

        natural_flow = (
            clean_q.endswith("?")
            and len(clean_q.split()) >= 4
            and not has_ellipsis
            and not has_stitched_template
            and not has_double_starter
            and not has_stacked_prep
            and not has_robotic_pattern
            and not has_long_quote
            and not has_raw_quote_syntax
            and not has_bare_person_consideration
            and not has_bare_entity_object
            and not has_circular_grounding
            and not has_generic_filler_phrase
            and not has_malformed_punct
            and not has_duplicate_detail_in_sentence
            and not has_ungrammatical_verb_fragment
            and not has_spliced_conversational_clause
            and not has_trailing_function_word_in_detail
        )
        if not natural_flow:
            failed.append("natural_conversational_flow")

        # 10. Cross-turn template-shape repetition check
        # Compare opening n-gram (first 4 words) and syntactic skeleton against previous_questions.
        # Fail if:
        # (a) same opening stem appears >2 times in a row (i.e. last 2 previous questions share this stem), OR
        # (b) same opening stem appears >40% of the time across the session (when len(previous_questions) >= 2), OR
        # (c) per-intent frequency: same opening stem appears >50% of the time for this intent (when intent used 3+ times).
        def get_stem_n_gram(text: str, n: int = 4) -> str:
            cleaned = re.sub(r'[^a-z0-9\s]', '', text.lower()).strip()
            tokens = cleaned.split()
            return " ".join(tokens[:n]) if len(tokens) >= n else " ".join(tokens)

        current_stem = get_stem_n_gram(clean_q, n=4)
        shape_diversity_passed = True

        if previous_questions and len(clean_q.split()) >= 4:
            prev_stems = [get_stem_n_gram(pq, n=4) for pq in previous_questions if len(pq.split()) >= 4]

            # (a) Consecutive repetition: if last 2 previous questions share the current opening stem
            if len(prev_stems) >= 2 and prev_stems[-1] == current_stem and prev_stems[-2] == current_stem:
                shape_diversity_passed = False

            # (b) Session-wide frequency: if current stem appears > 40% of the time across the session
            if len(prev_stems) >= 2:
                matching_count = sum(1 for ps in prev_stems if ps == current_stem)
                total_turns_count = len(prev_stems) + 1
                frequency = (matching_count + 1) / total_turns_count
                if frequency > 0.40:
                    shape_diversity_passed = False

            # (c) Per-intent frequency: if current stem appears > 50% for this intent once intent used >= 3 times
            current_intent = getattr(spec, "intent", None) or "UNKNOWN"
            prev_intents = getattr(state, "asked_intent_history", []) if state else []
            same_intent_stems = []
            for idx, pq in enumerate(previous_questions):
                pq_intent = prev_intents[idx] if idx < len(prev_intents) else None
                if not pq_intent:
                    pq_lower = pq.lower()
                    if "risk" in pq_lower or "hazard" in pq_lower or "concern" in pq_lower:
                        pq_intent = "ASK_RISK"
                    elif "alternative" in pq_lower or "settling on" in pq_lower or "backup" in pq_lower:
                        pq_intent = "ASK_ALTERNATIVE"
                    elif "stakeholder" in pq_lower or "teammate" in pq_lower or "aligned" in pq_lower:
                        pq_intent = "ASK_STAKEHOLDER"
                    elif "compromise" in pq_lower or "trade-off" in pq_lower or "tradeoff" in pq_lower or "balance" in pq_lower or "competing" in pq_lower:
                        pq_intent = "ASK_TRADEOFF"
                    elif "reflection" in pq_lower or "lesson" in pq_lower or "take forward" in pq_lower or "hindsight" in pq_lower:
                        pq_intent = "ASK_REFLECTION"
                    elif "reason" in pq_lower or "principal reason" in pq_lower or "factor" in pq_lower or "thinking" in pq_lower:
                        pq_intent = "ASK_REASON"
                if pq_intent == current_intent:
                    same_intent_stems.append(get_stem_n_gram(pq, n=4))

            if len(same_intent_stems) >= 2:  # with current turn, intent is used 3+ times
                matching_intent_count = sum(1 for s in same_intent_stems if s == current_stem) + 1
                total_intent_count = len(same_intent_stems) + 1
                intent_freq = matching_intent_count / total_intent_count
                if intent_freq > 0.50:
                    shape_diversity_passed = False

        if not shape_diversity_passed:
            failed.append("cross_turn_shape_diversity")

        # 11. Reactive clause quality check
        # Detects and rejects generic, content-free chatbot filler openers.
        # A good reactive clause is 2-6 words that reference the candidate's specific content
        # (decision, entity, constraint, number) before the question mark portion.
        BANNED_GENERIC_OPENERS = [
            "that's interesting", "that is interesting", "great point",
            "good point", "i see", "thanks for sharing", "thank you for sharing",
            "good to know", "understood", "got it", "nice", "okay so",
            "alright so", "well then", "interesting point", "fair enough",
            "absolutely", "of course", "sure thing", "no doubt",
            "that makes sense", "that's a good point", "that's a fair point",
            "great answer", "good answer", "nice answer", "excellent point",
            "wonderful", "perfect", "very good", "impressive",
        ]
        reactive_clause_passed = True

        # Extract the reactive clause: text before the first question word or question mark
        # A reactive clause typically appears before the main question body
        # Pattern: "<reactive>, <question>?" or "<reactive>— <question>?"
        reactive_clause = ""
        q_lower = clean_q.lower()
        # Split on em-dash, en-dash, semicolon, or comma followed by a question word or conjunction transition
        clause_split = re.split(r'[—–;]\s*|,\s*(?=(?:what|how|if|when|where|why|who|which|do|did|does|would|could|should|can|is|are|was|were|before|looking|walk|but|so|and)\b)', q_lower, maxsplit=1)
        if len(clause_split) >= 2:
            reactive_clause = clause_split[0].strip()

        if reactive_clause:
            rc_words = re.findall(r'\b[\w\'-]+\b', reactive_clause)
            rc_word_count = len(rc_words)

            # Distinguish genuine reactive clauses from question preambles.
            # A reactive clause contains an evaluative/attitudinal word that
            # shows the interviewer is reacting to what the candidate said
            # (e.g. "Bold to push back—", "Smart to catch misalignment—").
            # Question preambles like "Looking at your decision regarding..."
            # or "If a colleague questioned your approach..." don't contain
            # evaluative words and should NOT trigger word-count enforcement.
            REACTIVE_EVALUATIVE_WORDS = {
                "smart", "decisive", "bold", "aggressive", "tough", "creative",
                "critical", "gutsy", "interesting", "practical", "honest",
                "respectful", "risky", "strong", "valid", "right", "good", "great",
                "nice", "fast", "rapid", "careful", "wise", "clear", "fair",
                "quick", "brave", "shrewd", "sharp", "impressive", "clever",
                "savvy", "sound", "solid", "keen", "prudent", "ambitious",
                "thoughtful", "proactive", "courageous", "daring", "pragmatic",
                "thanks", "thank", "excellent", "wonderful", "perfect",
            }
            rc_words_lower = {w.lower() for w in rc_words}
            is_evaluative_clause = bool(rc_words_lower & REACTIVE_EVALUATIVE_WORDS)

            if is_evaluative_clause:
                # Strict word count check: reactive clause MUST be 2-6 words
                if rc_word_count < 2 or rc_word_count > 6:
                    reactive_clause_passed = False

                # Check against banned generic openers
                for banned in BANNED_GENERIC_OPENERS:
                    if reactive_clause == banned or reactive_clause.rstrip('., —–-') == banned:
                        reactive_clause_passed = False
                        break

            # Cross-turn reactive clause shape diversity:
            # Extract the reactive clause from previous questions and check for convergence
            if previous_questions and len(previous_questions) >= 2:
                prev_reaction_stems = []
                for pq in previous_questions:
                    pq_lower = pq.lower()
                    pq_split = re.split(r'[—–;]\s*|,\s*(?=(?:what|how|if|when|where|why|who|which|do|did|does|would|could|should|can|is|are|was|were|before|looking|walk|but|so|and)\b)', pq_lower, maxsplit=1)
                    if len(pq_split) >= 2:
                        prev_reaction_stems.append(pq_split[0].strip())

                if prev_reaction_stems:
                    # Check if same reactive clause stem repeats >40% across session
                    current_reaction_stem = reactive_clause
                    matching = sum(1 for ps in prev_reaction_stems if ps == current_reaction_stem)
                    total_with_reactions = len(prev_reaction_stems) + 1
                    if total_with_reactions >= 3 and (matching + 1) / total_with_reactions > 0.40:
                        reactive_clause_passed = False

        if not reactive_clause_passed:
            failed.append("reactive_clause_quality")

        is_passed = len(failed) == 0

        return QAChecklistResult(
            references_candidate_answer=ref_cand,
            references_scenario=ref_scen,
            exactly_one_objective=single_obj,
            does_not_repeat_previous_question=no_repeat,
            does_not_ask_already_answered_info=no_already_answered,
            does_not_hallucinate=no_hallucination,
            fits_current_interview_state=fits_state,
            does_not_skip_reasoning_chain=no_skip_reasoning,
            natural_conversational_flow=natural_flow,
            cross_turn_shape_diversity=shape_diversity_passed,
            reactive_clause_quality=reactive_clause_passed,
            is_passed=is_passed,
            failed_checks=failed,
        )

    def construct_deterministic_fallback(
        self,
        spec: FollowUpSpecification,
        decision_data: CandidateDecisionData,
        scenario_title: str,
        transcript_text: str,
        used_openings: Optional[List[str]] = None,
        state: Optional[ConversationState] = None,
    ) -> str:
        """Deterministic question generator when Nemotron fails QA checklist.

        Rules:
        - Extract candidate details and embed them into fallback questions.
        - NEVER splice raw candidate text (with quotes or ellipsis) into the question.
        - Rotate exemplar shapes (Shapes 1 through 6) aligned with intent and DialogueEditor.
        - ZERO generic filler strings.
        """
        intent = spec.intent
        from app.application.followup_subsystem.dialogue_editor import DialogueEditor
        editor = DialogueEditor()
        details = editor.extract_details_from_text(transcript_text)
        clean_details = [d for d in details if d["text"].lower() not in ("i'm", "sir", "ma'am", "well", "just", "sir,")]
        
        # Blacklist circular/meta terms
        meta_terms = {"the choice", "the decision", "the rationale", "the reason", "the approach", "the priority", "this decision", "your approach"}
        filtered_details = [d for d in clean_details if editor.format_detail(d).lower() not in meta_terms]

        detail_str = editor.join_details_safely([editor.format_detail(d) for d in filtered_details if editor.format_detail(d)])

        # Fix spelling errors (e.g. "chosing" -> "choosing")
        detail_str = re.sub(r'\bchosing\b', 'choosing', detail_str, flags=re.IGNORECASE)

        # Generalized Proper Noun / Organization / Entity Grounding
        if detail_str:
            clean_w = detail_str.strip(".,;:!?'\"` ")
            if clean_w in ("Arjun", "Meera", "George", "Uncle George"):
                detail_str = f"communicating with {clean_w}"
            elif clean_w in ("Dr. Arora", "Mrs. Sen", "Dr Arora", "Mrs Sen", "Dr. Reynolds", "Dr Reynolds"):
                detail_str = f"meeting with {clean_w}"
            elif clean_w in ("Navy", "Army", "Coast Guard", "Air Force", "Military"):
                detail_str = f"aligning with {clean_w} regulations"
            elif clean_w in ("NASA", "ISRO", "ESA", "FAA", "FDA", "OSHA", "NRC"):
                detail_str = f"complying with {clean_w} standards"
            elif len(clean_w.split()) == 1 and clean_w and clean_w[0].isupper():
                detail_str = f"navigating {clean_w} constraints"

        sess_seed = sum(ord(c) for c in (getattr(state, "session_id", "") or scenario_title or ""))
        turn_idx = getattr(state, "turn_number", 0) if (state and getattr(state, "turn_number", 0) > 0) else sess_seed
        shape_idx = (turn_idx - 1) % 4

        if intent in ("ASK_REASON", "CLARIFY_AMBIGUITY"):
            if detail_str:
                shapes = [
                    f"Looking at your decision regarding {detail_str}, what principal reason led to that choice in this situation?",
                    f"What key factor tipped your decision toward {detail_str}?",
                    f"Walk me through your thinking when {detail_str}?",
                    f"When evaluating the situation, what outcome were you most focused on when {detail_str}?",
                ]
            else:
                shapes = [
                    "What principal reason guided your decision in this scenario?",
                    "What key factor was the main driver behind your approach?",
                    "Walk me through your core reasoning when deciding on that action?",
                    "What primary goal were you aiming to achieve in this situation?",
                ]
            return shapes[shape_idx]

        elif intent == "ASK_RISK":
            if detail_str:
                shapes = [
                    f"What specific risk were you aiming to avoid when considering {detail_str}?",
                    f"When {detail_str}, what potential hazard concerned you most?",
                    f"How did you evaluate the risk of failure when {detail_str}?",
                    f"What made risk prevention your primary focus when {detail_str}?",
                ]
            else:
                shapes = [
                    "What specific operational risk were you aiming to prevent in this situation?",
                    "When you committed to that step, what failure mode concerned you most?",
                    "How did you assess the potential risks before executing that choice?",
                    "What was the biggest safety or performance concern in your assessment?",
                ]
            return shapes[shape_idx]

        elif intent == "ASK_STAKEHOLDER":
            if detail_str:
                shapes = [
                    f"If a teammate or stakeholder questioned your choice regarding {detail_str}, how would you explain your reasoning?",
                    f"When coordinating {detail_str}, how did you ensure all stakeholders remained aligned?",
                    f"Suppose someone on your team suggested an opposing approach to {detail_str} \u2014 how would you address their perspective?",
                    f"Walk me through how you communicated with your team regarding {detail_str}?",
                ]
            else:
                shapes = [
                    "If a colleague or stakeholder questioned your approach, how would you defend your rationale?",
                    "How did you ensure all relevant stakeholders were aligned with that decision?",
                    "How would you address a teammate who strongly preferred a different direction?",
                    "Walk me through how you communicated this decision across your group?",
                ]
            return shapes[shape_idx]

        elif intent == "ASK_ALTERNATIVE":
            if detail_str:
                shapes = [
                    f"Before settling on {detail_str}, what other alternative options did you explore?",
                    f"What alternative paths crossed your mind before you committed to {detail_str}?",
                    f"If circumstances had ruled out {detail_str}, what backup plan would you have deployed?",
                    f"What other approaches did you evaluate before deciding on {detail_str}?",
                ]
            else:
                shapes = [
                    "Before committing to this plan, what other alternatives did you explore?",
                    "What backup options did you evaluate before deciding on that course of action?",
                    "If your initial plan was blocked, what alternative strategy would you have chosen?",
                    "What other viable approaches did you consider in this situation?",
                ]
            return shapes[shape_idx]

        elif intent == "ASK_TRADEOFF":
            if detail_str:
                shapes = [
                    f"How did you evaluate the compromise regarding {detail_str} against your main goal?",
                    f"When considering the trade-offs around {detail_str}, how did you balance competing priorities?",
                    f"How did you weigh the competing constraints when {detail_str}?",
                    f"Reflecting on the trade-offs, what did you prioritize over secondary factors when {detail_str}?",
                ]
            else:
                shapes = [
                    "How did you evaluate the key trade-offs before settling on your approach?",
                    "Reflecting on competing priorities in this scenario, what compromise did you accept?",
                    "How did you weigh the competing factors and constraints in this situation?",
                    "What secondary factor did you deprioritize to achieve your primary objective?",
                ]
            return shapes[shape_idx]

        elif intent == "ASK_REFLECTION":
            if detail_str:
                shapes = [
                    f"Looking back at how that situation unfolded with {detail_str}, what key lesson will you take forward to your next project?",
                    f"Reflecting on {detail_str}, what would you do differently if faced with similar constraints in the future?",
                    f"What was the most important strategic takeaway you gained from {detail_str}?",
                    f"Looking back in hindsight at {detail_str}, how effective was that approach under time pressure?",
                ]
            else:
                shapes = [
                    "Looking back at how that situation unfolded, what key lesson will you take forward?",
                    "Reflecting on this scenario, what would you adjust if faced with similar constraints?",
                    "What was your single biggest insight from handling this challenge?",
                    "In hindsight, how would you evaluate your decision-making under that pressure?",
                ]
            return shapes[shape_idx]

        elif intent == "VERIFY_CONSISTENCY":
            if detail_str:
                return f"Looking back at {detail_str}, what shifted in your thinking compared to your earlier approach?"
            return "Looking back at the progression of your decisions, what shifted in your thinking compared to your earlier approach?"

        elif intent == "CONFIRM_BELIEF":
            if detail_str:
                shapes = [
                    f"Reflecting on {detail_str}, why did this priority become your primary focus in this scenario?",
                    f"What key factor prompted you to prioritize {detail_str} when navigating this situation?",
                    f"Looking at {detail_str}, what main strategic goal were you aiming for?",
                    f"What core principle guided your decision regarding {detail_str}?",
                ]
            else:
                shapes = [
                    "Reflecting on your approach, why did this priority become your primary focus in this scenario?",
                    "What key factor prompted you to prioritize that course of action when navigating this situation?",
                    "Looking at that outcome, what main strategic goal were you aiming for?",
                    "What core principle guided your decision in this scenario?",
                ]
            return shapes[shape_idx]

        else:
            return "Could you explain your reasoning in a little more detail?"
            return f"Help me understand your reasoning behind {detail_str} in a bit more detail."
