# Frontend integration — Classroom Scenario Recall (CSR / Gsm)

These files replace their same-named counterparts in the shared React
platform repo so that the "Working Memory (GSM)" module renders live
questions from the real CSR backend instead of the old client-side mock bank.

| File in this patch | Replaces / goes to |
|---|---|
| `services/modules/gsm.ts` | `src/services/modules/gsm.ts` (was a thin stub delegating to the mock `AssessmentService`; now calls `/api/modules/csr` directly, mirroring `processingSpeed.ts`) |
| `services/assessment/AssessmentService.ts` | `src/services/assessment/AssessmentService.ts` — added `GSMService` import and a `if (moduleId === "gsm") return GSMService....` branch in each of `startModule`, `submitAnswer`, `finishModule`, `getModuleResult` |
| `config/moduleConfig.ts` | `src/config/moduleConfig.ts` — the `gsm` entry's `apiBaseUrl` now points at `/api/modules/csr`, and name/description updated to reflect the CSR task battery |
| `config/questionsData.ts` | `src/config/questionsData.ts` — removed the old static `gsm: [...]` mock bank (module is now live-backed, same as `processing-speed` which never had a static entry) |
| `vite.config.ts` | project root `vite.config.ts` — added a dev-server proxy rule for `/api/modules/csr` alongside the existing `/api/modules/processing-speed` one |

## Running it end to end

```bash
# Terminal 1 — backend (serves both processing-speed and csr)
cd mentiscope_backend
python -m pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 — frontend
npm install
npm run dev
```

Open the app, start an assessment session, and the "Working Memory (GSM)"
module will run the Classroom Scenario Recall battery: 2 auditory-recall
trials (rendered via the runner's built-in `memory-span` sequence-flash UI),
2 visual grid-memory trials (`grid-pattern` UI), 4 distractor/interference
trials, and 2 sequential-recall trials — the last two rendered as multiple
choice among plausible re-orderings, since the shared runner has no
drag-to-reorder widget (the original `csr_prototype.html` prototype's
drag-and-drop interaction is not reproduced here; only the underlying task
logic and scoring are preserved).

## Known simplification vs. the HTML prototype

`csr_prototype.html` presents the auditory chunks one at a time with a
progress ring, and lets the user drag-reorder the sequential-recall list
directly. The shared platform's `AssessmentRunner` doesn't have hooks for
either interaction, so:

- Auditory recall uses the runner's existing `memory-span` flashing sequence
  view instead of the custom chunk-ring animation.
- Sequential recall is answered via multiple choice (server-generated
  plausible wrong orderings) instead of drag-and-drop.

The item content, scoring formulas, and mandatory output metadata are
unchanged from the approved prototype.
