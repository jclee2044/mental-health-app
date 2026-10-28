from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.features.emotion.domain import validate_entry
from app.errors import ValidationError


@pytest.fixture
def payload():
    return dict(feeling=3, color="#8FA98D", pleasantness=20, energy=-30,
                note="A fictional moment between tasks.", color_meaning="", recorded_at="2026-10-21T15:10:00Z", local_date="2026-10-21")


def test_domain_rejects_missing_explicit_choices(payload):
    for key, value in (("feeling", 0), ("feeling", True), ("color", "green"), ("pleasantness", 101), ("energy", None), ("recorded_at", "2026-10-21T12:00:00"), ("local_date", "2026-10-18"), ("note", "x" * 2001)):
        with pytest.raises(ValidationError) as failure:
            validate_entry({**payload, key: value})
        assert key in failure.value.fields


def test_entry_roundtrip_edit_delete_restart(tmp_path, payload):
    db_path = tmp_path / "test.sqlite3"
    entry_id = str(uuid4())
    with TestClient(create_app(db_path)) as client:
        created = client.put(f"/api/entries/{entry_id}", json=payload)
        assert created.status_code == 201
        assert created.json()["color"] == "#8fa98d"
        assert created.headers["cache-control"] == "no-store"
        assert len(client.get("/api/entries").json()["entries"]) == 1
        retry = client.put(f"/api/entries/{entry_id}", json=payload)
        assert retry.status_code == 200
        assert len(client.get("/api/entries").json()["entries"]) == 1
        second_id = str(uuid4())
        second = client.put(f"/api/entries/{second_id}", json={**payload, "note": "A second fictional moment on the same day."})
        assert second.status_code == 201
        daily = client.get("/api/entries").json()["entries"]
        assert len(daily) == 2
        assert {entry["local_date"] for entry in daily} == {"2026-10-21"}
        edited = client.put(f"/api/entries/{entry_id}", json={**payload, "note": "Changed fictional note", "recorded_at": "2026-10-22T15:00:00Z", "local_date": "2026-10-22"})
        assert edited.json()["recorded_at"] == created.json()["recorded_at"]
        assert edited.json()["local_date"] == "2026-10-21"
    with TestClient(create_app(db_path)) as client:
        assert client.get(f"/api/entries/{entry_id}").json()["note"] == "Changed fictional note"
        assert client.delete(f"/api/entries/{entry_id}").status_code == 204
        missing = client.get(f"/api/entries/{entry_id}")
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "not_found"
        assert len(client.get("/api/entries").json()["entries"]) == 1


def test_json_error_shapes_and_storage_failure(tmp_path, payload):
    with TestClient(create_app(tmp_path / "test.sqlite3")) as client:
        endpoint = f"/api/entries/{uuid4()}"
        for body in ({}, {**payload, "feeling": "3"}, {**payload, "extra": True}):
            result = client.put(endpoint, json=body)
            assert result.status_code == 422
            assert isinstance(result.json()["error"]["fields"], dict)
        assert client.put(endpoint, content="{bad", headers={"content-type": "application/json"}).status_code == 422
        client.app.state.emotion_store.database.path = tmp_path / "absent" / "unavailable.sqlite3"
        result = client.get("/api/entries")
        assert result.status_code == 503
        assert result.json()["error"]["code"] == "storage_unavailable"


def test_graph_only_entry_and_legacy_storage_compatibility(tmp_path, payload):
    """No inferred feeling; old NOT NULL databases work without destructive migration."""
    db_path = tmp_path / "existing.sqlite3"
    legacy_id, graph_id = str(uuid4()), str(uuid4())
    graph_payload = {key: value for key, value in payload.items() if key != "feeling"}
    with TestClient(create_app(db_path)) as client:
        assert client.put(f"/api/entries/{legacy_id}", json=payload).json()["feeling"] == 3
        saved = client.put(f"/api/entries/{graph_id}", json=graph_payload)
        assert saved.status_code == 201
        assert saved.json()["feeling"] is None
        assert client.put(f"/api/entries/{graph_id}", json={**graph_payload, "feeling": None}).status_code == 200
    with TestClient(create_app(db_path)) as client:
        records = {entry["id"]: entry for entry in client.get("/api/entries").json()["entries"]}
        assert records[legacy_id]["feeling"] == 3
        legacy_edit = client.put(f"/api/entries/{legacy_id}", json={**payload, "energy": 75})
        assert legacy_edit.json()["feeling"] == 3
        assert records[graph_id]["feeling"] is None
        edited = client.put(f"/api/entries/{graph_id}", json={**graph_payload, "energy": 75})
        assert edited.json()["energy"] == 75
        assert edited.json()["feeling"] is None
        assert client.get(f"/api/entries/{graph_id}").json()["feeling"] is None
