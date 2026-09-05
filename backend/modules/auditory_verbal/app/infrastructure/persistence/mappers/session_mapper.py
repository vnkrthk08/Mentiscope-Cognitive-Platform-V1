from datetime import datetime, timezone
from app.domain.entities.assessment_session import AssessmentSession, CandidateProgress
from app.domain.value_objects.enums import AssessmentStage, SessionStatus
from app.domain.entities.candidate_response import CandidateResponse, ListeningResponse, SpeakingResponse
from app.infrastructure.persistence.models.orm_models import AssessmentSessionORM


class SessionMapper:
    @staticmethod
    def to_orm(domain: AssessmentSession) -> AssessmentSessionORM:
        serialized_responses = []
        for r in domain.responses:
            if isinstance(r, ListeningResponse):
                serialized_responses.append({
                    "type": "LISTENING",
                    "response_id": r.response_id,
                    "session_id": r.session_id,
                    "prompt_id": r.prompt_id,
                    "timestamp": r.timestamp.isoformat(),
                    "selected_option_index": r.selected_option_index,
                    "response_time_ms": r.response_time_ms,
                })
            elif isinstance(r, SpeakingResponse):
                serialized_responses.append({
                    "type": "SPEAKING",
                    "response_id": r.response_id,
                    "session_id": r.session_id,
                    "prompt_id": r.prompt_id,
                    "timestamp": r.timestamp.isoformat(),
                    "audio_file_url": r.audio_file_url,
                    "duration_seconds": r.duration_seconds,
                    "transcript_text": r.transcript_text,
                    "acoustic_metadata": r.acoustic_metadata,
                })

        metadata_payload = dict(domain.metadata)
        metadata_payload["responses"] = serialized_responses

        curr_stage = domain.progress.current_stage.value if hasattr(domain.progress.current_stage, "value") else domain.progress.current_stage
        comp_stages = [s.value if hasattr(s, "value") else s for s in domain.progress.completed_stages]

        return AssessmentSessionORM(
            id=str(domain.session_id),
            candidate_id=domain.candidate_id,
            scenario_id=domain.scenario_id,
            status=domain.status.value,
            current_stage=curr_stage,
            completed_stages=comp_stages,
            metadata_json=metadata_payload,
        )

    @staticmethod
    def to_domain(orm: AssessmentSessionORM) -> AssessmentSession:
        def to_stage(s):
            try:
                return AssessmentStage(s)
            except ValueError:
                # Handle custom/non-standard stages gracefully
                return s

        progress = CandidateProgress(
            current_stage=to_stage(orm.current_stage),
            completed_stages=[to_stage(stage) for stage in orm.completed_stages],
            active_step_index=0,
            total_steps=12,
        )

        domain = AssessmentSession(
            session_id=str(orm.id),
            candidate_id=orm.candidate_id,
            scenario_id=orm.scenario_id,
            status=SessionStatus(orm.status),
            progress=progress,
            metadata={k: v for k, v in orm.metadata_json.items() if k != "responses"},
        )

        serialized_responses = orm.metadata_json.get("responses", [])
        for r in serialized_responses:
            ts = datetime.fromisoformat(r["timestamp"])
            if r["type"] == "LISTENING":
                resp = ListeningResponse(
                    response_id=r["response_id"],
                    session_id=r["session_id"],
                    prompt_id=r["prompt_id"],
                    timestamp=ts,
                    selected_option_index=r["selected_option_index"],
                    response_time_ms=r["response_time_ms"],
                )
            else:
                resp = SpeakingResponse(
                    response_id=r["response_id"],
                    session_id=r["session_id"],
                    prompt_id=r["prompt_id"],
                    timestamp=ts,
                    audio_file_url=r["audio_file_url"],
                    duration_seconds=r["duration_seconds"],
                    transcript_text=r.get("transcript_text"),
                    acoustic_metadata=r.get("acoustic_metadata", {}),
                )
            domain.add_response(resp)

        return domain
