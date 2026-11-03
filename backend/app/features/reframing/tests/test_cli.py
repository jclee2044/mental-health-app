"""Offline CLI smoke checks with temporary synthetic exports, never live vectors."""
import importlib.util
import json
from pathlib import Path

from app.features.reframing.corpus import load_corpus
from app.features.reframing.domain import digest, search_documents


def cli_module():
    path = Path(__file__).resolve().parents[5] / "scripts" / "reframing_kb.py"
    spec = importlib.util.spec_from_file_location("reframing_cli", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_offline_plan_publish_inspect_query_and_no_clobber(tmp_path, monkeypatch, capsys):
    cli = cli_module()
    monkeypatch.setattr(cli, "PROJECT", tmp_path)
    plan = tmp_path / "plan.json"
    assert cli.main(["plan", "--output", str(plan)]) == 0
    capsys.readouterr()
    data = json.loads(plan.read_text())
    assert len(data["documents"]) == 76
    assert cli.main(["plan", "--output", str(plan)]) == 2
    capsys.readouterr()
    export = {"schema_version": 1, "corpus_sha256": data["corpus_sha256"],
              "documents_sha256": data["documents_sha256"],
              "spec": {"provider": "openai", "model": "mock-only", "dimensions": 2},
              "rows": [{"id": d["id"], "sha256": d["sha256"], "vector": [1, 0] if d["card_id"] == "comparison" else [0, 1]} for d in data["documents"]]}
    vectors = tmp_path / "synthetic.json"
    vectors.write_text(json.dumps(export))
    index = tmp_path / "synthetic.sqlite3"
    assert cli.main(["publish", "--vectors", str(vectors), "--output", str(index)]) == 0
    capsys.readouterr()
    before = index.read_bytes()
    assert cli.main(["publish", "--vectors", str(vectors), "--output", str(index)]) == 2
    assert index.read_bytes() == before
    capsys.readouterr()
    common = ["--index", str(index), "--model", "mock-only", "--dimensions", "2"]
    assert cli.main(["inspect", *common]) == 0
    assert json.loads(capsys.readouterr().out)["documents"] == 76
    query = tmp_path / "query.json"
    query.write_text("[1,0]")
    assert cli.main(["query-vector", *common, "--vector-file", str(query), "--minimum-score", ".8"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["card_ids"] == ["comparison"]
    assert result["network"] == "none"
    assert "personal_memory" not in result["context"]
    assert index.read_bytes() == before


def test_bad_export_fails_before_creating_index(tmp_path, monkeypatch, capsys):
    cli = cli_module()
    monkeypatch.setattr(cli, "PROJECT", tmp_path)
    corpus = load_corpus()
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"schema_version": 1, "corpus_sha256": "stale", "documents_sha256": digest(search_documents(corpus)),
                                "spec": {"provider": "openai", "model": "mock-only", "dimensions": 2}, "rows": []}))
    destination = tmp_path / "not-created.sqlite3"
    assert cli.main(["publish", "--vectors", str(path), "--output", str(destination)]) == 2
    assert not destination.exists()
    assert "stale" not in capsys.readouterr().err


def test_output_paths_cannot_leave_project(tmp_path, monkeypatch, capsys):
    cli = cli_module()
    root = tmp_path / "project"
    root.mkdir()
    monkeypatch.setattr(cli, "PROJECT", root)
    outside = tmp_path / "outside.json"
    assert cli.main(["plan", "--output", str(outside)]) == 2
    assert not outside.exists()
