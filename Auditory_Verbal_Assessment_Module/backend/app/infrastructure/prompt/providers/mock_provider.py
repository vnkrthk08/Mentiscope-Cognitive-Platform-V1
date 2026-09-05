import json
import uuid
import time
import re
from typing import Dict, Any, List
from app.infrastructure.prompt.providers.base_provider import LLMProvider


class MockProvider(LLMProvider):
    """Fallback Mock LLM Provider class registered as 'mock' in LLMProviderRegistry."""

    def __init__(self, provider_name: str = "mock", default_model: str = "mock-llm-v1"):
        self._provider_name = provider_name
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return self._provider_name

    def health(self) -> bool:
        return True

    async def health_check(self) -> bool:
        return True

    def supported_models(self) -> List[str]:
        return [self.default_model, "mock-llm-v1"]

    def max_context_window(self, model_name: str) -> int:
        return 16384

    def estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        return 0.0

    async def generate(self, system_prompt: str = None, user_prompt: str = None, prompt_text: str = None, options: Dict[str, Any] = None) -> Dict[str, Any]:
        # Handle positional/keyword argument mismatches to bridge LLMProvider & ILLMProvider
        sys_p = system_prompt
        usr_p = user_prompt
        
        # If positional parameters are passed (prompt_text, options)
        if system_prompt is not None and user_prompt is None and isinstance(system_prompt, str):
            # This is likely APOS style: generate(prompt_text, options)
            sys_p = "You are a helpful assistant."
            usr_p = system_prompt
            if isinstance(prompt_text, dict):
                options = prompt_text
        elif prompt_text is not None:
            usr_p = prompt_text
            sys_p = system_prompt or "You are a helpful assistant."

        p_text = usr_p or ""
        
        # Determine prompt_id
        prompt_id = "UNKNOWN"
        if options:
            prompt_id = options.get("prompt_id", "UNKNOWN")
        elif "evidence" in p_text.lower():
            prompt_id = "EVIDENCE_EXTRACTION_PROMPT"
        elif "construct" in p_text.lower() or "evaluation" in p_text.lower():
            prompt_id = "CONSTRUCT_EVALUATION_PROMPT"
        elif "adaptive" in p_text.lower() or "follow" in p_text.lower():
            prompt_id = "ADAPTIVE_FOLLOWUP_PROMPT"

        # Simulates generic mock JSON or text responses
        if "behavioural indicators" in p_text.lower() or "psychometric scoring engine" in p_text.lower():
            # Dynamic indicator matching for SQ1/SQ2/SQ3
            import re
            ind_ids = re.findall(r"SQ\d_IND_\d", p_text)
            if not ind_ids:
                ind_ids = ["SQ1_IND_1", "SQ1_IND_2", "SQ1_IND_3", "SQ1_IND_4", "SQ1_IND_5"]
            unique_inds = list(dict.fromkeys(ind_ids))
            
            # Extract transcript from prompt
            cand_match = re.search(r'CANDIDATE TRANSCRIPT:\s*["\']?(.*?)["\']?\s*CANONICAL', p_text, re.DOTALL | re.IGNORECASE)
            transcript = cand_match.group(1).strip() if cand_match else p_text
            cand_lower = transcript.lower()
            words = transcript.split()
            word_count = len(words)
            
            mock_indicators = []
            for idx, i_id in enumerate(unique_inds):
                # Check for zero / silence
                if word_count == 0:
                    score_val = 0
                elif word_count < 4:
                    score_val = 1 if idx == 0 else 0
                elif "super interesting" in cand_lower or word_count < 8:
                    # Weak response
                    if "SQ1" in i_id:
                        score_val = 1 if (idx == 0 and any(v in cand_lower for v in ["choose", "decide", "re-route", "halt", "stop"])) else 0
                    elif "SQ2" in i_id:
                        score_val = 1 if (idx == 1 and any(v in cand_lower for v in ["adapt", "switch", "pivot", "reroute"])) else 0
                    else: # SQ3
                        score_val = 1 if (idx in (1, 4) and any(m in cand_lower for m in ["hindsight", "lesson", "principle", "learned"])) else 0
                else:
                    # Differentiated evaluation for rich responses based on specific construct cues
                    if "SQ1" in i_id:
                        # Decision Making: Clear choice, logical justification, consequence, alternative, action plan
                        if idx == 0: # Decision
                            score_val = 4 if any(v in cand_lower for v in ["decisively", "choose", "decide", "re-route", "select"]) else 3
                        elif idx == 1: # Justification
                            score_val = 4 if ("because" in cand_lower or "due to" in cand_lower or "in order to" in cand_lower) else 2
                        elif idx == 2: # Consequences
                            score_val = 3 if any(m in cand_lower for m in ["deadline", "risk", "disqualification", "consequence", "impact", "safety"]) else 1
                        elif idx == 3: # Alternatives
                            score_val = 4 if any(m in cand_lower for m in ["instead of", "rather than", "alternative", "option"]) else 2
                        elif idx == 4: # Action plan
                            score_val = 4 if any(m in cand_lower for m in ["execute", "plan", "roadmap", "ensures", "while executing"]) else 3
                        else:
                            score_val = 3
                    elif "SQ2" in i_id:
                        # Adaptability: Acknowledge complication, modify approach, prioritize constraint, explain rationale, feasible revised action
                        has_pivot = any(v in cand_lower for v in ["adapt", "switch", "pivot", "modify", "reroute", "re-route", "change", "adjust"])
                        has_comp = any(m in cand_lower for m in ["steep", "terrain", "broken", "temperature", "unexpected", "complication", "hill"])
                        if not has_pivot and not has_comp:
                            score_val = 1 if idx == 0 else 0
                        else:
                            if idx == 0: # Acknowledge complication
                                score_val = 4 if has_comp else 2
                            elif idx == 1: # Modifies approach
                                score_val = 4 if has_pivot else 1
                            elif idx == 2: # Prioritizes constraint
                                score_val = 3 if any(m in cand_lower for m in ["prioritize", "priority", "critical", "bottleneck", "flatter", "safe"]) else 2
                            elif idx == 3: # Explains rationale
                                score_val = 3 if any(c in cand_lower for c in ["because", "since", "due to", "in order to"]) else 2
                            elif idx == 4: # Feasible revised action
                                score_val = 4 if has_pivot and word_count >= 12 else 2
                            else:
                                score_val = 3
                    else: # SQ3
                        # Reflective Reasoning: Trade-offs, assumptions, ripple effects, hindsight improvements, transferable principles
                        has_retro = any(m in cand_lower for m in ["hindsight", "looking back", "assumption", "assumed", "lesson", "principle", "learned"])
                        if idx == 0: # Trade-offs
                            score_val = 3 if any(m in cand_lower for m in ["trade-off", "compromise", "rather than", "sacrifice", "balance", "instead of"]) else 2
                        elif idx == 1: # Assumptions
                            score_val = 4 if any(m in cand_lower for m in ["assumption", "assumed", "premise", "optimistic", "limitation", "flawed"]) else 2
                        elif idx == 2: # Ripple effects
                            score_val = 3 if any(m in cand_lower for m in ["consequence", "downstream", "stakeholder", "systemic", "timeline", "future"]) else 2
                        elif idx == 3: # Hindsight improvements
                            score_val = 3 if any(m in cand_lower for m in ["improve", "in hindsight", "better", "adjust", "optimize", "different"]) else 2
                        elif idx == 4: # Transferable principle
                            score_val = 4 if any(m in cand_lower for m in ["principle", "lesson", "always", "rule", "takeaway", "heuristic", "future operations"]) else 2
                        else:
                            score_val = 3

                score_val = min(4, max(0, score_val))
                mock_indicators.append({
                    "indicator_id": i_id,
                    "score": score_val,
                    "matched_anchor": f"Demonstrated evidence for anchor level {score_val}.",
                    "evidence_quote": transcript[:120] if transcript else "",
                    "rationale": f"Candidate demonstrated anchor level {score_val} behavioral evidence based on transcript analysis.",
                    "confidence": 0.92
                })
            mock_payload = {"indicators": mock_indicators}
        elif "evidence" in prompt_id.lower() or "extraction" in prompt_id.lower():

            mock_payload = {
                "verbatim_quotes": [
                    "Our team must prioritize safety protocols and address the logistics disruption immediately"
                ],
                "behavioral_indicators": [
                    "Initiated immediate emergency protocols",
                    "Prioritized human safety over cargo delays",
                ],
                "confidence_score": 0.94,
                "behaviors": [
                    {
                        "category": "Leadership",
                        "description": "Initiated immediate emergency protocols",
                        "quote": "Our team must prioritize safety protocols and address the logistics disruption immediately",
                        "start_word_index": 0,
                        "end_word_index": 10,
                        "start_time": 0.0,
                        "end_time": 5.0,
                        "confidence": 0.94,
                        "linked_constructs": ["Leadership"]
                    }
                ]
            }
        elif "construct" in prompt_id.lower() or "evaluation" in prompt_id.lower():
            mock_payload = {
                "construct_evaluations": [
                    {
                        "construct": "DECISION_MAKING",
                        "behavioral_summary": "Communicates decision rationale systematically under pressure.",
                        "evaluation_narrative": "Multiple evidence items consistently demonstrate ethical prioritization and structured problem-solving.",
                        "confidence": 0.95,
                    }
                ]
            }
        elif "understanding" in prompt_id.lower() or "INTERVIEW_UNDERSTANDING" in prompt_id:
            mock_payload = {
                "status": "VALID",
                "confidence": 0.96,
                "candidate_decision": {
                    "action": "Pause the experiment and inform the teacher immediately",
                    "reason": "Ensure safety and prevent hardware damage",
                    "stakeholders": ["Teacher", "Team members"],
                    "risks": ["Hardware damage", "Time delay"],
                    "alternatives": [],
                    "tradeoffs": ["Lose 10 minutes of presentation time"],
                    "reflection": None
                },
                "coverage": {
                    "decision": True,
                    "reason": True,
                    "risk": True,
                    "stakeholder": True,
                    "alternative": False,
                    "tradeoff": True,
                    "reflection": False
                },
                "conversation": {
                    "repetitive": False,
                    "contradiction": False,
                    "off_topic": False
                }
            }
        elif "follow_up" in prompt_id.lower() or "adaptive" in prompt_id.lower():
            t_text = (options.get("transcript_text") if isinstance(options, dict) else "") or p_text
            from app.application.followup_subsystem.dialogue_editor import DialogueEditor
            details = DialogueEditor().extract_details_from_text(t_text)
            detail_str = (" and ".join([d["text"] for d in details[:2]])) if details else "your approach"
            mock_q = f"Regarding {detail_str}, what specific risk were you aiming to avoid?"

            mock_payload = {
                "internal_reasoning": "Candidate provided a clear initial action. Probing risk awareness next.",
                "answer_quality": "GOOD",
                "intent": "ASK_RISK",
                "is_relevant": True,
                "needs_clarification": False,
                "follow_up_question": mock_q,
                "behavioral_evidence": [
                    {
                        "category": "Decision Making",
                        "quote": detail_str,
                        "confidence": 0.95
                    }
                ]
            }
        elif "scenario" in prompt_id.lower() or "generation" in prompt_id.lower() or "scen" in p_text.lower():
            domain = "School Science Exhibition"
            if "domain: '" in p_text.lower():
                try:
                    domain = p_text.split("domain: '")[1].split("'")[0]
                except Exception:
                    pass
            mock_payload = {
                "title": f"Crisis at the {domain}",
                "description": "An urgent coordination challenge has occurred that threatens the event deadline.",
                "listening_narration": "During soundcheck at 04:45 PM, fifteen minutes before parents enter the main auditorium, the central microphone amplifier malfunctioned. Uncle George reported that the backup acoustic speaker system takes 20 minutes to set up, but Meera wants to start the show on time using unamplified acoustic singing.",
                "listening_questions": [
                    {
                        "id": "L_Q1",
                        "prompt": "How long does Uncle George report the backup speaker system will take to set up?",
                        "options": ["10 minutes", "15 minutes", "20 minutes", "30 minutes"],
                        "correct_option_index": 2,
                        "target_construct": "Working Memory",
                        "secondary_constructs": ["Listening Comprehension"],
                        "question_type": "Recall",
                        "cognitive_objective": "Verbatim recall of exact setup duration mentioned in narration",
                        "difficulty": "intermediate",
                        "expected_evidence": {
                            "correct_answer_indicates": "Accurate verbatim recall of time figure 20 minutes",
                            "distractor_rationale": {"0": "Misremembered 10 minutes", "1": "Confused with 15 minutes setup time"}
                        },
                        "weight": 1.0,
                        "points": 10,
                        "max_replays": 2
                    },
                    {
                        "id": "L_Q2",
                        "prompt": "At what exact time did the central microphone amplifier malfunction during soundcheck?",
                        "options": ["04:15 PM", "04:30 PM", "04:45 PM", "05:00 PM"],
                        "correct_option_index": 2,
                        "target_construct": "Attention",
                        "secondary_constructs": ["Listening Comprehension"],
                        "question_type": "Detail",
                        "cognitive_objective": "Focused attention on specific timestamp detail easy to mishear",
                        "difficulty": "intermediate",
                        "expected_evidence": {
                            "correct_answer_indicates": "Focused attention on timestamp detail 04:45 PM",
                            "distractor_rationale": {"0": "Misheard 04:15 PM", "1": "Confused with 04:30 PM"}
                        },
                        "weight": 1.0,
                        "points": 10,
                        "max_replays": 2
                    },
                    {
                        "id": "L_Q3",
                        "prompt": "What alternative performance strategy did Meera propose to keep the show on schedule?",
                        "options": ["Postpone the event by 1 hour", "Sing unamplified acoustically", "Cancel the choir performance", "Replace the main sound crew"],
                        "correct_option_index": 1,
                        "target_construct": "Listening Comprehension",
                        "secondary_constructs": ["Reasoning"],
                        "question_type": "Comprehension",
                        "cognitive_objective": "Comprehension of overall proposed strategy in narrative context",
                        "difficulty": "intermediate",
                        "expected_evidence": {
                            "correct_answer_indicates": "Understanding of proposed unamplified acoustic singing strategy",
                            "distractor_rationale": {"0": "Unfounded postponement assumption", "2": "Drastic cancellation assumption"}
                        },
                        "weight": 1.0,
                        "points": 10,
                        "max_replays": 2
                    },
                    {
                        "id": "L_Q4",
                        "prompt": "What primary trade-off is created if the team proceeds with unamplified singing at 05:00 PM?",
                        "options": ["Starting on time versus acoustic audio coverage across the auditorium", "Ticket sales versus stage lighting", "Choir costume choices versus venue security", "Microphone brand versus amplifier cost"],
                        "correct_option_index": 0,
                        "target_construct": "Reasoning",
                        "secondary_constructs": ["Listening Comprehension"],
                        "question_type": "Inference",
                        "cognitive_objective": "Logical inference synthesizing timeline pressure and acoustic coverage impact",
                        "difficulty": "intermediate",
                        "expected_evidence": {
                            "correct_answer_indicates": "Inference synthesizing punctual start time and reduced acoustic volume",
                            "distractor_rationale": {"1": "Irrelevant ticketing distortion", "2": "Irrelevant costume distortion"}
                        },
                        "weight": 1.0,
                        "points": 10,
                        "max_replays": 2
                    }
                ],
                "speaking_prompts": [
                    {
                        "id": "S_P1",
                        "title": "Initial Decision: Audio Emergency",
                        "instructions": "Explain whether you choose to delay the opening or start acoustically, justifying your decision to Meera.",
                        "max_time_seconds": 120,
                        "target_constructs": ["COMMUNICATION", "DECISION_MAKING"],
                        "followup_eligible": True
                    },
                    {
                        "id": "S_P2",
                        "title": "Adaptive Challenge: Vocalist Resistance",
                        "instructions": "If the choir lead refuses to sing without microphones, how would you address their concern while keeping the event running smoothly?",
                        "max_time_seconds": 120,
                        "target_constructs": ["LEADERSHIP", "ADAPTABILITY"],
                        "followup_eligible": True
                    },
                    {
                        "id": "S_P3",
                        "title": "Reflective Probe: Performance Rationale",
                        "instructions": "Why do you believe your choice between punctuality and audio clarity is best for the audience experience?",
                        "max_time_seconds": 120,
                        "target_constructs": ["CONFIDENCE", "REASONING"],
                        "followup_eligible": True
                    }
                ],
                "construct_mappings": ["ATTENTION", "WORKING_MEMORY", "REASONING", "COMMUNICATION", "DECISION_MAKING", "LEADERSHIP", "ADAPTABILITY", "CONFIDENCE"],
                "expected_behaviour_signals": "Demonstrates team management, stress tolerance, and clear prioritization of scheduling versus auditory parameters.",
                "metadata": {}
            }
        else:
            mock_payload = {
                "status": "SUCCESS",
                "extracted_info": "Generic structured mock LLM output",
                "confidence": 0.95,
            }

        content_str = json.dumps(mock_payload)
        
        return {
            "choices": [
                {
                    "message": {
                        "content": content_str,
                        "role": "assistant",
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 120,
                "completion_tokens": 65,
                "total_tokens": 185,
            },
            "id": f"mock-{uuid.uuid4()}",
            "model": self.default_model,
            "latency_ms": 50.0,
            
            # APOS support
            "content": content_str,
            "raw_payload": mock_payload,
            "provider": self.provider_name,
            "prompt_tokens": 120,
            "completion_tokens": 65,
            "total_tokens": 185,
        }
