from fastapi.testclient import TestClient
from app.main import create_app


def test_static_shell_survives_unavailable_database(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "index.html").write_text("<h1>Still</h1>")
    blocker = tmp_path / "file-not-directory"
    blocker.write_text("blocker")
    with TestClient(create_app(blocker / "db.sqlite3", dist)) as client:
        assert client.get("/").status_code == 200
        assert "Still" in client.get("/").text
        assert client.get("/api/entries").status_code == 503
        missing = client.get("/api/missing")
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "not_found"
