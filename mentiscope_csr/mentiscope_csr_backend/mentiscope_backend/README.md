# MentiScope — Classroom Scenario Recall (CSR) Module

Working Memory (Gsm) cognitive assessment microservice, built per the MentiScope
Intern Technical Development Guidelines. Implements the shared platform's
`/start`, `/answer`, `/finish`, `/result` contract on the common Postgres
schema — no separate database or standalone app.

This package also contains the previously-integrated **Processing Speed**
module (unmodified) so `main.py` runs as the full shared FastAPI app; only the
`modules/csr/` package is CSR's own deliverable.

## What CSR assesses

Four Gsm sub-components, run in fixed order, 10 trials total:

| Sub-component            | Task ID      | Trials | Item prefix |
|---------------------------|--------------|--------|--------------|
| Auditory Memory            | `auditory`   | 2      | `AUD-`       |
| Visual Memory               | `visual`     | 2      | `VIS-`       |
| Interference Resistance    | `distractor` | 4      | `DIS-`       |
| Sequential Recall (updating)| `sequential` | 2      | `SEQ-`       |

Content (chunk sequences, grid layouts, distractor prompts, sequence-update
puzzles) is ported directly from the approved `csr_prototype.html` MVP, and
exposed through the platform's shared `Question` schema so the existing
front-end AssessmentRunner can render it using its built-in `memory-span` and
`grid-pattern` question types, with plain `choice`-style multiple choice for
the distractor and sequential tasks.

## Install & Run

```bash
python -m pip install -r requirements.txt
uvicorn mentiscope_backend.main:app --reload --port 8000
```

By default this uses a local SQLite file (`mentiscope.db`) for convenience.
For the shared platform Postgres database, copy `.env.example` to `.env` and
set `DATABASE_URL` before starting the server.

The module is registered under `/api/modules/csr` and exposes:

- `POST /api/modules/csr/start`
- `POST /api/modules/csr/answer`
- `POST /api/modules/csr/finish`
- `GET  /api/modules/csr/result`

Interactive API docs: `http://localhost:8000/docs` (also exported statically
to `openapi.json` in this folder).

A ready-to-import `postman_collection.json` is included; set its `base_url`
variable to your running server.

## Request / response shapes

**POST /start**
```json
// request
{ "session_id": "S001", "student_id": "STU-DEMO-001" }
// response
{
  "status": "success",
  "totalQuestions": 10,
  "question": {
    "id": "csr-1",
    "text": "What was the third step?",
    "story": "...",
    "sequence": ["Take the beaker", "...", "..."],
    "options": ["heat to 60 degrees", "..."],
    "type": "memory-span",
    "difficulty_level": 1
  }
}
```

**POST /answer**
```json
// request
{ "session_id": "S001", "question_id": "csr-1", "answer": "heat to 60 degrees", "duration_ms": 1450 }
// response
{ "status": "success", "isCorrect": true, "feedback": "Chunk identified correctly.", "nextQuestion": { "...": "..." } }
```

**POST /finish** — returns the mandatory metadata block plus the `metrics`
object, per guideline §5/§6:
```json
{
  "status": "success",
  "scorePercentage": 82.5,
  "analytics": { "...": "the metrics object" },
  "output": {
    "student_id": "STU-DEMO-001",
    "session_id": "S001",
    "module_id": "csr",
    "module_name": "Classroom Scenario Recall (Working Memory / Gsm)",
    "construct": "Gsm",
    "status": "Completed",
    "start_time": "2026-07-15T10:00:00+00:00",
    "end_time": "2026-07-15T10:03:12+00:00",
    "completion_time": 192,
    "timestamp": "2026-07-15T10:03:12+00:00",
    "metrics": {
      "raw_score": 82.5,
      "normalized_score": 104.5,
      "percentile": 59,
      "confidence_score": 0.82,
      "sub_scores": {
        "auditory_memory": 100.0,
        "visual_memory": 100.0,
        "interference_resistance": 75.0,
        "sequential_recall": 50.0
      },
      "accuracy": 80.0,
      "average_reaction_time_ms": 1310,
      "recommendations": ["Sequential updating below expected band; monitor multi-step instruction following."]
    }
  }
}
```

**GET /result?session_id=...** returns `{ "moduleId": "csr", "score": ..., "analytics": {...} }`.

## Scoring model

- Each sub-component score = percentage correct within that task's trials.
- `raw_score` = mean of the four sub-scores (25% weighting each, matching the
  original prototype's Evaluation Report §5 model).
- `normalized_score = 100 + (raw_score - 75) * 0.6`
- `percentile = clamp(1, 99, round(50 + (raw_score - 75) * 1.2))`
- `confidence_score` = 0.82 with ≥8 responses, else 0.55 (low-N caution flag).

This is the same placeholder normalization used in the prototype — real
normative data collection is deferred to the pilot phase per the Evaluation
Report's Sprint 2 plan (N≥100).

## Persistence

Uses only the shared tables — `sessions`, `responses`, `events`, `results`,
`analytics` — with `module_id = "csr"`. No CSR-specific table is created. See
`modules/csr/module_config.json` for the structured module descriptor.

## Testing

The module was validated end-to-end with FastAPI's `TestClient`:
run a full 10-trial session, confirm per-sub-component scoring against
known-correct answers, and confirm error responses (`404` for a missing
result, `409` for an answer submitted against a stale/mismatched
`question_id`).

## Not yet done (out of scope for this delivery)

- The shared React frontend has been updated (`moduleConfig.ts`,
  `questionsData.ts` placeholder removed, `CsrService.ts` added) so CSR
  appears as a selectable module and calls this backend — see the frontend
  diff notes in the accompanying message. The drag-and-reorder interaction
  and the auditory chunk-by-chunk reveal from `csr_prototype.html` are
  simplified on the shared runner to fit its generic `memory-span` /
  `grid-pattern` / `choice` question types; a fully bespoke UI (matching the
  prototype's visuals 1:1) is not implemented here.
- 5–10 minute demo video (not producible in this environment).
