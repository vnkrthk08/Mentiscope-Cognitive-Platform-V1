# Mentiscope Cognitive Platform - Backend Service

High-performance cognitive testing and psychometric evaluation API service built with FastAPI, SQLite, and SQLAlchemy.

## Batteries Included

- **Processing Speed (Gs)**: Visual classification & reaction latency
- **Fluid Intelligence (Gf)**: Matrix reasoning & progressive rule discovery
- **Working Memory & Retrieval (Gsm)**: Dynamic memory retention & span
- **Executive Control & Attention (CSR)**: Selective & sustained attention
- **Visual Processing (Gv)**: Spatial rotation, paper folding, hidden figures
- **Quantitative Reasoning (Gq)**: Numerical reasoning & logic
- **Auditory & Verbal (Module 10)**: Dialogue comprehension & audio assessment
- **Candidate Session & Authentication**: JWT proctored session state in `mentiscope.db`

## Running Locally

In the `backend` directory:

```bash
# Install dependencies
pip install -r requirements.txt

# Start FastAPI server on port 8000
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## API Documentation

When the backend is running, interactive Swagger OpenAPI documentation is available at:
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`
