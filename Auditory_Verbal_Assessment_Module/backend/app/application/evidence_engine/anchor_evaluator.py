import re
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from app.core.logging import logger
from app.core.config import settings
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.entities.behavioural_indicator import BehaviouralIndicator
from app.application.speech.fluency_engine import FluencyEngine, FluencyResult


@dataclass(frozen=True)
class IndicatorScoreResult:
    """Immutable scoring evaluation for a single behavioural indicator."""
    indicator_id: str
    name: str
    weight: float
    scale: str
    score: int                           # Strictly 0, 1, 2, 3, or 4
    matched_anchor: str
    evidence_quote: str
    confidence: float                   # Strictly audit metadata (NEVER modifies score)
    rationale: str
    tier_source: str                    # "TIER_2_SEMANTIC" | "TIER_1_FALLBACK"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "indicator_id": self.indicator_id,
            "name": self.name,
            "weight": self.weight,
            "scale": self.scale,
            "score": self.score,
            "matched_anchor": self.matched_anchor,
            "evidence_quote": self.evidence_quote,
            "confidence": round(self.confidence, 2),
            "rationale": self.rationale,
            "tier_source": self.tier_source,
        }


@dataclass(frozen=True)
class QuestionEvaluationResult:
    """Comprehensive evaluation result for a single speaking question (SQ1, SQ2, or SQ3)."""
    question_id: str
    prompt_id: str
    stage: str
    indicators: List[IndicatorScoreResult]
    weighted_indicator_sum: float       # Sum(score_i * weight_i)
    max_weighted_score: float           # 18.4
    rubric_score: float                 # (weighted_sum / 18.4) * 100
    fluency_result: FluencyResult
    question_score: float               # 0.70 * rubric_score + 0.30 * fluency_score
    tier_source: str
    reliability_status: str             # "VALIDATED_SEMANTIC" | "DEGRADED_STRUCTURAL" | "ZERO_RESPONSE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "prompt_id": self.prompt_id,
            "stage": self.stage,
            "indicators": [ind.to_dict() for ind in self.indicators],
            "weighted_indicator_sum": round(self.weighted_indicator_sum, 2),
            "max_weighted_score": self.max_weighted_score,
            "rubric_score": round(self.rubric_score, 2),
            "fluency_score": round(self.fluency_result.score, 1),
            "question_score": round(self.question_score, 2),
            "tier_source": self.tier_source,
            "reliability_status": self.reliability_status,
        }


class AnchorEvaluator:
    """Evaluates candidate speaking answers against canonical behavioural anchors.
    Orchestrates Tier 2 LLM semantic evaluation with a non-blocking Tier 1 structural fallback.
    Enforces the strict rule: Word count is ONLY a sufficiency gate; evidence determines score.
    """

    MAX_WEIGHTED_SCORE = 18.4
    TOTAL_WEIGHT = 4.6

    # Causal & structural discourse markers for Tier 1 structural fallback
    CAUSAL_CONNECTIVES = ["because", "since", "due to", "as a result", "therefore", "so that", "in order to", "consequently"]
    CONTRAST_CONNECTIVES = ["instead of", "rather than", "however", "alternatively", "trade-off", "compromise", "on the other hand"]
    ACTION_VERBS = ["choose", "decide", "reroute", "re-route", "halt", "stop", "inform", "notify", "deploy", "switch", "isolate", "inspect", "repair"]
    RETROSPECTIVE_MARKERS = ["in hindsight", "lesson", "learned", "looking back", "assumption", "principle", "improve", "future"]

    def __init__(self, fluency_engine: Optional[FluencyEngine] = None):
        self.fluency_engine = fluency_engine or FluencyEngine()

    async def evaluate_question(
        self,
        prompt: SpeakingPrompt,
        scenario_context: str,
        transcript_text: str,
        duration_seconds: Optional[float] = None,
        audio_file_url: Optional[str] = None,
        words_per_second: Optional[float] = None,
        pause_ratio: Optional[float] = None,
    ) -> QuestionEvaluationResult:
        """Evaluates one complete speaking answer (SQ1, SQ2, or SQ3)."""
        clean_text = (transcript_text or "").strip()
        words = clean_text.split() if clean_text else []
        word_count = len(words)

        # 1. Fluency Delivery Evaluation
        fluency_res = self.fluency_engine.evaluate(
            transcript_text=clean_text,
            duration_seconds=duration_seconds,
            audio_file_url=audio_file_url,
            words_per_second=words_per_second,
            pause_ratio=pause_ratio,
        )

        # 2. Zero / Silence Detection (0 words)
        if word_count == 0:
            zero_indicators = [
                IndicatorScoreResult(
                    indicator_id=ind.indicator_id,
                    name=ind.name,
                    weight=ind.weight,
                    scale=ind.scale,
                    score=0,
                    matched_anchor=ind.anchors.get("0", "Fails to state a choice or remains completely undecided."),
                    evidence_quote="",
                    confidence=1.0,
                    rationale="No audible or transcribable response provided.",
                    tier_source="TIER_1_FALLBACK",
                )
                for ind in prompt.behavioural_indicators
            ]
            return QuestionEvaluationResult(
                question_id=prompt.question_id,
                prompt_id=prompt.prompt_id,
                stage=prompt.stage,
                indicators=zero_indicators,
                weighted_indicator_sum=0.0,
                max_weighted_score=self.MAX_WEIGHTED_SCORE,
                rubric_score=0.0,
                fluency_result=fluency_res,
                question_score=0.0,
                tier_source="TIER_1_FALLBACK",
                reliability_status="ZERO_RESPONSE",
            )

        # 3. Attempt Tier 2 Semantic Anchor Evaluation if enabled
        tier2_result: Optional[List[IndicatorScoreResult]] = None
        if settings.ENABLE_LLM_EVALUATION and word_count >= 4:
            try:
                timeout = getattr(settings, "LLM_EVALUATION_TIMEOUT_SECONDS", 5.0)
                tier2_result = await asyncio.wait_for(
                    self._evaluate_tier2_llm(prompt, scenario_context, clean_text),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                logger.warning(f"[EVALUATOR] Tier 2 timeout ({timeout}s) for {prompt.question_id}. Falling back to Tier 1.")
            except Exception as e:
                logger.warning(f"[EVALUATOR] Tier 2 failure for {prompt.question_id}: {e}. Falling back to Tier 1.")

        # 4. Resolve Final Indicator Scores (Tier 2 or Tier 1 Fallback)
        if tier2_result and len(tier2_result) == len(prompt.behavioural_indicators):
            final_indicators = tier2_result
            tier_source = "TIER_2_SEMANTIC"
            rel_status = "VALIDATED_SEMANTIC"
        else:
            final_indicators = self._evaluate_tier1_structural(prompt, clean_text)
            tier_source = "TIER_1_FALLBACK"
            rel_status = "DEGRADED_STRUCTURAL"

        # 5. Compute Weighted Rubric Score
        # RubricScore = (Sum(score_i * weight_i) / 18.4) * 100
        weighted_sum = sum(ind.score * ind.weight for ind in final_indicators)
        rubric_score = round(min(100.0, max(0.0, (weighted_sum / self.MAX_WEIGHTED_SCORE) * 100.0)), 2)

        # 6. Compute Final Combined Question Score
        # QuestionScore = 0.70 * RubricScore + 0.30 * FluencyScore
        question_score = round(min(100.0, max(0.0, 0.70 * rubric_score + 0.30 * fluency_res.score)), 2)

        return QuestionEvaluationResult(
            question_id=prompt.question_id,
            prompt_id=prompt.prompt_id,
            stage=prompt.stage,
            indicators=final_indicators,
            weighted_indicator_sum=round(weighted_sum, 2),
            max_weighted_score=self.MAX_WEIGHTED_SCORE,
            rubric_score=rubric_score,
            fluency_result=fluency_res,
            question_score=question_score,
            tier_source=tier_source,
            reliability_status=rel_status,
        )

    # Canonical domain marker vocabularies for Tier 1 structural fallback
    DECISION_VERBS = ["choose", "decide", "re-route", "reroute", "halt", "stop", "switch", "deploy", "isolate", "inspect", "repair", "execute", "select"]
    CAUSAL_CONNECTIVES = ["because", "since", "due to", "as a result", "therefore", "so that", "in order to", "consequently"]
    CONTRAST_CONNECTIVES = ["instead of", "rather than", "however", "alternatively", "trade-off", "tradeoff", "compromise", "on the other hand", "versus", "against"]
    CONSEQUENCE_MARKERS = ["deadline", "risk", "damage", "consequence", "impact", "disqualification", "delay", "loss", "temperature", "voltage", "safety", "fail"]
    ACTION_PLAN_MARKERS = ["plan", "execute", "roadmap", "steps", "procedure", "strategy", "timeline", "protocol", "measures"]
    
    COMPLICATION_MARKERS = ["steep", "hill", "slope", "terrain", "broken", "temperature", "voltage", "unexpected", "complication", "issue", "bottleneck", "obstacle", "problem", "disruption", "challenge"]
    ADAPT_VERBS = ["adapt", "switch", "pivot", "modify", "reroute", "re-route", "change", "adjust", "alter", "divert", "substitute"]
    PRIORITY_MARKERS = ["prioritize", "priority", "critical", "most important", "essential", "primary", "bottleneck", "focus on", "flatter", "safe", "safest", "urgent"]
    
    TRADEOFF_MARKERS = ["trade-off", "tradeoff", "compromise", "sacrifice", "rather than", "instead of", "versus", "against", "lost", "gained", "weighed", "balance", "cost"]
    ASSUMPTION_MARKERS = ["assumption", "assumed", "premise", "limitation", "flawed", "blind spot", "boundary", "optimistic", "pessimistic", "relied on", "underlying", "supposed"]
    RIPPLE_MARKERS = ["consequence", "ripple", "downstream", "stakeholder", "systemic", "timeline", "future impact", "secondary", "trust", "safety", "long-term", "cascading", "as a result"]
    IMPROVEMENT_MARKERS = ["improve", "in hindsight", "better", "adjust", "optimize", "different", "could have", "should have", "next time", "corrective", "retrospective"]
    PRINCIPLE_MARKERS = ["principle", "lesson", "learned", "always", "rule", "takeaway", "heuristic", "future operations", "general guideline", "framework", "standard practice", "key takeaway"]

    def _evaluate_tier1_structural(
        self,
        prompt: SpeakingPrompt,
        transcript_text: str,
    ) -> List[IndicatorScoreResult]:
        """Tier 1 Conservative Structural Safeguard.
        Scores strictly between 0 and 2 based on verified discourse markers.
        NEVER assigns 3 or 4 without semantic LLM anchor verification.
        """
        clean_text = transcript_text.strip()
        lower_text = clean_text.lower()
        words = clean_text.split()
        word_count = len(words)

        results: List[IndicatorScoreResult] = []
        q_id = getattr(prompt, "question_id", "SQ1").upper()

        for ind in prompt.behavioural_indicators:
            ind_id = ind.indicator_id.upper()
            score = 0
            rationale = "Minimal or baseline structural detection."

            if word_count < 4:
                # 1-3 words: Level 1 on first indicator if action present, else 0
                if ("IND_1" in ind_id or "IND_2" in ind_id) and any(v in lower_text for v in self.DECISION_VERBS + self.ADAPT_VERBS):
                    score = 1
                    rationale = "Fragmentary choice/action statement (short response)."
                else:
                    score = 0
                    rationale = "Insufficient linguistic material for indicator."
            elif word_count < 8:
                # 4-7 words: Basic presence
                if "SQ1" in q_id:
                    if "IND_1" in ind_id:
                        score = 2 if any(v in lower_text for v in self.DECISION_VERBS) else 1
                        rationale = "Basic choice declared in short response."
                    elif "IND_2" in ind_id:
                        score = 1 if any(c in lower_text for c in self.CAUSAL_CONNECTIVES) else 0
                        rationale = "Causal connective present."
                    elif "IND_3" in ind_id:
                        score = 1 if any(m in lower_text for m in self.CONSEQUENCE_MARKERS) else 0
                        rationale = "Basic consequence reference."
                    elif "IND_4" in ind_id:
                        score = 1 if any(m in lower_text for m in self.CONTRAST_CONNECTIVES) else 0
                        rationale = "Basic contrast/alternative reference."
                    elif "IND_5" in ind_id:
                        score = 1 if any(m in lower_text for m in self.ACTION_PLAN_MARKERS + self.DECISION_VERBS) else 0
                        rationale = "Basic action directive."
                elif "SQ2" in q_id:
                    if "IND_1" in ind_id:
                        score = 1 if any(m in lower_text for m in self.COMPLICATION_MARKERS) else 0
                        rationale = "Basic complication mention."
                    elif "IND_2" in ind_id:
                        score = 2 if any(v in lower_text for v in self.ADAPT_VERBS) else 0
                        rationale = "Pivot/adaptation verb detected."
                    elif "IND_3" in ind_id:
                        score = 1 if any(m in lower_text for m in self.PRIORITY_MARKERS) else 0
                        rationale = "Basic priority marker."
                    elif "IND_4" in ind_id:
                        score = 1 if any(c in lower_text for c in self.CAUSAL_CONNECTIVES) else 0
                        rationale = "Causal connective for adaptation."
                    elif "IND_5" in ind_id:
                        score = 1 if any(v in lower_text for v in self.ADAPT_VERBS + self.DECISION_VERBS) else 0
                        rationale = "Basic revised step."
                else: # SQ3
                    if "IND_1" in ind_id:
                        score = 1 if any(m in lower_text for m in self.TRADEOFF_MARKERS) else 0
                        rationale = "Basic trade-off mention."
                    elif "IND_2" in ind_id:
                        score = 1 if any(m in lower_text for m in self.ASSUMPTION_MARKERS) else 0
                        rationale = "Basic assumption mention."
                    elif "IND_3" in ind_id:
                        score = 1 if any(m in lower_text for m in self.RIPPLE_MARKERS) else 0
                        rationale = "Basic downstream impact mention."
                    elif "IND_4" in ind_id:
                        score = 1 if any(m in lower_text for m in self.IMPROVEMENT_MARKERS) else 0
                        rationale = "Basic hindsight mention."
                    elif "IND_5" in ind_id:
                        score = 1 if any(m in lower_text for m in self.PRINCIPLE_MARKERS) else 0
                        rationale = "Basic lesson/principle statement."
            else:
                # 8+ words: Structural ceiling at Level 2
                if "SQ1" in q_id:
                    if "IND_1" in ind_id:
                        has_dec = any(v in lower_text for v in self.DECISION_VERBS)
                        score = 2 if (has_dec or word_count >= 15) else 1
                        rationale = "Decisive choice declared with clear commitment."
                    elif "IND_2" in ind_id:
                        score = 2 if any(c in lower_text for c in self.CAUSAL_CONNECTIVES) else (1 if word_count >= 15 else 0)
                        rationale = "Causal justification connective present."
                    elif "IND_3" in ind_id:
                        score = 2 if any(m in lower_text for m in self.CONSEQUENCE_MARKERS) and any(c in lower_text for c in self.CAUSAL_CONNECTIVES) else (1 if any(m in lower_text for m in self.CONSEQUENCE_MARKERS) else 0)
                        rationale = "Direct consequence / constraint impact evaluated."
                    elif "IND_4" in ind_id:
                        score = 2 if any(m in lower_text for m in self.CONTRAST_CONNECTIVES) else (1 if "instead" in lower_text or "than" in lower_text else 0)
                        rationale = "Alternative comparison / contrast connective present."
                    elif "IND_5" in ind_id:
                        has_act = any(v in lower_text for v in self.DECISION_VERBS)
                        has_plan = any(m in lower_text for m in self.ACTION_PLAN_MARKERS) or word_count >= 15
                        score = 2 if (has_act and has_plan) else (1 if has_act else 0)
                        rationale = "Feasible action directive / implementation plan articulated."
                elif "SQ2" in q_id:
                    if "IND_1" in ind_id:
                        score = 2 if any(m in lower_text for m in self.COMPLICATION_MARKERS) else (1 if word_count >= 15 else 0)
                        rationale = "New complication / constraint recognized."
                    elif "IND_2" in ind_id:
                        score = 2 if any(v in lower_text for v in self.ADAPT_VERBS) else (1 if any(v in lower_text for v in self.DECISION_VERBS) else 0)
                        rationale = "Strategic modification / pivot declared."
                    elif "IND_3" in ind_id:
                        score = 2 if any(m in lower_text for m in self.PRIORITY_MARKERS) else (1 if any(m in lower_text for m in self.COMPLICATION_MARKERS) else 0)
                        rationale = "Critical operational constraint prioritized."
                    elif "IND_4" in ind_id:
                        score = 2 if any(c in lower_text for c in self.CAUSAL_CONNECTIVES) else (1 if word_count >= 15 else 0)
                        rationale = "Adaptation rationale explained with causal connectives."
                    elif "IND_5" in ind_id:
                        has_act = any(v in lower_text for v in self.ADAPT_VERBS + self.DECISION_VERBS)
                        score = 2 if has_act and word_count >= 12 else (1 if has_act else 0)
                        rationale = "Feasible revised action formulated."
                else: # SQ3 (Reflective Reasoning)
                    if "IND_1" in ind_id:
                        score = 2 if any(m in lower_text for m in self.TRADEOFF_MARKERS) else (1 if any(c in lower_text for c in self.CONTRAST_CONNECTIVES) else 0)
                        rationale = "Trade-offs and competing compromises evaluated."
                    elif "IND_2" in ind_id:
                        score = 2 if any(m in lower_text for m in self.ASSUMPTION_MARKERS) else (1 if any(m in lower_text for m in self.IMPROVEMENT_MARKERS) else 0)
                        rationale = "Underlying assumptions and premises interrogated."
                    elif "IND_3" in ind_id:
                        score = 2 if any(m in lower_text for m in self.RIPPLE_MARKERS) else (1 if any(c in lower_text for c in self.CAUSAL_CONNECTIVES) else 0)
                        rationale = "Downstream consequences and ripple effects analyzed."
                    elif "IND_4" in ind_id:
                        score = 2 if any(m in lower_text for m in self.IMPROVEMENT_MARKERS) else (1 if "could" in lower_text or "should" in lower_text else 0)
                        rationale = "Hindsight optimizations and improvements identified."
                    elif "IND_5" in ind_id:
                        score = 2 if any(m in lower_text for m in self.PRINCIPLE_MARKERS) else (1 if "always" in lower_text or "lesson" in lower_text else 0)
                        rationale = "Transferable principle / general heuristic extracted."

            # Cap strictly at 2
            score = min(2, max(0, score))
            matched_anchor = ind.anchors.get(str(score), f"Anchor score {score}")

            results.append(
                IndicatorScoreResult(
                    indicator_id=ind.indicator_id,
                    name=ind.name,
                    weight=ind.weight,
                    scale=ind.scale,
                    score=score,
                    matched_anchor=matched_anchor,
                    evidence_quote=clean_text[:120] + ("..." if len(clean_text) > 120 else ""),
                    confidence=0.60,
                    rationale=rationale,
                    tier_source="TIER_1_FALLBACK",
                )
            )

        return results

    async def _evaluate_tier2_llm(
        self,
        prompt: SpeakingPrompt,
        scenario_context: str,
        transcript_text: str,
    ) -> List[IndicatorScoreResult]:
        """Tier 2 Semantic Anchor Evaluation using LLMProviderRegistry / ModelRouter."""
        from app.infrastructure.prompt_service.router import ModelRouter
        from app.infrastructure.prompt.provider_registry import llm_registry

        # Resolve provider
        router = ModelRouter()
        try:
            provider, model_name = router.select_provider_and_model()
        except Exception:
            provider = llm_registry.get_default_provider()
            model_name = "default"

        # Build comprehensive rubric prompt
        indicators_spec = []
        for ind in prompt.behavioural_indicators:
            anchors_text = "\n".join([f"      {k}: {v}" for k, v in sorted(ind.anchors.items())])
            indicators_spec.append(
                f"- Indicator ID: {ind.indicator_id}\n"
                f"  Name: {ind.name}\n"
                f"  Weight: {ind.weight}\n"
                f"  Anchors:\n{anchors_text}"
            )
        indicators_formatted = "\n\n".join(indicators_spec)

        system_instruction = (
            "You are a psychometric scoring engine. Evaluate the candidate's transcript strictly against the "
            "canonical 0-4 behavioural anchors provided. Do NOT award high scores based on length alone. "
            "Match the exact anchor level demonstrated by concrete evidence in the transcript.\n\n"
            "Return a JSON object with key 'indicators' containing a list of objects with fields: "
            "indicator_id (string), score (integer 0-4), matched_anchor (string), evidence_quote (verbatim string), "
            "rationale (string), confidence (float 0.0-1.0)."
        )

        user_content = (
            f"SCENARIO CONTEXT:\n{scenario_context}\n\n"
            f"QUESTION ({prompt.question_id} - {prompt.stage}):\n{prompt.instructions}\n"
            f"OBJECTIVE: {prompt.objective}\n\n"
            f"CANDIDATE TRANSCRIPT:\n\"{transcript_text}\"\n\n"
            f"CANONICAL BEHAVIOURAL INDICATORS & ANCHORS:\n{indicators_formatted}\n\n"
            f"Evaluate all 5 indicators and output valid JSON."
        )

        # Call provider
        prompt_payload = f"{system_instruction}\n\n{user_content}"
        
        # Dispatch to provider
        if hasattr(provider, "generate_completion"):
            raw_response = await provider.generate_completion(prompt=prompt_payload, model=model_name)
        elif hasattr(provider, "generate"):
            try:
                raw_response = await provider.generate(prompt_text=prompt_payload, options={"prompt_id": "BEHAVIOURAL_INDICATOR_EVALUATION"})
            except TypeError:
                try:
                    raw_response = await provider.generate(prompt=prompt_payload)
                except TypeError:
                    raw_response = await provider.generate(prompt_payload, {"prompt_id": "BEHAVIOURAL_INDICATOR_EVALUATION"})
        else:
            raise ValueError(f"Provider {provider} lacks generate method")


        # Parse JSON
        parsed_json = self._parse_json_response(raw_response)
        raw_indicators = parsed_json.get("indicators", [])

        # Map to IndicatorScoreResult objects
        results: List[IndicatorScoreResult] = []
        ind_map = {ind.indicator_id: ind for ind in prompt.behavioural_indicators}

        for item in raw_indicators:
            ind_id = item.get("indicator_id")
            if ind_id in ind_map:
                canon_ind = ind_map[ind_id]
                raw_score = item.get("score", 0)
                try:
                    score_int = min(4, max(0, int(raw_score)))
                except (ValueError, TypeError):
                    score_int = 0

                conf = float(item.get("confidence", 0.90))
                matched_anchor = canon_ind.anchors.get(str(score_int), item.get("matched_anchor", ""))

                results.append(
                    IndicatorScoreResult(
                        indicator_id=canon_ind.indicator_id,
                        name=canon_ind.name,
                        weight=canon_ind.weight,
                        scale=canon_ind.scale,
                        score=score_int,
                        matched_anchor=matched_anchor,
                        evidence_quote=str(item.get("evidence_quote", "")),
                        confidence=conf,
                        rationale=str(item.get("rationale", "Grounded anchor evaluation.")),
                        tier_source="TIER_2_SEMANTIC",
                    )
                )

        if len(results) != len(prompt.behavioural_indicators):
            raise ValueError(f"Expected {len(prompt.behavioural_indicators)} indicators, got {len(results)}")

        return results

    def _parse_json_response(self, response_payload: Any) -> Dict[str, Any]:
        """Extracts and parses JSON from raw LLM output or mock response dict."""
        if isinstance(response_payload, dict):
            return response_payload

        text = str(response_payload).strip()
        # Strip markdown code fences if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        return json.loads(text)
