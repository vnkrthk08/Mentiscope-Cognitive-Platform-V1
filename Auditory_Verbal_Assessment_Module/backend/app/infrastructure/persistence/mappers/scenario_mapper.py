import logging
from app.domain.entities.scenario import Scenario
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.entities.behavioural_indicator import BehaviouralIndicator
from app.domain.entities.follow_up_question import FollowUpQuestion
from app.domain.value_objects.audio_asset import AudioAsset
from app.domain.value_objects.enums import ConstructType, DifficultyLevel
from app.domain.value_objects.scenario_version import ScenarioVersion
from app.domain.value_objects.time_limit import TimeLimit
from app.domain.assessment.speaking_canonical_config import CANONICAL_SPEAKING_SPECS
from app.infrastructure.persistence.models.orm_models import ScenarioORM

logger = logging.getLogger(__name__)


class ScenarioMapper:
    @staticmethod
    def to_orm(domain: Scenario) -> ScenarioORM:
        return ScenarioORM(
            id=domain.scenario_id,
            title=domain.title,
            narrative=domain.narrative,
            audio_asset={
                "url": domain.audio_asset.url,
                "duration_seconds": domain.audio_asset.duration_seconds,
                "format": domain.audio_asset.format,
            },
            listening_questions=[
                {
                    "question_id": q.question_id,
                    "prompt": q.prompt,
                    "options": q.options,
                    "correct_option_index": q.correct_option_index,
                    "target_construct": q.target_construct.value,
                    "difficulty": q.difficulty.value,
                    "points": q.points,
                    "max_replays": q.max_replays,
                    "secondary_constructs": [sc.value for sc in q.secondary_constructs],
                    "question_type": q.question_type,
                    "cognitive_objective": q.cognitive_objective,
                    "expected_evidence": q.expected_evidence,
                    "weight": q.weight,
                }
                for q in domain.listening_questions
            ],
            speaking_prompts=[
                {
                    "question_id": p.question_id,
                    "prompt_id": p.prompt_id,
                    "stage": p.stage,
                    "title": p.title,
                    "instructions": p.instructions,
                    "objective": p.objective,
                    "primary_constructs": [c.value for c in p.primary_constructs],
                    "secondary_constructs": [c.value for c in p.secondary_constructs],
                    "behavioural_indicators": [
                        ind.to_dict() if hasattr(ind, "to_dict") else ind
                        for ind in p.behavioural_indicators
                    ],
                    "time_limit": {"max_seconds": p.time_limit.max_seconds},
                    "max_indicator_weighted_score": p.max_indicator_weighted_score,
                    "target_constructs": [c.value for c in p.target_constructs],
                    "followup_eligible": p.followup_eligible,
                }
                for p in domain.speaking_prompts
            ],
            follow_up_definitions=[
                {
                    "followup_id": f.followup_id,
                    "parent_prompt_id": f.parent_prompt_id,
                    "prompt_text": f.prompt_text,
                    "target_construct": f.target_construct.value,
                    "priority": f.priority,
                    "trigger_conditions": f.trigger_conditions,
                    "expected_evidence_pattern": f.expected_evidence_pattern,
                    "time_limit": {"max_seconds": f.time_limit.max_seconds},
                }
                for f in domain.follow_up_definitions
            ],
            construct_mappings=[c.value for c in domain.construct_mappings],
            metadata_json=domain.metadata,
        )

    @staticmethod
    def to_domain(orm: ScenarioORM) -> Scenario:
        speaking_prompts_list = []
        raw_prompts = orm.speaking_prompts or []

        for idx, p in enumerate(raw_prompts):
            q_id = p.get("question_id") or f"SQ{idx + 1}"
            canonical_spec = CANONICAL_SPEAKING_SPECS.get(q_id, CANONICAL_SPEAKING_SPECS.get(f"SQ{idx + 1}"))

            # Extract or fallback to canonical stage
            stage = p.get("stage") or (canonical_spec["stage"] if canonical_spec else "STAGE_1_DECISION")
            objective = p.get("objective") or (canonical_spec["objective"] if canonical_spec else "")
            max_score = float(p.get("max_indicator_weighted_score", canonical_spec["max_indicator_weighted_score"] if canonical_spec else 18.4))

            # Primary constructs
            if "primary_constructs" in p and p["primary_constructs"]:
                primary_constructs = [ConstructType.from_str(c) for c in p["primary_constructs"]]
            elif canonical_spec:
                primary_constructs = list(canonical_spec["primary_constructs"])
            else:
                primary_constructs = [ConstructType.from_str(c) for c in p.get("target_constructs", ["DECISION_MAKING"])]

            # Secondary constructs
            if "secondary_constructs" in p:
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

            time_limit_sec = 120
            if "time_limit" in p and isinstance(p["time_limit"], dict):
                time_limit_sec = int(p["time_limit"].get("max_seconds", 120))
            elif "max_seconds" in p:
                time_limit_sec = int(p["max_seconds"])

            sp = SpeakingPrompt(
                prompt_id=p.get("prompt_id") or f"{q_id}_{orm.id}",
                question_id=q_id,
                stage=stage,
                title=p.get("title", f"Speaking Task {idx + 1}"),
                instructions=p.get("instructions") if (p.get("instructions") and p.get("instructions").strip()) else (p.get("title") or f"Describe your operational strategy and decision-making rationale for scenario '{orm.title}' under the given constraints."),
                objective=objective,
                primary_constructs=primary_constructs,
                secondary_constructs=secondary_constructs,
                behavioural_indicators=indicators,
                time_limit=TimeLimit(max_seconds=time_limit_sec),
                max_indicator_weighted_score=max_score,
                followup_eligible=p.get("followup_eligible", True),
            )
            speaking_prompts_list.append(sp)

        # Legacy fallback if only 1 prompt exists: synthesize SQ2 and SQ3 grounded in scenario
        if len(speaking_prompts_list) == 1:
            logger.info(f"[LegacyMigration] Scenario {orm.id} contains only 1 prompt. Injecting canonical SQ2 and SQ3.")
            sp1 = speaking_prompts_list[0]
            sp1.question_id = "SQ1"
            sp1.stage = "STAGE_1_DECISION"
            sp1.objective = CANONICAL_SPEAKING_SPECS["SQ1"]["objective"]
            sp1.primary_constructs = CANONICAL_SPEAKING_SPECS["SQ1"]["primary_constructs"]
            sp1.secondary_constructs = CANONICAL_SPEAKING_SPECS["SQ1"]["secondary_constructs"]
            sp1.behavioural_indicators = CANONICAL_SPEAKING_SPECS["SQ1"]["behavioural_indicators"]

            fu_text = ""
            if getattr(orm, "follow_up_definitions", None) and len(orm.follow_up_definitions) > 0:
                fu_text = orm.follow_up_definitions[0].get("prompt_text", "")

            sq2_instructions = fu_text or f"Suppose unexpected constraints arise 15 minutes before the deadline for '{orm.title}'. How would you pivot your original plan to ensure operational continuity?"
            sp2 = SpeakingPrompt(
                prompt_id=f"SQ2_{orm.id}",
                question_id="SQ2",
                stage="STAGE_2_CHALLENGE",
                title=f"Adaptive Challenge: {orm.title}",
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
                prompt_id=f"SQ3_{orm.id}",
                question_id="SQ3",
                stage="STAGE_3_REFLECTIVE",
                title=f"Reflective Reasoning: {orm.title}",
                instructions=f"Reflecting on the trade-offs in '{orm.title}', what key assumptions did you make, and what transferable principle would you apply to similar future situations?",
                objective=CANONICAL_SPEAKING_SPECS["SQ3"]["objective"],
                primary_constructs=CANONICAL_SPEAKING_SPECS["SQ3"]["primary_constructs"],
                secondary_constructs=CANONICAL_SPEAKING_SPECS["SQ3"]["secondary_constructs"],
                behavioural_indicators=CANONICAL_SPEAKING_SPECS["SQ3"]["behavioural_indicators"],
                time_limit=TimeLimit(max_seconds=120),
                max_indicator_weighted_score=18.4,
                followup_eligible=True,
            )
            speaking_prompts_list = [sp1, sp2, sp3]

        return Scenario(
            scenario_id=orm.id,
            title=orm.title,
            narrative=orm.narrative,
            audio_asset=AudioAsset(
                url=orm.audio_asset.get("url", orm.audio_asset.get("file_path", "audio/mp3")),
                duration_seconds=orm.audio_asset["duration_seconds"],
                format=orm.audio_asset.get("format", "audio/mp3"),
            ),
            listening_questions=[
                ListeningQuestion(
                    question_id=q.get("question_id") or q.get("id", "LQ_0"),
                    prompt=q.get("prompt") or q.get("question_text", ""),
                    options=q.get("options", []),
                    correct_option_index=q.get("correct_option_index", 0),
                    target_construct=ConstructType.from_str(q["target_construct"]),
                    difficulty=DifficultyLevel(q["difficulty"]),
                    points=q.get("points", 10),
                    max_replays=q.get("max_replays", 2),
                    secondary_constructs=[ConstructType.from_str(sc) for sc in q.get("secondary_constructs", [])],
                    question_type=q.get("question_type", "Detail"),
                    cognitive_objective=q.get("cognitive_objective", ""),
                    expected_evidence=q.get("expected_evidence", {}),
                    weight=float(q.get("weight", 1.0)),
                )
                for q in orm.listening_questions
            ],
            speaking_prompts=speaking_prompts_list,
            version=ScenarioVersion(version_str="1.0.0"),
            difficulty=DifficultyLevel(orm.listening_questions[0]["difficulty"]) if orm.listening_questions else DifficultyLevel.INTERMEDIATE,
            follow_up_definitions=[
                FollowUpQuestion(
                    followup_id=f.get("followup_id") or f.get("id", "FU_0"),
                    parent_prompt_id=f.get("parent_prompt_id", "S_P1"),
                    prompt_text=f.get("prompt_text", ""),
                    target_construct=ConstructType.from_str(f["target_construct"]),
                    priority=f.get("priority", 1),
                    trigger_conditions=f.get("trigger_conditions", {}),
                    expected_evidence_pattern=f.get("expected_evidence_pattern", ""),
                    time_limit=TimeLimit(max_seconds=f.get("time_limit", {}).get("max_seconds", 60.0) if isinstance(f.get("time_limit"), dict) else float(f.get("max_seconds", 60.0))),
                )
                for f in (getattr(orm, "follow_up_definitions", getattr(orm, "follow_ups", [])) or [])
            ],
            construct_mappings=[ConstructType(c) for c in orm.construct_mappings],
            metadata=orm.metadata_json,
        )
