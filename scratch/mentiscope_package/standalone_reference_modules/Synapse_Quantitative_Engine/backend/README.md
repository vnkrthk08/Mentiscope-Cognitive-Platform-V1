# MentiScope - Quantitative Ability (Gq) Assessment

This is an independent Python microservice for the MentiScope Cognitive Assessment Platform.
It evaluates Quantitative Ability (Gq) using dynamic, adaptive questions.

## Features
- **Adaptive Question Routing**: Uses Item Response Theory to adjust difficulty.
- **Item Exposure Control**: Prevents consecutive identical template tests.
- **Comprehensive Analytics**: Computes reaction time, accuracy, and confidence.
- **REST API**: Standard endpoints for Start, Answer, and Result phases.

## Technology Stack
- **Backend**: Python 3.11+, FastAPI
- **Database**: PostgreSQL (fallback to SQLite configured in `.env` if not provided)
- **Frontend**: React (Vite)

## Installation & Setup

1. **Clone the repository** (or extract the module archive).
2. **Setup virtual environment**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Configuration**:
   The `.env` file must be configured with a PostgreSQL `DATABASE_URL`. Alternatively, `database.py` defaults to `sqlite:///./mentiscope.db` for local testing.
5. **Initialize Database**:
   The `init_db.py` script automatically creates all required tables and populates the question templates.
   ```bash
   python -m app.database.init_db
   ```
6. **Run the Server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Standard Assessment Flow

The assessment flows through 4 REST API endpoints:
1. `POST /api/start` - Initializes the session and returns the first question.
2. `POST /api/answer` - Submits a student response and telemetry, and calculates the next question based on the adaptive engine.
3. `POST /api/finish` - Marks the assessment session as complete.
4. `GET /api/result/{session_id}` - Generates the unified `metrics` and standard metadata response payload required by the MentiScope Scoring Engine.

## Deliverables Included
- `README.md`: This file.
- `requirements.txt`: Python dependencies.
- `database.sql`: Required schema definitions.
- `module_config.json`: Standard module definition.
