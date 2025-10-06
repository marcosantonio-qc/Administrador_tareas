import pytest
from datetime import date, time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.core.security import create_access_token
from app.models.models import RoleEnum, Room


client = TestClient(app)

def auth_header(role: RoleEnum = RoleEnum.admin):
    token = create_access_token(subject="admin@example.com", role=role)
    return {"Authorization": f"Bearer {token}"}


def test_create_event_conflict(monkeypatch):
    # Note: This is an integration-style test that assumes DB is available.
    # In CI, you may run against a test DB or mock the DB session.
    pass
