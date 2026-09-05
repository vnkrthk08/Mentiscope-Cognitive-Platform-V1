"""
Scenario Analytics Dashboard Telemetry Collector.
Tracks behavioral metrics, distributions, guard rejections, and repeated experience rates.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from collections import Counter


@dataclass
class ScenarioAnalyticsCollector:
    """Offline telemetry engine capturing scenario diversity and experience metrics."""

    categories: List[str] = field(default_factory=list)
    subcategories: List[str] = field(default_factory=list)
    intents: List[str] = field(default_factory=list)
    grammars: List[str] = field(default_factory=list)
    interaction_models: List[str] = field(default_factory=list)
    decision_types: List[str] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)
    structural_hashes: List[str] = field(default_factory=list)

    guard_1_structural_rejections: int = 0
    guard_2_semantic_rejections: int = 0
    generation_latencies_ms: List[float] = field(default_factory=list)

    def record_scenario(
        self,
        category: str,
        subcategory: str,
        intent: str,
        grammar: str,
        interaction_model: str,
        decision_type: str,
        title: str,
        structural_hash: str,
        latency_ms: float = 0.0,
    ):
        self.categories.append(category)
        self.subcategories.append(subcategory)
        self.intents.append(intent)
        self.grammars.append(grammar)
        self.interaction_models.append(interaction_model)
        self.decision_types.append(decision_type)
        self.titles.append(title)
        self.structural_hashes.append(structural_hash)

        if latency_ms > 0:
            self.generation_latencies_ms.append(latency_ms)

    def record_guard_rejection(self, guard_level: int):
        if guard_level == 1:
            self.guard_1_structural_rejections += 1
        elif guard_level == 2:
            self.guard_2_semantic_rejections += 1

    def analyze_scenario(self, scenario) -> Dict[str, Any]:
        """Analyzes a single scenario entity for structural telemetry."""
        listening_questions = getattr(scenario, "listening_questions", [])
        if not listening_questions and hasattr(scenario, "listening_module"):
            listening_questions = getattr(scenario.listening_module, "questions", [])

        speaking_prompts = getattr(scenario, "speaking_prompts", [])
        if not speaking_prompts and hasattr(scenario, "speaking_module"):
            speaking_prompts = getattr(scenario.speaking_module, "prompts", [])

        narr = getattr(scenario, "narrative", "")
        words = narr.split() if narr else []

        audio_asset = getattr(scenario, "audio_asset", None)
        duration_sec = getattr(audio_asset, "duration_seconds", 180.0) if audio_asset else 180.0

        return {
            "scenario_id": getattr(scenario, "scenario_id", "N/A"),
            "title": getattr(scenario, "title", "N/A"),
            "difficulty": getattr(scenario.difficulty, "value", str(getattr(scenario, "difficulty", "N/A"))),
            "listening_questions_count": len(listening_questions),
            "speaking_prompts_count": len(speaking_prompts),
            "word_count": len(words),
            "total_audio_duration_seconds": float(duration_sec),
            "estimated_reading_time_seconds": round(len(words) / 2.5, 1),
            "estimated_completion_time_minutes": round((len(words) / 150.0) + (float(duration_sec) / 60.0), 1),
        }

    def generate_report(self) -> Dict[str, Any]:
        total = len(self.titles)
        if total == 0:
            return {"status": "NO_DATA"}

        hash_counts = Counter(self.structural_hashes)
        repeated_hash_count = sum(c - 1 for c in hash_counts.values() if c > 1)
        repeated_experience_rate = round((repeated_hash_count / total) * 100, 2)

        avg_latency = (
            round(sum(self.generation_latencies_ms) / len(self.generation_latencies_ms), 2)
            if self.generation_latencies_ms
            else 0.0
        )

        return {
            "total_scenarios_generated": total,
            "repeated_experience_rate_pct": f"{repeated_experience_rate}%",
            "unique_categories": len(set(self.categories)),
            "unique_subcategories": len(set(self.subcategories)),
            "unique_intents": len(set(self.intents)),
            "unique_grammars": len(set(self.grammars)),
            "unique_interaction_models": len(set(self.interaction_models)),
            "unique_structural_hashes": len(set(self.structural_hashes)),
            "category_distribution": dict(Counter(self.categories)),
            "intent_distribution": dict(Counter(self.intents)),
            "grammar_distribution": dict(Counter(self.grammars)),
            "interaction_model_distribution": dict(Counter(self.interaction_models)),
            "guard_1_structural_rejections": self.guard_1_structural_rejections,
            "guard_2_semantic_rejections": self.guard_2_semantic_rejections,
            "avg_generation_latency_ms": avg_latency,
            "versions": {
                "assessment_skeleton_version": "2.0.0",
                "scenario_skeleton_version": "2.0.0",
                "grammar_version": "1.0.0",
                "interaction_model_version": "1.0.0",
                "prompt_version": "2.0.0",
                "taxonomy_version": "2.0.0",
            },
        }


# Alias for backward compatibility
ScenarioAnalytics = ScenarioAnalyticsCollector
