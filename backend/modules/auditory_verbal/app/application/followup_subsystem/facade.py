"""
Adaptive Interview Intelligence System (AIIS v15.0.0 Architecture).
Orchestrates the 10-Module Pipeline:
1. Frontend Validator (Surface check)
2. Interview Understanding Engine (Single LLM call: status, decision, coverage, signals)
3. Interview Memory (Evidence Repository: Candidate Facts)
4. Conversation Manager & Conversation State (Interviewer Brain & Action Mapping Table)
5. Information Need Prioritization Engine (Priority scoring of missing gaps)
6. Interview Strategy Engine (Selects EXACTLY ONE objective)
7. Specification Compiler (Compiles immutable FollowUpSpecification)
8. Question Writer (Nemotron - "Continue an interview" persona)
9. Interview QA Engine (9-point boolean quality checklist & deterministic fallback)
10. Interview Completion Engine (Evidence saturation & section completion evaluation)
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)
from app.application.followup_subsystem.evidence_extractor import BehavioralEvidenceExtractor
from app.application.followup_subsystem.evidence_graph import BehavioralEvidenceGraph, GraphNode, GraphEdge, NodeType, EdgeType
from app.application.followup_subsystem.construct_analyzer import ConstructAnalysisEngine
from app.application.followup_subsystem.closure_engine import ConstructSaturationEngine, InterviewClosureEngine, InterviewCompletionEngine, ClosureDecision
from app.application.followup_subsystem.analytics_collector import InterviewAnalyticsCollector
from app.application.followup_subsystem.interview_understanding import InterviewUnderstandingEngine, InterviewUnderstandingResult
from app.application.followup_subsystem.memory import InterviewMemoryManager, InterviewMemory
from app.application.followup_subsystem.conversation_manager import ConversationStateManager, ConversationManager, ConversationState, InterviewerAction
from app.application.followup_subsystem.decision_gap_prioritization import DecisionGapPrioritizationEngine, PrioritizedInformationNeed
from app.application.followup_subsystem.strategy_engine import InterviewStrategyEngine, InterviewObjective
from app.application.followup_subsystem.style_engine import ConversationStyleEngine, StyleProfile
from app.application.followup_subsystem.planning_engine import FollowUpPlanningEngine
from app.application.followup_subsystem.compiler import FollowUpSpecificationCompiler
from app.application.followup_subsystem.specification import FollowUpSpecification
from app.application.followup_subsystem.interview_quality_engine import InterviewQAEngine, QAChecklistResult
from app.application.followup_subsystem.reasoning_engine import EvidenceReasoningEngine, ConstructExplanation
from app.application.followup_subsystem.explanation_builder import ConstructExplanationBuilder
from app.infrastructure.prompt_service.facade import AIPromptOrchestrationService as APOSFacade


from app.application.followup_subsystem.evidence_sufficiency_engine import EvidenceSufficiencyEngine, DimensionSufficiency, EvidenceLevel
from app.application.followup_subsystem.behavioral_consistency_engine import BehavioralConsistencyEngine, BehaviorObservation, BehaviorState
from app.application.followup_subsystem.behavioral_belief_engine import BehavioralBeliefEngine, BehaviorBelief, BeliefStatus


from app.application.followup_subsystem.world_model import InterviewWorldModel
from app.application.followup_subsystem.intent_understanding_engine import IntentUnderstandingEngine, CandidateIntent, IntentResult
from app.application.followup_subsystem.interview_controller import InterviewController, InterviewPolicy, InterviewMode
from app.application.followup_subsystem.information_gain_engine import InformationGainEngine, InformationGainResult
from app.application.followup_subsystem.dialogue_planner import DialoguePlanner, SemanticDialogueAct, InterviewMove
from app.application.followup_subsystem.conversation_flow_engine import ConversationFlowEngine, FlowDecision
from app.application.followup_subsystem.dialogue_editor import DialogueEditor, EditedDialogueResult


from app.application.followup_subsystem.session_state import FollowUpSessionStateManager
from app.application.followup_subsystem.adaptive_evidence_extractor import AdaptiveEvidenceExtractor
from app.application.followup_subsystem.adaptive_coverage_analyzer import AdaptiveCoverageAnalyzer
from app.application.followup_subsystem.adaptive_gap_detector import AdaptiveGapDetector
from app.application.followup_subsystem.adaptive_objective_planner import AdaptiveObjectivePlanner
from app.application.followup_subsystem.adaptive_specification_compiler import AdaptiveFollowUpSpecificationCompiler


class AdaptiveInterviewIntelligenceSystem:
    """Facade orchestrating the AIIS v20.1 Architecture."""

    def __init__(self, apos_facade: Optional[APOSFacade] = None):
        self.extractor = BehavioralEvidenceExtractor()
        self.analyzer = ConstructAnalysisEngine()
        self.saturation_engine = ConstructSaturationEngine()
        self.completion_engine = InterviewCompletionEngine()
        self.closure_engine = self.completion_engine
        self.understanding_engine = InterviewUnderstandingEngine()
        self.intent_engine = IntentUnderstandingEngine()
        self.controller = InterviewController()
        self.gain_engine = InformationGainEngine()
        self.dialogue_planner = DialoguePlanner()
        self.flow_engine = ConversationFlowEngine()
        self.dialogue_editor = DialogueEditor()
        self.memory_manager = InterviewMemoryManager()
        self.sufficiency_engine = EvidenceSufficiencyEngine()
        self.consistency_engine = BehavioralConsistencyEngine()
        self.belief_engine = BehavioralBeliefEngine()
        self.state_manager = ConversationStateManager()
        self.conversation_manager = ConversationManager()
        self.prioritization_engine = DecisionGapPrioritizationEngine()
        self.strategy_engine = InterviewStrategyEngine()
        self.style_engine = ConversationStyleEngine()
        self.planning_engine = FollowUpPlanningEngine()
        self.compiler = FollowUpSpecificationCompiler()
        self.qa_engine = InterviewQAEngine()
        self.reasoning_engine = EvidenceReasoningEngine()
        self.explanation_builder = ConstructExplanationBuilder()
        self.apos = apos_facade or APOSFacade()

        # New Adaptive Follow-up Planning Layer (Shadow Mode - Stages 1 to 6)
        self.shadow_state_manager = FollowUpSessionStateManager()
        self.shadow_extractor = AdaptiveEvidenceExtractor(self.apos)
        self.shadow_coverage_analyzer = AdaptiveCoverageAnalyzer()
        self.shadow_gap_detector = AdaptiveGapDetector()
        self.shadow_objective_planner = AdaptiveObjectivePlanner()
        self.shadow_spec_compiler = AdaptiveFollowUpSpecificationCompiler()
        self.enable_shadow_stage6_llm: bool = True
        self._shadow_tasks: set = set()

        self._total_turns = 0
        self._qa_passed_count = 0
        self._qa_failed_count = 0
        self._qa_failure_log: List[Dict[str, Any]] = []
        self._llm_total_evaluations = 0
        self._llm_qa_passed_count = 0
        self._llm_qa_rejected_count = 0
        self._llm_rejection_log: List[Dict[str, Any]] = []
        self._check_failure_counts: Dict[str, int] = {}

    def get_qa_fallback_analytics(self) -> Dict[str, Any]:
        return {
            "total_turns": self._total_turns,
            "llm_total_evaluations": self._llm_total_evaluations,
            "llm_qa_passed_count": self._llm_qa_passed_count,
            "llm_qa_rejected_count": self._llm_qa_rejected_count,
            "llm_fallback_rate": round(self._llm_qa_rejected_count / max(self._llm_total_evaluations, 1), 4),
            "check_failure_counts": dict(self._check_failure_counts),
            "rejection_log": list(self._llm_rejection_log),
            "qa_passed_count": self._qa_passed_count,
            "qa_failed_count": self._qa_failed_count,
            "qa_pass_rate": round(self._qa_passed_count / max(self._total_turns, 1), 2),
            "recent_failures": self._qa_failure_log[-20:],
        }

    def generate_assessment_explanation_report(
        self,
        session_id: str,
        candidate_id: str,
        target_constructs: List[str],
        scores: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        state = self.state_manager.get_or_create_state(session_id)
        graph = state.evidence_graph
        sat_matrix = self.saturation_engine.calculate_saturation(graph, target_constructs, state)
        score_dict = scores or {}
        explanations: List[ConstructExplanation] = []
        for c in target_constructs:
            c_score = score_dict.get(c, 0.80)
            sat_metrics = sat_matrix.get(c)
            expl = self.reasoning_engine.explain_construct(c, graph, sat_metrics, c_score)
            explanations.append(expl)
        report = self.explanation_builder.build_assessment_explanation(session_id, candidate_id, explanations)
        return report.to_dict()

    @classmethod
    def _lookup_scenario_narrative(cls, scenario_title: str) -> str:
        if not scenario_title:
            return "During an urgent high-stakes decision scenario, the candidate must address competing technical and team priorities under tight deadlines."
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
        return f"In scenario '{scenario_title}', the candidate must navigate urgent technical, safety, ethical, and team constraints under tight evaluation deadlines."

    async def generate_followup_question(
        self,
        scenario_title: str,
        transcript_text: str,
        target_construct: str,
        conversation_history: str = "",
        current_assessment_state: str = "SPEAKING_ASSESSMENT",
        behavior_evidence: str = "",
        target_constructs: Optional[List[str]] = None,
        session_id: str = "default_session",
        scenario_text: str = "",
        scenario_background_stakes: str = "",
    ) -> Dict[str, Any]:
        """Runs the 10-module AIIS pipeline."""

        constructs_list = target_constructs or [target_construct]

        # Module 3 & 4: Retrieve Interview Memory (Candidate Facts) & Conversation State (Interviewer Brain)
        memory = self.memory_manager.get_or_create_memory(session_id)
        state = self.state_manager.get_or_create_state(session_id)
        graph = state.evidence_graph


        # Module 2: Interview Understanding Engine (Single LLM call parsing as primary path)
        understanding_payload = None
        if (transcript_text or "").strip():
            try:
                apos_und_res = await self.apos.execute_prompt(
                    prompt_id="INTERVIEW_UNDERSTANDING_PROMPT",
                    variables={
                        "scenario_title": scenario_title,
                        "transcript_text": transcript_text,
                        "conversation_history": conversation_history or "None",
                    },
                    version="15.0.0"
                )
                understanding_payload = dict(apos_und_res.validated_response or {})
            except Exception:
                understanding_payload = None

        understanding_res = self.understanding_engine.evaluate_understanding(
            scenario_title=scenario_title,
            transcript_text=transcript_text,
            conversation_history=conversation_history,
            llm_response_payload=understanding_payload,
        )

        # Record candidate facts into Interview Memory (Module 3)
        memory.record_candidate_facts(transcript_text, understanding_res.candidate_decision, state.turn_number)

        # Module 4: Conversation Manager — Determine Interviewer Action & Check Contradiction
        action = self.conversation_manager.determine_action(understanding_res.status, state)
        contra_info = memory.detect_contradiction(understanding_res.candidate_decision.action)
        if contra_info:
            action = InterviewerAction.VERIFY_CONSISTENCY

        # Extract behavioral evidence for scoring
        evidence_items = self.extractor.extract_evidence(transcript_text, constructs_list)
        saturation_matrix = self.saturation_engine.calculate_saturation(graph, constructs_list, state)

        # Module 10: Interview Completion Engine — Evaluate Closure
        closure_decision = self.completion_engine.evaluate_closure(graph, saturation_matrix, state, constructs_list)

        if closure_decision.should_close or action == InterviewerAction.TERMINATE:
            return {
                "internal_reasoning": closure_decision.closure_reason or "Interview section completed.",
                "answer_quality": "GOOD",
                "intent": "INTERVIEW_CLOSURE",
                "is_relevant": True,
                "needs_clarification": False,
                "follow_up_question": "Thank you for completing this assessment section. You have provided clear, comprehensive responses across all topics.",
                "question_text": "Thank you for completing this assessment section. You have provided clear, comprehensive responses across all topics.",
                "closure_decision": closure_decision.to_dict(),
                "conversation_state": state.to_dict(),
                "interview_memory": memory.to_dict(),
            }

        # Module 2.5: Intent Understanding Engine (Pure Perception)
        intent_res = self.intent_engine.evaluate_intent(
            transcript_text=transcript_text,
            turn_number=state.turn_number,
            understanding_result=understanding_res,
        )

        # Immediate Repair Routing for Non-Valid Input Statuses (NONSENSICAL, OFF_TOPIC, REFUSAL)
        if action in (InterviewerAction.REALISTIC_ANSWER, InterviewerAction.REDIRECT, InterviewerAction.ENCOURAGE):
            repair_msgs = {
                InterviewerAction.REALISTIC_ANSWER: "I couldn't clearly understand how you would handle the situation. Could you explain your approach in a little more detail?",
                InterviewerAction.REDIRECT: "Let's focus back on the scenario. What step would you take to address the situation at hand?",
                InterviewerAction.ENCOURAGE: "Your input is important for this assessment. What initial approach would you consider?",
            }
            repair_q = repair_msgs.get(action, "Could you explain your approach in a little more detail?")
            state.asked_question_texts.append(repair_q)
            self.conversation_manager.update_interviewer_state(state, "REPAIR")
            return {
                "internal_reasoning": f"Repair action {action.value} triggered due to status {understanding_res.status}",
                "answer_quality": "INVALID",
                "intent": "REPAIR_RESPONSE",
                "is_relevant": action != InterviewerAction.REDIRECT,
                "needs_clarification": True,
                "follow_up_question": repair_q,
                "question_text": repair_q,
                "understanding_result": understanding_res.to_dict(),
                "intent_result": intent_res.to_dict(),
                "conversation_state": state.to_dict(),
                "interview_memory": memory.to_dict(),
                "qa_result": {"is_passed": True, "failed_checks": []},
            }

        # Module 3: Interview World Model (Consolidated State)
        world_model = InterviewWorldModel(
            session_id=session_id,
            scenario_title=scenario_title,
            turn_number=state.turn_number,
            memory=memory,
            conversation_state=state,
            intent_result=intent_res.to_dict(),
        )

        # Module 3.8: Interview Controller (Generates explicit InterviewPolicy)
        policy = self.controller.evaluate_policy(
            intent_res=intent_res,
            overall_uncertainty=world_model.calculate_overall_uncertainty(),
            turn_number=state.turn_number,
            contradiction_detected=(action == InterviewerAction.VERIFY_CONSISTENCY),
        )
        world_model.active_policy = policy.to_dict()

        # Module 4.5: Information Gain Engine (Calculates Expected Uncertainty Reduction ΔU)
        gain_res = self.gain_engine.compute_information_gain(world_model)
        world_model.information_gain_scores = gain_res.expected_gain_matrix

        # Module 7.5: Dialogue Planner (Pure Semantic Dialogue Acts)
        cand_summary = memory.extract_memory_reference() or transcript_text[:50]
        dialogue_act = self.dialogue_planner.plan_dialogue_act(
            objective=gain_res.recommended_dimension,
            policy=policy,
            candidate_summary=cand_summary,
            target_dimension=gain_res.recommended_dimension,
        )

        # Module 7.8: Conversation Flow Engine
        flow_decision = self.flow_engine.evaluate_flow(world_model, policy)

        # Module 3.5: Evidence Sufficiency Engine (AIIS v16)
        sufficiency_matrix = self.sufficiency_engine.evaluate_sufficiency(
            decision=understanding_res.candidate_decision,
            memory=memory,
            transcript_text=transcript_text,
        )

        # Module 3.6: Behavioral Consistency Engine (AIIS v17.1)
        observations: Dict[str, BehaviorObservation] = {}
        for dim in ["Reason", "Risk", "Stakeholders", "Alternatives", "Tradeoffs", "Reflection"]:
            obs = self.consistency_engine.evaluate_consistency(
                dimension=dim,
                decision=understanding_res.candidate_decision,
                memory=memory,
                scenario_title=scenario_title,
                transcript_text=transcript_text,
                turn_number=state.turn_number,
            )
            observations[dim] = obs

        # Module 3.7: Behavioral Belief Engine (AIIS v18)
        existing_beliefs = getattr(state, "beliefs_matrix", {})
        beliefs_matrix = self.belief_engine.evaluate_beliefs(
            observations=observations,
            existing_beliefs=existing_beliefs,
            turn_number=state.turn_number,
        )
        setattr(state, "beliefs_matrix", beliefs_matrix)
        world_model.beliefs_matrix = {k: v.to_dict() for k, v in beliefs_matrix.items()}

        # Module 5 & 6: Prioritization & Strategy Engine — Select Objective using Information Gain Target & Policy
        prioritized_needs = self.prioritization_engine.prioritize_gaps(
            sufficiency_matrix=sufficiency_matrix,
            beliefs_matrix=beliefs_matrix,
            state=state,
            target_construct=target_construct,
            target_constructs=constructs_list,
        )
        active_objective = self.strategy_engine.select_objective(
            action,
            prioritized_needs,
            state,
            policy,
            target_construct,
            gain_res.recommended_dimension,
        )

        # Style Engine Profile Computation
        style_profile = self.style_engine.determine_style(state, active_objective.value, transcript_text)

        # Module 7: FollowUpPlanningEngine & Specification Compiler
        plan = self.planning_engine.create_plan(
            active_objective=active_objective,
            decision_data=understanding_res.candidate_decision,
            scenario_title=scenario_title,
            transcript_text=transcript_text,
            state=state,
        )
        memory_ref = memory.extract_memory_reference()
        spec = self.compiler.compile(
            state=state,
            plan=plan,
            style_profile=style_profile,
            memory_reference=memory_ref,
        )

        # Module 8: Question Writer
        scen_narrative = getattr(state, "scenario_narrative", "") or scenario_text or self._lookup_scenario_narrative(scenario_title)
        scen_stakes = getattr(state, "scenario_stakes", "") or scenario_background_stakes or (
            "High-stakes technical and interpersonal decision under strict time constraints, where trade-offs between safety, quality, team alignment, and deadlines must be balanced."
        )
        variables = {
            "followup_specification": str(spec.to_dict()),
            "scenario_title": scenario_title,
            "scenario_text": scen_narrative,
            "scenario_background_stakes": scen_stakes,
            "transcript_text": transcript_text,
            "target_construct": spec.target_construct,
            "conversation_history": conversation_history or "None",
            "current_assessment_state": current_assessment_state,
            "behavior_evidence": str([e.indicator for e in evidence_items]),
        }

        generated_q_text = ""
        raw_llm_payload: Dict[str, Any] = {}

        try:
            result = await self.apos.execute_prompt(
                prompt_id="ADAPTIVE_FOLLOWUP_PROMPT",
                variables=variables,
                version="16.0.0"
            )
            raw_llm_payload = dict(result.validated_response or {})
            generated_q_text = raw_llm_payload.get("follow_up_question") or raw_llm_payload.get("question_text", "")
        except Exception as err:
            generated_q_text = ""

        # Module 8.5: Dialogue Editor — 40+ Opening Templates Rotation & Wording Compression
        editor_res = self.dialogue_editor.edit_dialogue(
            raw_question_text=generated_q_text,
            summary_reference=cand_summary,
            target_dimension=gain_res.recommended_dimension,
            used_openings=world_model.dialogue_memory.used_opening_templates,
        )
        edited_q_text = editor_res.edited_question_text

        # Module 9: Interview QA Engine — Evaluate real LLM output against quality checklist
        llm_qa_result: QAChecklistResult = self.qa_engine.evaluate_question(
            question_text=edited_q_text,
            spec=spec,
            decision_data=understanding_res.candidate_decision,
            scenario_title=scenario_title,
            state=state,
            previous_questions=state.asked_question_texts,
            transcript_text=transcript_text,
            scenario_narrative=scen_narrative,
        )

        self._llm_total_evaluations += 1
        fallback_triggered = False

        if llm_qa_result.is_passed and edited_q_text:
            self._llm_qa_passed_count += 1
            final_question_text = edited_q_text
            logger.info(
                f"[AIIS QA PASS] LLM output passed all QA checks. Session={session_id} Turn={state.turn_number} Q='{edited_q_text}'"
            )
        else:
            self._llm_qa_rejected_count += 1
            fallback_triggered = True
            for chk in llm_qa_result.failed_checks:
                self._check_failure_counts[chk] = self._check_failure_counts.get(chk, 0) + 1
            self._llm_rejection_log.append({
                "session_id": session_id,
                "turn_number": state.turn_number,
                "scenario_title": scenario_title,
                "transcript_text": transcript_text,
                "raw_generated_text": generated_q_text,
                "edited_question_text": edited_q_text,
                "failed_checks": list(llm_qa_result.failed_checks),
                "intent": active_objective.value,
            })
            logger.warning(
                f"[AIIS QA REJECTION] Real LLM question rejected. Session={session_id} Turn={state.turn_number} "
                f"Failed={llm_qa_result.failed_checks} Raw='{generated_q_text}' Edited='{edited_q_text}'"
            )
            # If QA Checklist fails any check, fall back to deterministic question construction
            # then route the fallback through DialogueEditor (Module 8.5) — defense in depth
            fallback_text = self.qa_engine.construct_deterministic_fallback(
                spec=spec,
                decision_data=understanding_res.candidate_decision,
                scenario_title=scenario_title,
                transcript_text=transcript_text,
                state=state,
            )
            fallback_editor_res = self.dialogue_editor.edit_dialogue(
                raw_question_text=fallback_text,
                summary_reference=cand_summary,
                target_dimension=gain_res.recommended_dimension,
                used_openings=world_model.dialogue_memory.used_opening_templates,
            )
            world_model.dialogue_memory.used_opening_templates.append(fallback_editor_res.opening_template_used)
            final_question_text = fallback_editor_res.edited_question_text

        # HARD SAFETY NET: Prevent exact or near-exact question text repetition against ALL previous question texts in session
        lower_final = final_question_text.strip().lower()
        for asked_q in state.asked_question_texts:
            lower_asked = asked_q.strip().lower()
            if lower_final == lower_asked or (len(lower_asked) > 15 and (lower_asked in lower_final or lower_final in lower_asked)):
                avail_templates = [t for t in self.dialogue_editor.OPENING_TEMPLATES if t not in world_model.dialogue_memory.used_opening_templates[-5:]]
                new_opener = avail_templates[0] if avail_templates else "Looking back..."
                dim_name = gain_res.recommended_dimension or "decision"
                turn_idx = len(state.asked_question_texts)
                varied_tails = [
                    "what key factor guided your choice?",
                    "what principal priority led to your decision?",
                    "how did you weigh the primary risks?",
                    "what outcome were you most focused on achieving?",
                ]
                chosen_tail = varied_tails[turn_idx % len(varied_tails)]
                final_question_text = f"{new_opener} regarding your approach to {dim_name.lower()}, {chosen_tail}"
                world_model.dialogue_memory.used_opening_templates.append(new_opener)
                break

        # Final QA evaluation on the final question text
        qa_result = self.qa_engine.evaluate_question(
            question_text=final_question_text,
            spec=spec,
            decision_data=understanding_res.candidate_decision,
            scenario_title=scenario_title,
            state=state,
            previous_questions=state.asked_question_texts,
            transcript_text=transcript_text,
        )

        self._total_turns += 1
        if qa_result.is_passed:
            self._qa_passed_count += 1
        else:
            self._qa_failed_count += 1
            self._qa_failure_log.append({
                "session_id": session_id,
                "turn_number": state.turn_number,
                "raw_generated_text": generated_q_text,
                "final_question_text": final_question_text,
                "failed_checks": qa_result.failed_checks,
            })

        state.asked_question_texts.append(final_question_text)
        state.asked_intent_history.append(active_objective.value)
        self.conversation_manager.update_interviewer_state(state, active_objective.value)

        # Dispatch non-blocking background shadow adaptive pipeline task (GC-safe)
        shadow_task = asyncio.create_task(
            self._run_shadow_adaptive_pipeline(
                session_id=session_id,
                scenario_title=scenario_title,
                transcript_text=transcript_text,
                target_constructs=constructs_list,
                turn_number=state.turn_number,
                scenario_id=getattr(state, "scenario_id", "SCEN-001"),
                candidate_id=getattr(state, "candidate_id", "CANDIDATE-001"),
            )
        )
        self._shadow_tasks.add(shadow_task)
        shadow_task.add_done_callback(self._shadow_tasks.discard)

        return {
            "internal_reasoning": spec.reason,
            "answer_quality": "INVALID" if action == InterviewerAction.CLARIFY else "GOOD",
            "intent": active_objective.value,
            "is_relevant": action != InterviewerAction.REDIRECT,
            "needs_clarification": action == InterviewerAction.CLARIFY,
            "follow_up_question": final_question_text,
            "question_text": final_question_text,
            "behavioral_evidence": [{"category": e.construct, "quote": e.verbatim_quote, "confidence": e.confidence} for e in evidence_items],
            "world_model": world_model.to_dict(),
            "intent_result": intent_res.to_dict(),
            "interview_policy": policy.to_dict(),
            "information_gain": gain_res.to_dict(),
            "dialogue_act": dialogue_act.to_dict(),
            "flow_decision": flow_decision.to_dict(),
            "dialogue_editor": editor_res.to_dict(),
            "qa_result": qa_result.to_dict(),
            "llm_qa_result": llm_qa_result.to_dict(),
            "llm_raw_question": generated_q_text,
            "llm_edited_question": edited_q_text,
            "fallback_triggered": fallback_triggered,
            "interview_memory": memory.to_dict(),
            "understanding_result": understanding_res.to_dict(),
            "sufficiency_matrix": {k: v.to_dict() for k, v in sufficiency_matrix.items()},
            "beliefs_matrix": {k: v.to_dict() for k, v in beliefs_matrix.items()},
            "closure_decision": closure_decision.to_dict(),
        }

    async def _run_shadow_adaptive_pipeline(
        self,
        session_id: str,
        scenario_title: str,
        transcript_text: str,
        target_constructs: List[str],
        turn_number: int,
        scenario_id: str = "SCEN-001",
        candidate_id: str = "CANDIDATE-001",
        scenario_constraints: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Runs Stages 1-4 (Evidence Extraction → Coverage → Gap Detection → Objective Planner) in Shadow Mode."""
        import json
        prim = target_constructs[:2] if target_constructs else ["DECISION_MAKING", "REASONING"]
        sec = target_constructs[2:] if len(target_constructs) > 2 else ["COMMUNICATION", "ATTENTION"]
        if not sec:
            sec = ["COMMUNICATION", "ATTENTION"]

        # 1. Retrieve or create session state
        session_state = self.shadow_state_manager.get_or_create_state(
            session_id=session_id,
            scenario_id=scenario_id,
            candidate_id=candidate_id,
            primary_constructs=prim,
            secondary_constructs=sec,
        )

        # 2. Stage 1: Evidence Extraction (LLM call)
        source = "initial_response" if turn_number <= 1 else f"followup_{turn_number-1}"
        latest_entry = await self.shadow_extractor.extract_evidence(
            scenario_title=scenario_title,
            candidate_response=transcript_text,
            session_state=session_state,
            turn_number=turn_number,
            source=source,
        )

        # 3. Stage 2: Construct Coverage Analysis (Deterministic)
        self.shadow_coverage_analyzer.analyze_coverage(session_state, latest_entry)

        # 4. Stage 3: Evidence Gap Detection (Deterministic)
        primary_gaps, secondary_gaps = self.shadow_gap_detector.detect_gaps(session_state)

        # 5. Stage 4: Follow-up Objective Planner (Deterministic)
        objective_decision = self.shadow_objective_planner.plan_objective(
            session_state=session_state,
            primary_gaps=primary_gaps,
            secondary_gaps=secondary_gaps,
            turn_number=turn_number,
            scenario_constraints=scenario_constraints,
        )

        # Record decision into session state followup_history (skip for terminate)
        if not objective_decision.is_terminate:
            session_state.followup_history.append({
                "turn": turn_number,
                "objective": objective_decision.objective,
                "target_constructs": objective_decision.target_constructs,
                "reason": objective_decision.reason,
            })

        # 6. Stage 5: Follow-up Specification Compiler (Deterministic DTO Bridge)
        followup_spec_dto = None
        if not objective_decision.is_terminate:
            try:
                style_profile = self.style_engine.determine_style(
                    state=session_state,
                    active_objective=objective_decision.objective,
                    transcript_text=transcript_text,
                )
                followup_spec_dto = self.shadow_spec_compiler.compile(
                    decision=objective_decision,
                    session_state=session_state,
                    style_profile=style_profile,
                    turn_number=turn_number,
                    transcript_text=transcript_text,
                )
            except Exception as err:
                logger.warning(
                    f"[ADAPTIVE FOLLOWUP SHADOW SPEC] StyleEngine / compiler failed for turn {turn_number}: {err} — skipping spec compile"
                )
                followup_spec_dto = None

        # 7. Stage 6: Follow-up Question Phrasing (LLM + Dialogue Editor + QA Engine)
        stage6_phrasing = None
        if not objective_decision.is_terminate and followup_spec_dto and self.enable_shadow_stage6_llm:
            try:
                scen_narrative = self._lookup_scenario_narrative(scenario_title)
                scen_stakes = (
                    "High-stakes technical and interpersonal decision under strict time constraints, "
                    "where trade-offs between safety, quality, team alignment, and deadlines must be balanced."
                )
                assessment_state_str = self._format_shadow_assessment_state(session_state)
                behavior_evidence_str = self._format_shadow_behavior_evidence(latest_entry)
                conv_history_str = self._format_shadow_conversation_history(session_state)

                prompt_vars = {
                    "followup_specification": str(followup_spec_dto.to_dict()),
                    "scenario_title": scenario_title,
                    "scenario_text": scen_narrative,
                    "scenario_background_stakes": scen_stakes,
                    "transcript_text": transcript_text,
                    "target_construct": followup_spec_dto.target_construct,
                    "conversation_history": conv_history_str,
                    "current_assessment_state": assessment_state_str,
                    "behavior_evidence": behavior_evidence_str,
                }

                llm_result = await asyncio.wait_for(
                    self.apos.execute_prompt(
                        prompt_id="ADAPTIVE_FOLLOWUP_PROMPT",
                        variables=prompt_vars,
                        version="16.0.0",
                    ),
                    timeout=45.0,
                )
                raw_llm_payload = dict(llm_result.validated_response or {})
                raw_q_text = raw_llm_payload.get("follow_up_question") or raw_llm_payload.get("question_text", "")

                editor_res = self.dialogue_editor.edit_dialogue(
                    raw_question_text=raw_q_text,
                    summary_reference=transcript_text[:50],
                    target_dimension=followup_spec_dto.target_construct,
                    used_openings=[],
                )
                edited_q_text = editor_res.edited_question_text

                qa_eval = self.qa_engine.evaluate_question(
                    question_text=edited_q_text,
                    spec=followup_spec_dto,
                    decision_data=None,
                    scenario_title=scenario_title,
                    state=None,
                    previous_questions=[],
                    transcript_text=transcript_text,
                    scenario_narrative=scen_narrative,
                )

                stage6_phrasing = {
                    "raw_llm_question": raw_q_text,
                    "edited_question": edited_q_text,
                    "qa_evaluation": qa_eval.to_dict(),
                }
            except asyncio.TimeoutError:
                logger.warning(
                    f"[ADAPTIVE FOLLOWUP SHADOW PHRASING] Stage 6 LLM call timed out after 45.0s for turn {turn_number} — skipping phrasing"
                )
                stage6_phrasing = None
            except Exception as err:
                logger.warning(
                    f"[ADAPTIVE FOLLOWUP SHADOW PHRASING] Stage 6 LLM phrasing failed for turn {turn_number}: {err} — skipping phrasing"
                )
                stage6_phrasing = None

        # 8. Logging (Shadow Mode Output)
        output_payload = {
            "shadow_pipeline_stage": "STAGE_1_2_3_4_5_6_COMPLETE" if stage6_phrasing else "STAGE_1_2_3_4_5_COMPLETE",
            "session_id": session_id,
            "state": session_state.to_dict(),
            "primary_gaps": primary_gaps,
            "secondary_gaps": secondary_gaps,
            "stage4_decision": objective_decision.to_dict(),
            "stage5_spec": followup_spec_dto.to_dict() if followup_spec_dto else None,
            "stage6_phrasing": stage6_phrasing,
            "is_terminate": objective_decision.is_terminate,
            "termination_reason": objective_decision.termination_reason,
        }
        logger.info(f"[ADAPTIVE FOLLOWUP SHADOW PHRASING] {json.dumps(output_payload)}")
        return output_payload

    def _format_shadow_assessment_state(self, session_state: FollowUpSessionState) -> str:
        """Formats session_state construct coverage dictionary into structured summary string."""
        parts = []
        for c_name, cov in session_state.construct_coverage.items():
            parts.append(f"{c_name}: {cov.confidence:.2f} ({cov.status})")
        return ", ".join(parts) if parts else "No coverage records yet"

    def _format_shadow_behavior_evidence(self, latest_entry: Any) -> str:
        """Formats latest EvidenceLogEntry claims and reasoning into evidence string."""
        if not latest_entry:
            return "No evidence recorded"
        claims = getattr(latest_entry, "claims", [])
        reasoning = getattr(latest_entry, "reasoning_shown", [])
        return f"Claims: {claims} | Reasoning: {reasoning}"

    def _format_shadow_conversation_history(self, session_state: FollowUpSessionState) -> str:
        """Formats multi-turn transcript history from session_state evidence log."""
        if not session_state.evidence_log:
            return "None"
        history_lines = []
        for entry in session_state.evidence_log:
            history_lines.append(f"Turn {entry.turn} ({entry.source}): {entry.claims}")
        return "\n".join(history_lines)



# Backward compatibility alias
AdaptiveFollowUpSystem = AdaptiveInterviewIntelligenceSystem

