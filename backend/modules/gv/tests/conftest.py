from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# DATABASE_URL is read when backend/database.py is imported. The test command
# sets it explicitly; this fallback keeps direct pytest runs deterministic.
os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/mentiscope_gv_test.db")

from backend.database import Base, SessionLocal, engine  # noqa: E402
from backend.modules.gv.api.router import router  # noqa: E402


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/modules/gv")
    return TestClient(app)


@pytest.fixture()
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
