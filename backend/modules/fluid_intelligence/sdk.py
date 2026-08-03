"""Stable SDK serialization and export helpers for assessment sessions."""

from __future__ import annotations

import csv
import json
from io import StringIO
from pathlib import Path
from typing import Iterable

from .models import AssessmentSession, InteractionEvent, ScoreReport


class AssessmentSDK:
    """Export domain objects without exposing implementation-specific encoders."""

    @staticmethod
    def session_json(session: AssessmentSession, *, include_answers: bool = False, indent: int = 2) -> str:
        return json.dumps(session.to_dict(include_answers=include_answers), indent=indent, ensure_ascii=False)

    @staticmethod
    def events_csv(events: Iterable[InteractionEvent]) -> str:
        rows = [event.to_dict() for event in events]
        fields = [
            "event_id", "event_type", "assessment_id", "participant_id",
            "puzzle_id", "question_id", "option_id", "previous_option_id",
            "reaction_time_ms", "difficulty", "is_correct", "timestamp", "payload",
        ]
        output = StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            row["payload"] = json.dumps(row["payload"], ensure_ascii=False, separators=(",", ":"))
            writer.writerow(row)
        return output.getvalue()

    @staticmethod
    def score_csv(score: ScoreReport) -> str:
        output = StringIO(newline="")
        fields = ["scope", "ability", "raw_score", "maximum_score", "normalized_score", "percentile", "confidence_score"]
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerow({
            "scope": "overall", "ability": "", "raw_score": score.raw_score,
            "maximum_score": score.maximum_score, "normalized_score": score.normalized_score,
            "percentile": score.percentile, "confidence_score": score.confidence_score,
        })
        for subscore in score.subscores:
            writer.writerow({
                "scope": "subscore", "ability": subscore.ability.value,
                "raw_score": subscore.raw_score, "maximum_score": subscore.maximum_score,
                "normalized_score": subscore.normalized_score, "percentile": "", "confidence_score": "",
            })
        return output.getvalue()

    @staticmethod
    def write_text(content: str, destination: str | Path) -> Path:
        """Write UTF-8 export content and return the resolved destination."""

        path = Path(destination).expanduser().resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="")
        return path


__all__ = ["AssessmentSDK"]
