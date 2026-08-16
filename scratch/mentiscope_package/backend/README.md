# ⚙️ Mentiscope Psychometric Backend API
- **Framework**: FastAPI (Python 3.11+) + Uvicorn
- **ORM & DB**: SQLAlchemy + SQLite (`mentiscope.db`)
- **Validation**: Pydantic v2

### Local Execution:
```bash
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Interactive API Documentation:
Visit `http://localhost:8000/docs` (Swagger UI) or `http://localhost:8000/redoc`.
