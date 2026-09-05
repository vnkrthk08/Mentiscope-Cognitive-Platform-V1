from typing import Dict, Optional
from app.infrastructure.prompt_service.template import PromptTemplate
from app.domain.exceptions.prompt_exceptions import PromptNotFound


class PromptRepository:
    """Manages prompt template storage, lookup, and version retrieval."""

    def __init__(self):
        self._templates: Dict[str, Dict[str, PromptTemplate]] = {}
        self._register_default_templates()

    def _register_default_templates(self):
        # 1. Evidence Extraction Prompt Template v1.0.0
        tmpl_evidence = PromptTemplate(
            prompt_id="EVIDENCE_EXTRACTION_PROMPT",
            version="1.0.0",
            description="Extracts verbatim quotes and behavioral indicators from speaking transcripts.",
            prompt_type="EXTRACTION",
            template_text=(
                "You are an expert cognitive evidence extractor for scenario '{scenario_title}'.\n"
                "Analyze the following candidate speaking response transcript:\n"
                "'''\n{transcript_text}\n'''\n"
                "Extract observable evidence for construct: {construct_name}.\n"
                "Strictly follow these rules:\n"
                "1. Identify decisions, reasoning, leadership statements, communication behaviors, and emotional regulation evidence.\n"
                "2. Extract supporting verbatim quotes.\n"
                "3. Do NOT calculate scores or percentages. Scoring is handled deterministically by Mentiscope algorithms. Your output is evidence only.\n"
                "4. If the transcript contains only invalid or insufficient responses (e.g., 'hello', 'yes', 'abc', 'I don't know') across attempts, do NOT fabricate evidence. Return empty arrays for verbatim_quotes and behavioral_indicators, and a low confidence_score (e.g., less than 0.1).\n"
                "Return JSON matching the schema."
            ),
            required_variables=["scenario_title", "transcript_text", "construct_name"],
            output_schema={
                "type": "object",
                "required": ["verbatim_quotes", "behavioral_indicators", "confidence_score"],
                "properties": {
                    "verbatim_quotes": {"type": "array"},
                    "behavioral_indicators": {"type": "array"},
                    "confidence_score": {"type": "number"},
                },
            },
        )
        self.register_template(tmpl_evidence)

        # 2. Interview Understanding Prompt Template v15.0.0 (AIIS Module 2)
        tmpl_understanding = PromptTemplate(
            prompt_id="INTERVIEW_UNDERSTANDING_PROMPT",
            version="15.0.0",
            description="Evaluates candidate response status, extracts decision elements, assesses coverage, and identifies conversation signals.",
            prompt_type="UNDERSTANDING",
            template_text=(
                "You are the Interview Understanding Engine for scenario '{scenario_title}'.\n"
                "Analyze the candidate's response in context of the scenario and conversation history.\n\n"
                "SCENARIO: '{scenario_title}'\n"
                "CONVERSATION HISTORY:\n{conversation_history}\n"
                "CANDIDATE RESPONSE: '{transcript_text}'\n\n"
                "DIRECTIVES:\n"
                "1. CLASSIFY RESPONSE: Exactly 1 status: VALID, PARTIALLY_VALID, TOO_SHORT, OFF_TOPIC, NONSENSICAL, UNCERTAIN, REFUSAL, REPETITIVE, CONTRADICTORY.\n"
                "2. EXTRACT DECISION: Extract verbatim or null for: action, reason, stakeholders (list), risks (list), alternatives (list), tradeoffs (list), reflection.\n"
                "3. COVERAGE: Set boolean for decision, reason, risk, stakeholder, alternative, tradeoff, reflection.\n"
                "4. SIGNALS: Set boolean for repetitive, contradiction, off_topic.\n"
                "Do NOT hallucinate. Unstated fields MUST remain null or empty.\n"
                "Return JSON matching output schema."
            ),
            required_variables=["scenario_title", "transcript_text", "conversation_history"],
            output_schema={
                "type": "object",
                "required": ["status", "confidence", "candidate_decision", "coverage", "conversation"],
                "properties": {
                    "status": {"type": "string"},
                    "confidence": {"type": "number"},
                    "candidate_decision": {"type": "object"},
                    "coverage": {"type": "object"},
                    "conversation": {"type": "object"},
                },
            },
        )
        self.register_template(tmpl_understanding)

        # 3. Adaptive Follow-up Question Writer Prompt Template v16.0.0 (AIIS Module 8)
        tmpl_followup = PromptTemplate(
            prompt_id="ADAPTIVE_FOLLOWUP_PROMPT",
            version="16.0.0",
            description="Converts FollowUpSpecification into a natural English question with an earned, content-grounded reactive clause (2-6 words) before asking the objective question.",
            prompt_type="ADAPTIVE",
            template_text=(
                "You are an expert, authentic human interviewer conducting an adaptive psychometric assessment with a secondary student.\n\n"
                "SCENARIO CONTEXT & FULL SITUATION:\n"
                "- Scenario Title: '{scenario_title}'\n"
                "- Full Scenario Narrative & Details: {scenario_text}\n"
                "- Scenario Background & Stakes: {scenario_background_stakes}\n"
                "- Candidate's Stated Response (ASR Transcript): '{transcript_text}'\n"
                "- Active Objective (Target Construct): '{target_construct}'\n"
                "- Follow-up Specification: {followup_specification}\n"
                "- Conversation History:\n{conversation_history}\n\n"
                "PSYCHOLOGICAL RATIONALE & INTERVIEWER PERSONA:\n"
                "Your objective is to evaluate the student's authentic cognitive and behavioral capabilities under realistic problem-solving conditions. "
                "Real interviewers do NOT ask 100% sterile questions without acknowledging what the candidate just said. They open with a brief (2–6 word) "
                "earned reactive clause tied directly to the candidate's specific decision, stance, or constraint, followed immediately by exactly one focused question.\n\n"
                "STRICT INTERVIEWING RULES:\n"
                "1. OPEN WITH A BRIEF, CONTENT-GROUNDED REACTIVE CLAUSE (2-6 words):\n"
                "   - Acknowledge the candidate's specific content naturally before asking your question.\n"
                "   - Vary your reaction tone across turns: agreement ('Right, safety first, but—', 'Makes sense given the deadline,'), "
                "mild challenge/skepticism ('A risky speed reduction, though—', 'Bold to stand firm there—', 'Tough call on the budget,'), "
                "curiosity/probing ('Interesting shift in strategy,', 'Fair point on the telemetry, but'), or neutral analytical acknowledgment ('With the reading at 12 NTU,', 'Looking at those trade-offs,').\n"
                "   - Transition cleanly using a comma, dash (—), or hyphen into the question.\n"
                "2. STRICTLY BAN CHATBOT FILLER OPENERS: NEVER start with generic, content-free bot filler like 'That's interesting', 'Great point', 'I see', 'Thanks for sharing', 'Good to know', or 'Understood'. The reaction must be earned by specific candidate content.\n"
                "3. ALIGN WITH ACTIVE OBJECTIVE: Land on exactly one clear, focused question with the required objective dimension ('risk', 'alternative', 'tradeoff', 'priority', 'reason', 'stakeholder', 'lesson').\n"
                "4. ASK EXACTLY ONE FOCUSED OBJECTIVE: Never ask compound or multi-sentence questions. Keep the total output concise and punchy.\n"
                "5. ZERO ROBOTIC CONNECTOR PATTERNS: Never use formulas like 'regarding your approach to', 'when considering X and Y', 'you mentioned your decision to', or long verbatim quotes spliced with ellipses.\n\n"
                "FEW-SHOT INTERVIEWER EXEMPLARS (VARIED REACTION TONES + FOCUSED OBJECTIVES):\n"
                "- Exemplar 1 (Agreement Tone — Short/Blunt Decision 'Safety regulations are non-negotiable.') [Intent: ASK_RISK]:\n"
                "  Interviewer: 'Right, safety first, but what specific hazard were you most concerned about if the pack overheated?'\n\n"
                "- Exemplar 2 (Mild Skepticism / Challenge — Speed vs Safety Compromise 'I cut motor current by 25% so the circuit stays cool.') [Intent: ASK_TRADEOFF]:\n"
                "  Interviewer: 'A risky speed reduction, though—how did you balance that 25% loss against finishing before the clock ran out?'\n\n"
                "- Exemplar 3 (Curiosity / Probing Tone — Team Disagreement 'When Arjun pushed to continue, I showed him the thermal data.') [Intent: ASK_STAKEHOLDER]:\n"
                "  Interviewer: 'Fair point on the telemetry, but how would you have handled things if Arjun still refused to accept the sensor readings?'\n\n"
                "- Exemplar 4 (Neutral Analytical Acknowledgment — Component Choice 'We picked the standard acrylic mount to keep costs low.') [Intent: ASK_ALTERNATIVE]:\n"
                "  Interviewer: 'Makes sense given the budget, but before settling on the acrylic mount, what other alternative materials did you evaluate?'\n\n"
                "- Exemplar 5 (Mild Pushback on Ethical / Management Stance 'Even with management pressure, I refused to falsify the report.') [Intent: CONFIRM_BELIEF / ASK_REASON]:\n"
                "  Interviewer: 'Bold to stand firm against management—what core principle made speaking up non-negotiable for you?'\n\n"
                "- Exemplar 6 (Reflective & Forward-Looking — Post-Incident Adaptation 'Next time we will install active heat sinks.') [Intent: ASK_REFLECTION]:\n"
                "  Interviewer: 'A smart design adjustment—looking back at this incident, what key lesson will shape your future rover architecture?'\n\n"
                "Format response as strict JSON matching the output schema."
            ),
            required_variables=[
                "scenario_title",
                "scenario_text",
                "scenario_background_stakes",
                "transcript_text",
                "target_construct",
                "conversation_history",
                "current_assessment_state",
                "behavior_evidence"
            ],
            output_schema={
                "type": "object",
                "required": [
                    "internal_reasoning",
                    "answer_quality",
                    "intent",
                    "is_relevant",
                    "needs_clarification",
                    "follow_up_question",
                    "behavioral_evidence"
                ],
                "properties": {
                    "internal_reasoning": {"type": "string"},
                    "answer_quality": {"type": "string"},
                    "intent": {"type": "string"},
                    "is_relevant": {"type": "boolean"},
                    "needs_clarification": {"type": "boolean"},
                    "follow_up_question": {"type": "string"},
                    "behavioral_evidence": {"type": "array"}
                },
            },
        )
        self.register_template(tmpl_followup)

        # 3b. Evidence Extraction Prompt Template v1.0.0 (Adaptive Follow-up Stage 1)
        tmpl_adaptive_extraction = PromptTemplate(
            prompt_id="ADAPTIVE_EVIDENCE_EXTRACTION_PROMPT",
            version="1.0.0",
            description="Extracts structured evidence items (claims, reasoning, assumptions, hedges, contradictions) from a candidate response.",
            prompt_type="EXTRACTION",
            template_text=(
                "You are a psychometric evidence extraction engine. Your task is to analyze the candidate's latest response in an assessment scenario.\n\n"
                "SCENARIO TITLE: '{scenario_title}'\n"
                "PRIOR TURN EVIDENCE LOG:\n{prior_evidence_log}\n"
                "CANDIDATE LATEST RESPONSE: '{candidate_response}'\n\n"
                "DIRECTIVES:\n"
                "Extract structured facts, reasoning, assumptions, hedges, and contradictions from the latest response only. Be strictly construct-agnostic — describe what was said, not what psychological construct it implies.\n\n"
                "1. CLAIMS: Specific explicit statements of action, decision, choice, or factual assertions made by the candidate.\n"
                "2. REASONING_SHOWN: Explicit logic, justifications, explanations, or trade-off rationales offered by the candidate.\n"
                "3. ASSUMPTIONS: Unstated or explicit background premises the candidate relies upon.\n"
                "4. HEDGES_OR_CONFIDENCE_MARKERS: Words or phrases showing hesitation, uncertainty, or high confidence (e.g., 'maybe', 'I think', 'definitely', 'probably').\n"
                "5. CONTRADICTIONS_WITH_PRIOR_TURNS: Direct contradictions between claims in the latest response vs prior turn evidence log. If none, return empty list [].\n\n"
                "Do NOT fabricate or extrapolate. Return strict JSON matching output schema."
            ),
            required_variables=["scenario_title", "candidate_response", "prior_evidence_log"],
            output_schema={
                "type": "object",
                "required": ["claims", "reasoning_shown", "assumptions", "hedges_or_confidence_markers", "contradictions_with_prior_turns"],
                "properties": {
                    "claims": {"type": "array", "items": {"type": "string"}},
                    "reasoning_shown": {"type": "array", "items": {"type": "string"}},
                    "assumptions": {"type": "array", "items": {"type": "string"}},
                    "hedges_or_confidence_markers": {"type": "array", "items": {"type": "string"}},
                    "contradictions_with_prior_turns": {"type": "array", "items": {"type": "string"}},
                },
            },
        )
        self.register_template(tmpl_adaptive_extraction)

        # 3. Construct Evaluation Prompt Template v1.0.0
        tmpl_construct = PromptTemplate(
            prompt_id="CONSTRUCT_EVALUATION_PROMPT",
            version="1.0.0",
            description="Evaluates psychological constructs based on aggregated behavioral evidence items.",
            prompt_type="EVALUATION",
            template_text=(
                "Evaluate psychological construct '{construct_name}' for scenario '{scenario_title}'.\n"
                "Evidence Summary:\n{evidence_summary}\n"
                "Return structured JSON matching schema."
            ),
            required_variables=["scenario_title", "construct_name", "evidence_summary"],
            output_schema={
                "type": "object",
                "required": ["construct_evaluations"],
                "properties": {
                    "construct_evaluations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["construct", "behavioral_summary", "evaluation_narrative", "confidence"],
                            "properties": {
                                "construct": {"type": "string"},
                                "behavioral_summary": {"type": "string"},
                                "evaluation_narrative": {"type": "string"},
                                "confidence": {"type": "number"},
                            },
                        },
                    }
                },
            },
        )
        self.register_template(tmpl_construct)

        # 4. Scenario Generation Prompt Template v1.0.0
        tmpl_scengen = PromptTemplate(
            prompt_id="SCENARIO_GENERATION_PROMPT",
            version="1.0.0",
            description="Generates a complete psychometric assessment scenario based on planning blueprint metadata.",
            prompt_type="GENERATION",
            template_text=(
                "You are an expert psychometric assessment narrative expander.\n"
                "The supplied Assessment Specification is AUTHORITATIVE. Your task is to expand the specification into fluent, highly realistic natural English.\n\n"
                "AUTHORITATIVE ASSESSMENT SPECIFICATION:\n"
                "- Assessment Specification: {assessment_specification}\n"
                "- Domain Theme: '{domain}'\n"
                "- Category: '{category}'\n"
                "- Subcategory: '{subcategory}'\n"
                "- Context Seed: '{context_seed}'\n"
                "- Scenario Grammar: '{scenario_grammar}'\n"
                "- Interaction Model: '{interaction_model}'\n\n"
                "PSYCHOMETRIC PARAMETERS:\n"
                "- Difficulty Level: '{difficulty}'\n"
                "- Listening Task Difficulty: '{listening_difficulty}'\n"
                "- Speaking Focus Construct: '{speaking_focus}'\n"
                "- Primary constructs to assess: {primary_constructs}\n"
                "- Secondary constructs to assess: {secondary_constructs}\n"
                "- Listening Narration word count range: {narration_length_min} to {narration_length_max} words\n"
                "- Expected Speaking response time: {expected_speaking_duration_seconds} seconds\n"
                "- Language Level: '{language_level}'\n\n"
                "AUTHORITATIVE EXPANDER DIRECTIVES:\n"
                "1. AUTHORITATIVE SPECIFICATION: Do NOT invent new objectives, new stakeholders, new trigger events, or new constraints. Elaborate the supplied NarrativeBeats into a 4-paragraph narration.\n"
                "2. EXACT LISTENING CONSTRUCT COVERAGE & ZERO DUPLICATES:\n"
                "   Construct exactly 4 Listening Questions. Each question must target EXACTLY ONE of the following 4 constructs with NO duplicates across the 4 questions:\n"
                "   - Question 1 (Working Memory): Verbatim recall of a specific fact, number, or detail explicitly stated in the narration.\n"
                "   - Question 2 (Attention): Correct identification of a detail requiring focused listening (something easy to mishear, a distractor mentioned only once, or a subtle distinction between two similar stated facts).\n"
                "   - Question 3 (Listening Comprehension): Understanding of overall meaning and narrative logic; must NOT be answerable from a single isolated sentence.\n"
                "   - Question 4 (Reasoning): A conclusion or inference NOT explicitly stated, requiring synthesis of two or more parts of the narration.\n\n"
                "3. HARD RULE - NO FRAMEWORK LEAKAGE:\n"
                "   A listening question must NEVER name or ask about cognitive constructs, psychometric abilities, scoring criteria, or internal assessment framework elements (e.g. 'Which cognitive construct is evaluated by...'). Every question MUST be answerable purely from the scenario narration content itself.\n\n"
                "4. DISTRACTOR DESIGN & OPTION-BALANCING REQUIREMENTS:\n"
                "   - All four answer choices must have comparable length, grammatical structure, specificity, and level of detail. The correct answer must not be identifiable because it is longer, more detailed, more qualified, or more precise than the distractors.\n"
                "   - Distractors must be plausible, scenario-grounded, and represent realistic misunderstandings (e.g., a mishearing of a similar figure, or a conclusion reached by missing one relevant detail) — NOT arbitrary, absurd, or artificially shortened answers.\n"
                "   - Do NOT use distractors that test ethical or behavioral judgment (e.g., 'blame teammates for the technical difficulty') — those belong to the Speaking module's behavioural constructs, not listening comprehension.\n"
                "   - Distribute the correct answer position randomly across indices 0, 1, 2, and 3.\n\n"
                "5. SPEAKING PROMPT STAGE ALIGNMENT: Construct exactly 3 Speaking Prompts following the 3 EDAPAF Stage specifications (Initial Decision, Adaptive Challenge, Reflective Probe).\n"
                "6. REALISM & FLUENCY: Elaborate all structural elements into fluent, natural English suitable for a Class 10-11 secondary student.\n\n"
                "REQUIRED SCENARIO STRUCTURE:\n"
                "1. A concise, engaging Scenario Title.\n"
                "2. A Scenario Description detailing the context/crisis.\n"
                "3. A Listening Narration paragraph to be read aloud (word count strictly within requested range).\n"
                "4. Exactly 4 Listening Questions (multiple choice). Each question object MUST include structured metadata:\n"
                "   - id, prompt, options (4 choices), correct_option_index (0-3)\n"
                "   - target_construct (Working Memory | Attention | Listening Comprehension | Reasoning)\n"
                "   - secondary_constructs (array of strings)\n"
                "   - question_type (Recall | Inference | Detail | Sequencing | Comprehension)\n"
                "   - cognitive_objective (string explaining synthesis/recall/attention required)\n"
                "   - difficulty (beginner | intermediate | advanced)\n"
                "   - expected_evidence (object with correct_answer_indicates and distractor_rationale map)\n"
                "   - weight (number, default 1.0), points (10), max_replays (2)\n"
                "5. Exactly 3 Speaking Prompts corresponding to the EDAPAF 3-stage guided conversation.\n\n"
                "Return a strict JSON object matching the output schema."
            ),
            required_variables=[
                "assessment_specification",
                "domain",
                "category",
                "subcategory",
                "context_seed",
                "scenario_grammar",
                "interaction_model",
                "difficulty",
                "listening_difficulty",
                "speaking_focus",
                "primary_constructs",
                "secondary_constructs",
                "narration_length_min",
                "narration_length_max",
                "expected_speaking_duration_seconds",
                "language_level",
            ],
            output_schema={
                "type": "object",
                "required": [
                    "title",
                    "description",
                    "listening_narration",
                    "listening_questions",
                    "speaking_prompts",
                    "construct_mappings",
                    "expected_behaviour_signals",
                ],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "listening_narration": {"type": "string"},
                    "listening_questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "id",
                                "prompt",
                                "options",
                                "correct_option_index",
                                "target_construct",
                                "secondary_constructs",
                                "question_type",
                                "cognitive_objective",
                                "difficulty",
                                "expected_evidence",
                                "weight",
                                "points",
                                "max_replays"
                            ],
                            "properties": {
                                "id": {"type": "string"},
                                "prompt": {"type": "string"},
                                "options": {"type": "array"},
                                "correct_option_index": {"type": "integer"},
                                "target_construct": {"type": "string"},
                                "secondary_constructs": {"type": "array"},
                                "question_type": {"type": "string"},
                                "cognitive_objective": {"type": "string"},
                                "difficulty": {"type": "string"},
                                "expected_evidence": {
                                    "type": "object",
                                    "required": ["correct_answer_indicates", "distractor_rationale"],
                                    "properties": {
                                        "correct_answer_indicates": {"type": "string"},
                                        "distractor_rationale": {"type": "object"}
                                    }
                                },
                                "weight": {"type": "number"},
                                "points": {"type": "integer"},
                                "max_replays": {"type": "integer"}
                            }
                        }
                    },
                    "speaking_prompts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["id", "title", "instructions", "max_time_seconds", "target_constructs", "followup_eligible"],
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                                "instructions": {"type": "string"},
                                "max_time_seconds": {"type": "integer"},
                                "target_constructs": {"type": "array"},
                                "followup_eligible": {"type": "boolean"}
                            }
                        }
                    },
                    "construct_mappings": {"type": "array"},
                    "expected_behaviour_signals": {"type": "string"}
                }
            }
        )
        self.register_template(tmpl_scengen)

    def register_template(self, template: PromptTemplate):
        if template.prompt_id not in self._templates:
            self._templates[template.prompt_id] = {}
        self._templates[template.prompt_id][template.version] = template

    def get_template(self, prompt_id: str, version: str = "1.0.0") -> PromptTemplate:
        versions = self._templates.get(prompt_id)
        if not versions:
            raise PromptNotFound(prompt_id, version)

        tmpl = versions.get(version)
        if not tmpl:
            # Fallback to latest available version
            latest_key = sorted(versions.keys())[-1]
            tmpl = versions[latest_key]
        return tmpl
