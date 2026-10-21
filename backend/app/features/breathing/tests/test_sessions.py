from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.errors import ValidationError
from app.features.breathing.domain import validate_session


@pytest.fixture
def session():
    return dict(pattern="paced-4-6-v1", status="completed", started_at="2026-10-21T15:00:00Z", ended_at="2026-10-21T15:01:03Z", local_date="2026-10-21", sequence_seconds=63, active_seconds=60, pause_seconds=0, instruction_seconds=73)


def test_fixed_pattern_and_invalid_completion(session):
    for key, value in (("pattern", "box"), ("active_seconds", 64), ("sequence_seconds", 50), ("pause_seconds", float("nan")), ("instruction_seconds", 10), ("ended_at", "2026-10-20T15:00:00Z")):
        with pytest.raises(ValidationError):
            validate_session({**session, key: value})
    assert validate_session({**session, "status": "ended", "sequence_seconds": 2, "active_seconds": 0})


def test_sessions_persist_once_and_keep_partial_separate(tmp_path, session):
    path = tmp_path / "test.sqlite3"
    session_id = str(uuid4())
    with TestClient(create_app(path)) as client:
        assert client.put(f"/api/sessions/{session_id}", json=session).status_code == 201
        assert client.put(f"/api/sessions/{session_id}", json=session).status_code == 200
        partial = {**session, "status": "ended", "sequence_seconds": 5, "active_seconds": 2, "pause_seconds": 10}
        assert client.put(f"/api/sessions/{uuid4()}", json=partial).status_code == 201
    with TestClient(create_app(path)) as client:
        result = client.get("/api/sessions")
        assert result.headers["cache-control"] == "no-store"
        assert len(result.json()["sessions"]) == 2
        assert {item["status"] for item in result.json()["sessions"]} == {"completed", "ended"}
