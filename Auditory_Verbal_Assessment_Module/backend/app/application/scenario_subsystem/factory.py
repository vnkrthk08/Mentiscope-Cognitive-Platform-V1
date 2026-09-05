import logging
from typing import Any, Dict, List
from app.domain.entities.scenario import Scenario
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.entities.behavioural_indicator import BehaviouralIndicator
from app.domain.entities.follow_up_question import FollowUpQuestion
from app.domain.value_objects.audio_asset import AudioAsset
from app.domain.value_objects.time_limit import TimeLimit
from app.domain.value_objects.scenario_version import ScenarioVersion
from app.domain.value_objects.enums import ConstructType, DifficultyLevel
from app.domain.assessment.speaking_canonical_config import CANONICAL_SPEAKING_SPECS

logger = logging.getLogger(__name__)


class ScenarioFactory:
    """Factory transforming raw dictionary configurations into immutable Domain Entities."""

    def create_from_dict(self, data: Dict[str, Any]) -> Scenario:
        scenario_id = data["id"]
        title = data["title"]
        narrative = data["narrative"]
        version = ScenarioVersion(data.get("version", "1.0.0"))
        difficulty = DifficultyLevel(data.get("difficulty", "INTERMEDIATE").upper())

        # Hydrate Audio Asset
        raw_audio = data.get("audio_asset", {})
        audio_asset = AudioAsset(
            url=raw_audio.get("url", raw_audio.get("file_path", f"/audio/scenarios/{scenario_id}.mp3")),
            duration_seconds=float(raw_audio.get("duration_seconds", 180.0)),
            format=raw_audio.get("format", "audio/mp3"),
        )

        # Hydrate Listening Questions
        listening_questions: List[ListeningQuestion] = []
        raw_lq_list = (
            data.get("listening_module", {}).get("questions")
            or data.get("listening_questions")
            or []
        )
        for q in raw_lq_list:
            lq = ListeningQuestion(
                question_id=q.get("id") or q.get("question_id", "LQ_0"),
                prompt=q.get("prompt") or q.get("question_text", ""),
                options=q.get("options", []),
                correct_option_index=int(q.get("correct_option_index", 0)),
                target_construct=ConstructType.from_str(q.get("target_construct", "LISTENING_COMPREHENSION")),
                difficulty=DifficultyLevel(q.get("difficulty", "INTERMEDIATE").upper()),
                points=int(q.get("points", 10)),
                max_replays=int(q.get("max_replays", 2)),
                secondary_constructs=[ConstructType.from_str(sc) for sc in q.get("secondary_constructs", [])],
                question_type=q.get("question_type", "Detail"),
                cognitive_objective=q.get("cognitive_objective", ""),
                expected_evidence=q.get("expected_evidence", {}),
                weight=float(q.get("weight", 1.0)),
            )
            listening_questions.append(lq)

        # Hydrate Speaking Prompts
        speaking_prompts: List[SpeakingPrompt] = []
        raw_sp_list = (
            data.get("speaking_questions")
            or data.get("speaking_prompts")
            or data.get("speaking_module", {}).get("prompts")
            or []
        )

        for idx, p in enumerate(raw_sp_list):
            q_id = p.get("question_id") or f"SQ{idx + 1}"
            canonical_spec = CANONICAL_SPEAKING_SPECS.get(q_id, CANONICAL_SPEAKING_SPECS.get(f"SQ{idx + 1}"))

            stage = p.get("stage") or (canonical_spec["stage"] if canonical_spec else "STAGE_1_DECISION")
            objective = p.get("objective") or (canonical_spec["objective"] if canonical_spec else "")
            max_score = float(p.get("max_indicator_weighted_score", canonical_spec["max_indicator_weighted_score"] if canonical_spec else 18.4))

            # Primary constructs
            if "primary_constructs" in p and p["primary_constructs"]:
                primary_constructs = [ConstructType.from_str(c) for c in p["primary_constructs"]]
            elif canonical_spec:
                primary_constructs = list(canonical_spec["primary_constructs"])
            elif "target_constructs" in p:
                primary_constructs = [ConstructType.from_str(c) for c in p["target_constructs"]]
            else:
                primary_constructs = [ConstructType.DECISION_MAKING]

            # Secondary constructs
            if "secondary_constructs" in p and p["secondary_constructs"]:
                secondary_constructs = [ConstructType.from_str(c) for c in p["secondary_constructs"]]
            elif canonical_spec:
                secondary_constructs = list(canonical_spec["secondary_constructs"])
            else:
                secondary_constructs = [ConstructType.COMMUNICATION]

            # Behavioural indicators
            indicators = []
            if "behavioural_indicators" in p and p["behavioural_indicators"]:
                for ind in p["behavioural_indicators"]:
                    if isinstance(ind, BehaviouralIndicator):
                        indicators.append(ind)
                    elif isinstance(ind, dict):
                        indicators.append(BehaviouralIndicator.from_dict(ind))
            elif canonical_spec:
                indicators = list(canonical_spec["behavioural_indicators"])

            time_limit_sec = int(p.get("max_time_seconds", p.get("max_seconds", 120)))
            if "time_limit" in p and isinstance(p["time_limit"], dict):
                time_limit_sec = int(p["time_limit"].get("max_seconds", 120))

            sp = SpeakingPrompt(
                prompt_id=p.get("prompt_id") or p.get("id") or f"{q_id}_{scenario_id}",
                question_id=q_id,
                stage=stage,
                title=p.get("title", f"Speaking Task {idx + 1}"),
                instructions=p.get("instructions", ""),
                objective=objective,
                primary_constructs=primary_constructs,
                secondary_constructs=secondary_constructs,
                behavioural_indicators=indicators,
                time_limit=TimeLimit(max_seconds=time_limit_sec),
                max_indicator_weighted_score=max_score,
                followup_eligible=bool(p.get("followup_eligible", True)),
            )
            speaking_prompts.append(sp)

        # Legacy fallback if only 1 prompt exists: synthesize SQ2 and SQ3 grounded in scenario
        if len(speaking_prompts) == 1:
            logger.info(f"[LegacyMigration] ScenarioFactory: Scenario {scenario_id} contains 1 prompt. Injecting canonical SQ2 and SQ3.")
            sp1 = speaking_prompts[0]
            sp1.question_id = "SQ1"
            sp1.stage = "STAGE_1_DECISION"
            sp1.objective = CANONICAL_SPEAKING_SPECS["SQ1"]["objective"]
            sp1.primary_constructs = CANONICAL_SPEAKING_SPECS["SQ1"]["primary_constructs"]
            sp1.secondary_constructs = CANONICAL_SPEAKING_SPECS["SQ1"]["secondary_constructs"]
            sp1.behavioural_indicators = CANONICAL_SPEAKING_SPECS["SQ1"]["behavioural_indicators"]

            raw_fu = data.get("follow_ups", [])
            fu_text = raw_fu[0].get("prompt_text", "") if raw_fu else data.get("fu_prompt", "")

            sq2_instructions = fu_text or f"Suppose unexpected constraints arise 15 minutes before the deadline for '{title}'. How would you pivot your original plan to ensure operational continuity?"
            sp2 = SpeakingPrompt(
                prompt_id=f"SQ2_{scenario_id}",
                question_id="SQ2",
                stage="STAGE_2_CHALLENGE",
                title=f"Adaptive Challenge: {title}",
                instructions=sq2_instructions,
                objective=CANONICAL_SPEAKING_SPECS["SQ2"]["objective"],
                primary_constructs=CANONICAL_SPEAKING_SPECS["SQ2"]["primary_constructs"],
                secondary_constructs=CANONICAL_SPEAKING_SPECS["SQ2"]["secondary_constructs"],
                behavioural_indicators=CANONICAL_SPEAKING_SPECS["SQ2"]["behavioural_indicators"],
                time_limit=TimeLimit(max_seconds=120),
                max_indicator_weighted_score=18.4,
                followup_eligible=True,
            )

            sp3 = SpeakingPrompt(
                prompt_id=f"SQ3_{scenario_id}",
                question_id="SQ3",
                stage="STAGE_3_REFLECTIVE",
                title=f"Reflective Reasoning: {title}",
                instructions=f"Reflecting on the trade-offs in '{title}', what key assumptions did you make, and what transferable principle would you apply to similar future situations?",
                objective=CANONICAL_SPEAKING_SPECS["SQ3"]["objective"],
                primary_constructs=CANONICAL_SPEAKING_SPECS["SQ3"]["primary_constructs"],
                secondary_constructs=CANONICAL_SPEAKING_SPECS["SQ3"]["secondary_constructs"],
                behavioural_indicators=CANONICAL_SPEAKING_SPECS["SQ3"]["behavioural_indicators"],
                time_limit=TimeLimit(max_seconds=120),
                max_indicator_weighted_score=18.4,
                followup_eligible=True,
            )
            speaking_prompts = [sp1, sp2, sp3]

        # Hydrate Follow-Up Questions (optional)
        follow_ups: List[FollowUpQuestion] = []
        raw_followups = data.get("follow_ups", [])
        for f in raw_followups:
            fq = FollowUpQuestion(
                followup_id=f.get("id") or f.get("followup_id", "FU_0"),
                parent_prompt_id=f.get("parent_prompt_id", "SQ1"),
                prompt_text=f.get("prompt_text", ""),
                target_construct=ConstructType.from_str(f.get("target_construct", "ADAPTABILITY")),
                priority=int(f.get("priority", 1)),
                trigger_conditions=f.get("trigger_conditions", {}),
                expected_evidence_pattern=f.get("expected_evidence_pattern", ""),
                time_limit=TimeLimit(max_seconds=int(f.get("max_time_seconds", 90))),
            )
            follow_ups.append(fq)

        # Aggregate Construct Mappings
        construct_mappings: List[ConstructType] = []
        for q in listening_questions:
            if q.target_construct not in construct_mappings:
                construct_mappings.append(q.target_construct)
        for p in speaking_prompts:
            for c in p.primary_constructs + p.secondary_constructs:
                if c not in construct_mappings:
                    construct_mappings.append(c)

        return Scenario(
            scenario_id=scenario_id,
            title=title,
            narrative=narrative,
            audio_asset=audio_asset,
            listening_questions=listening_questions,
            speaking_prompts=speaking_prompts,
            version=version,
            difficulty=difficulty,
            follow_up_definitions=follow_ups,
            construct_mappings=construct_mappings,
            metadata=data.get("metadata", {}),
        )
