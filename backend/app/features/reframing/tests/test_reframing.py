"""Fictional content + synthetic vectors/HTTP mocks; no semantic/model claims."""
import copy
import json
import math
import sqlite3
from email.message import Message
from pathlib import Path
from types import SimpleNamespace
from urllib.error import HTTPError, URLError

import pytest

from app.features.reframing import register
from app.features.reframing.corpus import load_corpus
from app.features.reframing.domain import (
    FAMILIES, REFERENCE_POLICY, IndexUnavailable, InvalidKnowledge, canonical,
    embedding_spec, rank, reference_context, search_documents, strict_json,
    unit_vector, validate_corpus,
)
from app.features.reframing.embeddings import EmbeddingUnavailable, OpenAIEmbedder
from app.features.reframing import embeddings
from app.features.reframing.service import ReframingService
from app.features.reframing.storage import IndexStore

SPEC = {"provider": "openai", "model": "mock-only-never-call", "dimensions": 3}


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def fail(*_args, **_kwargs):
        pytest.fail("Unexpected network attempt")
    monkeypatch.setattr(embeddings, "open_embedding_request", fail)


@pytest.fixture
def corpus():
    return load_corpus()


def vector_rows(corpus):
    # Deliberately synthetic directions: tests only the scoring/provenance mechanics.
    return [{"id": d["id"], "sha256": d["sha256"], "vector": [1, 0, 0] if d["card_id"] == "counterexample" else [0, 1, 0]}
            for d in search_documents(corpus)]


@pytest.fixture
def store(tmp_path, corpus):
    store = IndexStore(tmp_path / "techniques.sqlite3")
    store.publish(corpus, SPEC, vector_rows(corpus))
    return store


class FakeEmbedder:
    spec = SPEC

    def __init__(self, vector=(1, 0, 0), fail=False):
        self.vector, self.fail, self.calls = vector, fail, []

    def embed(self, inputs):
        self.calls.append(list(inputs))
        if self.fail:
            raise EmbeddingUnavailable("private diagnostic must not escape")
        return (self.vector,)


def test_corpus_has_all_families_original_examples_and_separate_variants(corpus):
    assert FAMILIES <= {c["family"] for c in corpus.active}
    assert len(corpus.active) == 19
    assert len(corpus.cards) == 26
    assert all(len(c["search_phrases"]) == 3 for c in corpus.active)
    assert all(c["example"]["assistant"].count("?") == 1 for c in corpus.active)
    assert len(search_documents(corpus)) == 76
    assert not {"chunk_up_exaggeration", "assumed_motive", "six_step_procedure"} & {d["card_id"] for d in search_documents(corpus)}
    assert all(s["source_id"] in corpus.sources for c in corpus.cards for s in c["sources"])


def test_corpus_rejects_unknown_sources_duplicate_ids_and_active_procedures():
    from app.features.reframing.corpus import CORPUS_PATH
    data = json.loads(CORPUS_PATH.read_text())
    mutations = [
        lambda x: x["cards"][0]["sources"][0].update(source_id="unknown"),
        lambda x: x["cards"][1].update(id=x["cards"][0]["id"]),
        lambda x: x["cards"][0].update(kind="procedure"),
        lambda x: x["cards"][0].update(unexpected="field"),
        lambda x: x["cards"][0].update(related=["unknown"]),
    ]
    for mutate in mutations:
        changed = copy.deepcopy(data)
        mutate(changed)
        with pytest.raises(InvalidKnowledge):
            validate_corpus(changed)


@pytest.mark.parametrize("raw", ['{"a":1,"a":2}', '{"a":NaN}', '[Infinity]', '\ud800', '['])
def test_strict_json_rejects_invalid_records(raw):
    with pytest.raises(InvalidKnowledge):
        strict_json(raw)


@pytest.mark.parametrize("vector", [[0, 0, 0], [1, 2], [True, 0, 0], [math.nan, 1, 2], [math.inf, 1, 2], ["1", 0, 0], [10**400, 0, 0]])
def test_vector_validation(vector):
    with pytest.raises(InvalidKnowledge):
        unit_vector(vector, 3)


def test_large_finite_vectors_normalize_without_overflow():
    assert unit_vector([1e308, 1e308, 0], 3) == pytest.approx((2 ** -.5, 2 ** -.5, 0))


def test_snapshot_real_sqlite_and_rank_family_deduplication(store, corpus):
    rows = store.snapshot(corpus, SPEC)
    found = rank(corpus, rows, [4, 0, 0], dimensions=3, minimum_score=.8)
    assert [(c["id"], score) for c, score in found] == [("counterexample", 1.0)]
    assert len(rows) == 76
    assert rank(corpus, rows, [-1, 0, 0], dimensions=3, minimum_score=.8) == ()
    assert rank(corpus, rows, [1, 0, 0], dimensions=3, minimum_score=.8, exclude_families=("counterexample",)) == ()


def test_no_missing_index_creation(tmp_path, corpus):
    path = tmp_path / "absent.sqlite3"
    with pytest.raises(IndexUnavailable):
        IndexStore(path).snapshot(corpus, SPEC)
    assert not path.exists()


def test_publish_validation_and_exclusive_output(store, corpus, tmp_path):
    before = store.path.read_bytes()
    with pytest.raises(FileExistsError):
        store.publish(corpus, SPEC, vector_rows(corpus))
    assert store.path.read_bytes() == before
    for rows in [vector_rows(corpus)[:-1], [vector_rows(corpus)[0]] * 76]:
        path = tmp_path / "bad.sqlite3"
        with pytest.raises(InvalidKnowledge):
            IndexStore(path).publish(corpus, SPEC, rows)
        assert not path.exists()


@pytest.mark.parametrize("change", ["model", "dimension", "content", "missing", "extra", "nan", "zero", "wrong_hash", "wrong_card", "bad_metadata"])
def test_reject_stale_incompatible_or_corrupt_indexes(store, corpus, change):
    spec = dict(SPEC)
    if change == "model":
        spec["model"] = "different-model"
    elif change == "dimension":
        spec["dimensions"] = 2
    elif change == "content":
        # A change to a non-search note still invalidates the complete corpus revision.
        from app.features.reframing.corpus import CORPUS_PATH
        data = json.loads(CORPUS_PATH.read_text())
        data["cards"][0]["note"] += " Updated."
        corpus = validate_corpus(data)
    else:
        with sqlite3.connect(store.path) as db:
            key = db.execute("SELECT id FROM reframing_vectors LIMIT 1").fetchone()[0]
            if change == "missing":
                db.execute("DELETE FROM reframing_vectors WHERE id=?", (key,))
            elif change == "extra":
                db.execute("INSERT INTO reframing_vectors VALUES ('extra','counterexample','x','[1,0,0]')")
            elif change in {"nan", "zero"}:
                db.execute("UPDATE reframing_vectors SET vector=? WHERE id=?", ('[NaN,0,0]' if change == "nan" else '[0,0,0]', key))
            elif change == "wrong_hash":
                db.execute("UPDATE reframing_vectors SET document_sha256='wrong' WHERE id=?", (key,))
            elif change == "wrong_card":
                db.execute("UPDATE reframing_vectors SET card_id='altered_state' WHERE id=?", (key,))
            else:
                db.execute("UPDATE reframing_metadata SET payload='{}'")
    with pytest.raises(IndexUnavailable):
        store.snapshot(corpus, spec)


def test_service_never_embeds_without_permission_or_ready_index(store, corpus, tmp_path):
    embedder = FakeEmbedder()
    service = ReframingService(store, embedder=embedder, minimum_score=.8)
    for permission in [False, None, 1, "yes"]:
        assert service.prepare("A fictional thought", allow_reference_lookup=permission).status == "skipped"
    assert embedder.calls == []
    missing = ReframingService(IndexStore(tmp_path / "missing"), embedder=embedder, minimum_score=.8)
    assert missing.prepare("fictional", allow_reference_lookup=True).status == "unavailable"
    assert ReframingService(store, embedder=embedder).prepare("fictional", allow_reference_lookup=True).status == "unavailable"
    assert embedder.calls == []


@pytest.mark.parametrize("kwargs", [{"budget": -1}, {"budget": 10001}, {"exclude_families": None}, {"exclude_families": [1]}])
def test_invalid_configuration_never_transmits_a_query(store, kwargs):
    embedder = FakeEmbedder()
    service = ReframingService(store, embedder=embedder, minimum_score=.8)
    assert service.prepare("fictional", allow_reference_lookup=True, **kwargs).status == "unavailable"
    assert embedder.calls == []


def test_failed_atomic_publish_leaves_no_partial_destination(tmp_path, corpus, monkeypatch):
    from app.features.reframing import storage
    def fail(*_args):
        raise OSError("simulated disk publication failure")
    monkeypatch.setattr(storage.os, "link", fail)
    destination = tmp_path / "never-published.sqlite3"
    with pytest.raises(OSError):
        IndexStore(destination).publish(corpus, SPEC, vector_rows(corpus))
    assert not destination.exists()
    assert not list(tmp_path.glob(".reframing-build-*"))


def test_unapproved_book_variant_never_enters_context_even_if_its_vector_would_match(store, corpus):
    with sqlite3.connect(store.path) as db:
        db.execute("INSERT INTO reframing_vectors VALUES ('six_step_procedure:summary','six_step_procedure','fictional','[1,0,0]')")
    embedder = FakeEmbedder()
    result = ReframingService(store, embedder=embedder, minimum_score=.8).prepare("fictional", allow_reference_lookup=True)
    assert result.status == "unavailable"
    assert result.context == ""
    assert embedder.calls == []


def test_service_context_is_bounded_labeled_and_has_only_actual_sources(store, corpus):
    before = store.path.read_bytes()
    embedder = FakeEmbedder()
    service = ReframingService(store, embedder=embedder, minimum_score=.8)
    result = service.prepare("Nothing I try works", allow_reference_lookup=True)
    assert result.report() == {"status": "ready", "card_ids": ["counterexample"]}
    assert result.context.startswith("REFRAMING_TECHNIQUE_REFERENCE\n")
    assert len(result.context.encode()) <= 10000
    payload = json.loads(result.context.split("\n", 1)[1])
    assert payload["cards"][0]["id"] == "counterexample"
    assert all(ref["source"]["id"] == ref["source_id"] for ref in payload["cards"][0]["sources"])
    assert "Nothing I try works" not in result.context
    assert store.path.read_bytes() == before
    assert "not personal facts" in REFERENCE_POLICY
    assert service.prepare("fictional", allow_reference_lookup=True, budget=20).status == "no_match"


def test_failure_and_bad_query_do_not_retain_or_echo_input(store):
    embedder = FakeEmbedder(fail=True)
    service = ReframingService(store, embedder=embedder, minimum_score=.8)
    result = service.prepare("fictional secret", allow_reference_lookup=True)
    assert result.report() == {"status": "unavailable", "card_ids": []}
    assert result.context == ""
    embedder.calls.clear()
    for query in ["", "界" * 2667, "\ud800", "a\x00b"]:
        assert service.prepare(query, allow_reference_lookup=True).status == "unavailable"
    assert embedder.calls == []


def test_multiline_current_message_is_supported_without_storing_query(store):
    embedder = FakeEmbedder()
    result = ReframingService(store, embedder=embedder, minimum_score=.8).prepare("A fictional first line\nA second line", allow_reference_lookup=True)
    assert result.status == "ready"
    assert embedder.calls == [["A fictional first line\nA second line"]]
    assert "A second line" not in result.context


def test_reference_budget_never_slices_json_or_includes_ineligible_cards(corpus):
    selected = ((corpus.active[0], 1), (corpus.active[1], .9))
    full, ids = reference_context(corpus, selected)
    assert len(ids) == 2
    only_one, ids = reference_context(corpus, selected, budget=len(full.encode()) - 1)
    assert len(ids) == 1
    json.loads(only_one.split("\n", 1)[1])
    with pytest.raises(InvalidKnowledge):
        reference_context(corpus, ((next(c for c in corpus.cards if c["status"] == "reference_only"), 1),))


def test_registration_is_disabled_and_has_no_storage_effects(tmp_path):
    app = SimpleNamespace(state=SimpleNamespace())
    assert register(app, object()) is None
    assert app.state.reframing.prepare("fictional", allow_reference_lookup=True).report() == {"status": "off", "card_ids": []}


class Response:
    def __init__(self, data, status=200, content_type="application/json", raw=None):
        self.status = status
        self.headers = Message()
        self.headers["Content-Type"] = content_type
        self.raw = json.dumps(data).encode() if raw is None else raw

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        pass

    def read(self, size):
        return self.raw[:size]


def response_data():
    return {"model": SPEC["model"], "data": [{"object": "embedding", "index": 0, "embedding": [3, 0, 0]}]}


def test_embedding_request_projects_only_server_owned_fields(monkeypatch):
    calls = []
    def mock(request, *, timeout):
        calls.append((request, timeout))
        return Response(response_data())
    monkeypatch.setattr(embeddings, "open_embedding_request", mock)
    embedder = OpenAIEmbedder("fictional-key", SPEC["model"], 3)
    assert embedder.embed(["fictional query"]) == ((1., 0., 0.),)
    request, timeout = calls[0]
    assert request.full_url == embeddings.URL
    assert timeout == 5
    assert json.loads(request.data) == {"model": SPEC["model"], "dimensions": 3, "input": ["fictional query"], "encoding_format": "float"}
    assert "fictional-key" not in repr(embedder)


@pytest.mark.parametrize("problem", ["timeout", "http", "url", "wrong_model", "duplicate_index", "bool_index", "wrong_dimension", "zero", "bad_json", "non_json", "oversized", "redirect"])
def test_embedding_failures_are_bounded_sanitized_and_never_retried(monkeypatch, problem):
    calls = []
    def mock(_request, *, timeout):
        calls.append(timeout)
        if problem == "timeout":
            raise TimeoutError("private")
        if problem == "http":
            raise HTTPError(embeddings.URL, 401, "private", {}, None)
        if problem == "url":
            raise URLError("private")
        data = response_data()
        if problem == "wrong_model": data["model"] = "unexpected"
        if problem == "duplicate_index": data["data"] *= 2
        if problem == "bool_index": data["data"][0]["index"] = False
        if problem == "wrong_dimension": data["data"][0]["embedding"] = [1, 0]
        if problem == "zero": data["data"][0]["embedding"] = [0, 0, 0]
        return Response(data, status=302 if problem == "redirect" else 200,
                        content_type="text/html" if problem == "non_json" else "application/json",
                        raw=b'{' if problem == "bad_json" else (b' ' * (embeddings.MAX_RESPONSE_BYTES + 1) if problem == "oversized" else None))
    monkeypatch.setattr(embeddings, "open_embedding_request", mock)
    with pytest.raises(EmbeddingUnavailable, match="^Embedding service unavailable.$"):
        OpenAIEmbedder("fictional-key", SPEC["model"], 3).embed(["fictional"])
    assert calls == [5]


def test_adapter_restores_batch_order_and_rejects_invalid_input_before_io(monkeypatch):
    data = {"model": SPEC["model"], "data": [{"object": "embedding", "index": 1, "embedding": [0, 2, 0]}, {"object": "embedding", "index": 0, "embedding": [2, 0, 0]}]}
    monkeypatch.setattr(embeddings, "open_embedding_request", lambda *a, **k: Response(data))
    adapter = OpenAIEmbedder("fictional-key", SPEC["model"], 3)
    assert adapter.embed(["one", "two"]) == ((1., 0., 0.), (0., 1., 0.))
    for value in [[], [""], ["x"] * 17, ["x" * 8001], ["\ud800"]]:
        with pytest.raises(InvalidKnowledge):
            adapter.embed(value)
