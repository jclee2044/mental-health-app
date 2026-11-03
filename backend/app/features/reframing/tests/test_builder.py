"""Only injected synthetic embeddings; real API usage is never enabled here."""
import pytest
from app.features.reframing.builder import build_export
from app.features.reframing.corpus import load_corpus
from app.features.reframing.domain import InvalidKnowledge, search_documents
from app.features.reframing.embeddings import EmbeddingUnavailable
from app.features.reframing.storage import IndexStore


class SyntheticEmbedder:
    spec = {"provider": "openai", "model": "mock-only", "dimensions": 2}

    def __init__(self, fail_on=None):
        self.calls = []
        self.fail_on = fail_on

    def embed(self, values):
        self.calls.append(values)
        if len(self.calls) == self.fail_on:
            raise EmbeddingUnavailable("fictional failure")
        return tuple([1., 0.] for _ in values)


def test_build_requires_explicit_opt_in_and_preflights_entire_request_cap():
    corpus, embedder = load_corpus(), SyntheticEmbedder()
    for permission, cap in [(False, 5), (1, 5), (True, None), (True, True), (True, 4)]:
        with pytest.raises(InvalidKnowledge):
            build_export(corpus, embedder, allow_api_usage=permission, max_requests=cap)
    assert embedder.calls == []


def test_complete_synthetic_build_round_trips_through_the_index(tmp_path):
    corpus, embedder = load_corpus(), SyntheticEmbedder()
    result = build_export(corpus, embedder, allow_api_usage=True, max_requests=5)
    assert [len(batch) for batch in embedder.calls] == [16, 16, 16, 16, 12]
    assert [t for batch in embedder.calls for t in batch] == [d["text"] for d in search_documents(corpus)]
    assert not any("Reference-only source method." in t for batch in embedder.calls for t in batch)
    assert len(result["rows"]) == 76
    store = IndexStore(tmp_path / "synthetic.sqlite3")
    store.publish(corpus, result["spec"], result["rows"])
    assert len(store.snapshot(corpus, result["spec"])) == 76


def test_batch_failure_stops_build_without_retry_or_publishing(tmp_path):
    embedder = SyntheticEmbedder(fail_on=2)
    with pytest.raises(EmbeddingUnavailable):
        build_export(load_corpus(), embedder, allow_api_usage=True, max_requests=5)
    assert len(embedder.calls) == 2
    assert not list(tmp_path.iterdir())


def test_invalid_batch_result_aborts_before_next_request():
    embedder = SyntheticEmbedder()
    def bad(values):
        embedder.calls.append(values)
        return ()
    embedder.embed = bad
    with pytest.raises(InvalidKnowledge):
        build_export(load_corpus(), embedder, allow_api_usage=True, max_requests=5)
    assert len(embedder.calls) == 1
