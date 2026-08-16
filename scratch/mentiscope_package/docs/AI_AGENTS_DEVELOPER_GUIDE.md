# 🤖 Mentiscope AI Agent & Developer Integration Guidelines

> **Target Audience**: AI Coding Assistants (AGY / Antigravity / Cursor / Claude / Copilot) and Developers working on this codebase.  
> **Primary Objective**: Ensure any new module or feature strictly adheres to Mentiscope's unified UI/UX design system, backend architecture, and standardized quiz rendering engine.

---

## 🛑 MANDATORY INTEGRATION DIRECTIVE: NO STANDALONE UI EMBEDDING

When adding or integrating new cognitive subtests/modules:

1. **NEVER** drop an isolated, standalone frontend app (e.g., separate Vite/React sub-app, external iframe, or custom unstyled page) into the user-facing portal.
2. **ALWAYS** extract only the **backend scoring algorithms, mathematical engines, item bank logic, and REST API endpoints**.
3. **ALWAYS** render the frontend items using Mentiscope's unified UI/UX design system, routing through `AssessmentRunner.tsx` or dedicated battery renderers (like `GVItemRenderer.tsx`).

---

## 🎨 UI/UX & Design System Architecture

All user-facing views MUST strictly follow Mentiscope's luxury aesthetic design system:

### 1. Color Palette & Visuals
- **Primary Background**: `bg-slate-950` / `bg-slate-900/90` with `backdrop-blur-2xl`
- **Borders & Dividers**: `border border-slate-800` / `border-slate-800/80`
- **Accents**:
  - Primary / Interactive: Vibrant Indigo (`from-blue-600 to-indigo-600`, `text-blue-400`)
  - Success / Accuracy: Emerald (`text-emerald-400`, `bg-emerald-950/60`, `border-emerald-800/60`)
  - Warning / Speed: Amber / Teal (`text-amber-400`, `text-teal-400`)
- **Typography**: Clean sans-serif with font-mono for quantitative scores and timed chronographs.

### 2. Standardized Quiz Layout Contract
Every cognitive assessment item MUST render inside a standardized quiz container featuring:
- **Header**: Domain Badge (e.g., `Gv · Visual Processing`), Item Index (`Item 3 of 12`), and Analog Chronograph / Timer.
- **Stimulus Box**: High-definition SVG graphic or structured question prompt (`item.stimulus` / `item.text`).
- **Response Input**: Keyboard-accessible choices, interactive SVG grid selections, or map placement slots.
- **Feedback Overlay**: AnimatePresence glassmorphism modal on submission with instant evaluation.

---

## ⚙️ Backend Module Architecture Standards

Every backend module MUST reside inside `backend/modules/<module_id>/` and implement the following FastAPI router contract:

```text
backend/modules/<module_id>/
├── api/
│   └── router.py          # FastAPI APIRouter mounted under /api/modules/<module_id>
├── engine/                # Core scoring algorithms & psychometric metrics
├── item_bank/             # Question schemas, SVG generators, or static JSON banks
├── models.py              # SQLAlchemy DB models
└── schemas.py             # Pydantic request/response schemas
```

### Required API Endpoints per Module
1. `POST /api/modules/<module_id>/start` — Initializes session & returns item list.
2. `POST /api/modules/<module_id>/answer` — Evaluates item response & returns score delta.
3. `POST /api/modules/<module_id>/finish` — Finalizes module score & returns subscores + recommendations.
4. `GET /api/modules/<module_id>/result/{session_id}` — Retrieves historical report.

---

## 💾 Database Persistence Standard ("ROM-Like Storage")

All candidate assessment records MUST be permanently archived in the SQLite database (`mentiscope.db`):
- Model: `SavedAssessmentSession` in `backend/core_models.py`.
- Endpoints: `/api/sessions/save`, `/api/sessions/history`, `/api/sessions/{session_id}`.
- Rule: Refreshing the browser or logging back in after days MUST retain full student history intact.

---

## 🚦 Navigation & Logged-In User Redirect Rule

- Authenticated users attempting to visit `/auth` or `/login` MUST automatically redirect to `/dashboard` (or `/admin`).
- Navigating to assessment modules MUST pass through `AssessmentService.getRunnerPage(moduleId)` to load the correct page route (`"assessment"` or dedicated route like `"gv-assessment"`).

---

## 🧪 Verification & Build Requirement

Before declaring any task complete:
1. Always run `npx vite build` to verify clean TypeScript compilation.
2. Never swallow exceptions or leave `return null;` in page components without fallback UI.
