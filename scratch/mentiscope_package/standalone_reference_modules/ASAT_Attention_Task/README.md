# ASAT: Adaptive Shape Attention Task

## Project Overview
ASAT is a cognitive assessment capsule designed to evaluate sustained, selective, divided, and executive attention. Originally an MVP, this project has been fully migrated and integrated to align with the standard **MentiScope** platform requirements. It functions as an independent Python microservice using FastAPI, integrating seamlessly via standardized API endpoints and PostgreSQL.

## Folder Structure
```
asat_mentiscope_integration/
├── backend/
│   ├── app/
│   │   ├── routers/       # FastAPI route handlers
│   │   ├── main.py        # Application entrypoint
│   │   ├── config.py      # Environment variables & DB settings
│   │   ├── database.py    # PostgreSQL connection and SQLAlchemy setup
│   │   ├── models.py      # Pydantic schemas (Request/Response)
│   │   └── schemas.py     # SQLAlchemy ORM schemas (Database tables)
│   ├── .env.example       # Example environment variables (No secrets)
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/               # Vanilla JS Vite source code
│   ├── index.html         # Frontend entrypoint
│   ├── package.json       # Node.js dependencies
│   └── vite.config.js     # Vite configuration (proxies API to backend)
├── module_config.json     # MentiScope module compliance configuration
├── database.sql           # PostgreSQL DDL for manual DB creation
├── postman_collection.json # API testing suite
└── README.md              # This document
```

## Technology Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy (Async), Uvicorn
- **Database**: PostgreSQL (asyncpg driver)
- **Frontend**: HTML5, Vanilla JavaScript, CSS, Vite
- **Architecture**: Modular REST API with MentiScope standardized endpoints

## Installation Steps

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 14+

### Environment Variables
1. Navigate to the `backend/` directory.
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Update `.env` with your local PostgreSQL credentials (do **not** commit this file).

### Database Setup
Ensure PostgreSQL is running locally and that you have created a database matching your `.env` configuration (default: `asat`).
When the FastAPI backend starts, SQLAlchemy will automatically detect and create all necessary tables matching `database.sql`.

### Running the Backend
1. Navigate to `backend/`
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Running the Frontend
1. Navigate to `frontend/`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Access the application at `http://localhost:5173`

## Swagger URL
Interactive API documentation is automatically generated and can be accessed while the backend is running at:
**[http://localhost:8000/docs](http://localhost:8000/docs)**

## API Overview

### MentiScope Standardized Endpoints
- `POST /api/start`: Initializes a new cognitive assessment session.
- `POST /api/answer`: Logs individual trial responses and metrics.
- `POST /api/finish`: Completes the session and stores the final calculated module scores.
- `GET /api/result/{session_id}`: Retrieves the final metrics for a completed session.

### Legacy Dashboard Endpoints (Retained for Compatibility)
- `POST /api/auth/register` & `/api/auth/login`: Faculty authentication.
- `POST /api/students`: Student registration.
- `GET /api/students`: Faculty dashboard data retrieval.
- `POST /api/sessions` & `POST /api/sessions/{id}/events` & `PATCH /api/sessions/{id}`: Legacy assessment data pipeline.

## Postman Usage
A fully configured `postman_collection.json` is included in the root directory. 
1. Import this file into Postman.
2. The collection includes step-by-step requests to simulate a complete assessment flow without using the frontend UI.
3. Ensure the backend is running locally on port `8000`.

## Integration Notes
- **API Proxy**: The frontend uses Vite's proxy in `vite.config.js` to automatically forward all `/api` requests to `http://127.0.0.1:8000`.
- **Stateless Configuration**: All database tables and connection URIs are driven purely by `.env`. There are no hardcoded secrets anywhere in the source code.
- **Auto-Migration**: The backend uses `Base.metadata.create_all` during startup to ensure tables exist.

## Known Assumptions
1. **Shared Schema Constraints**: The PostgreSQL tables use names directly translated from the MVP (e.g., `students`, `sessions`). These may need to be aliased or migrated once the final official MentiScope schema is provided.
2. **Authentication Flow**: The standard `/api/start` MentiScope endpoint currently does not enforce authentication (e.g., JWT). It assumes MentiScope platform handles authentication prior to invoking the capsule.
3. **Frontend Framework**: The frontend remains in Vanilla JS per Phase 1 approval. A React migration will be required in Phase 2.
