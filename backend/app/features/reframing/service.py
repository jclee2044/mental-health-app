"""Independent composition interface. No chat routes, history or prompt mutation."""
from dataclasses import dataclass
from .corpus import load_corpus
from .domain import (InvalidKnowledge, IndexUnavailable, MAX_QUERY_BYTES, embedding_spec,
                     context_budget, rank, reference_context, selection_settings, text)
from .embeddings import EmbeddingUnavailable


@dataclass(frozen=True)
class Retrieval:
    status: str
    context: str = ""
    card_ids: tuple = ()

    @property
    def block(self):
        from ...context_data import ContextBlock
        from .domain import REFERENCE_POLICY
        return ContextBlock(REFERENCE_POLICY, self.context) if self.context else ContextBlock()

    def report(self):
        # No query, personal information or credential is retained in a report.
        return {"status": self.status, "card_ids": list(self.card_ids)}


class ReframingService:
    def __init__(self, store, *, embedder=None, minimum_score=None, corpus_loader=load_corpus, configuration_error=False):
        self.configuration_error = configuration_error
        self.store = store
        self.embedder = embedder
        self.minimum_score = minimum_score
        self.corpus_loader = corpus_loader

    def prepare(self, query, *, allow_reference_lookup=False, exclude_families=(), budget=10000):
        # Server configuration controls lookup, not conversational permission.
        if self.configuration_error:
            return Retrieval("unavailable")
        if self.embedder is None:
            return Retrieval("off")
        if allow_reference_lookup is not True:
            return Retrieval("skipped")
        try:
            if not isinstance(query, str):
                raise InvalidKnowledge("Invalid query.")
            text(query.replace("\r", " ").replace("\n", " ").replace("\t", " "), MAX_QUERY_BYTES)
            corpus = self.corpus_loader()
            spec = embedding_spec(**self.embedder.spec)
            # Validate the whole current index before any potentially paid query call.
            rows = self.store.snapshot(corpus, spec)
            # Validate settings before sending text to any embedding service.
            selection_settings(self.minimum_score)
            context_budget(budget)
            if (not isinstance(exclude_families, (tuple, list, frozenset, set)) or
                    len(exclude_families) > 100 or any(not isinstance(f, str) for f in exclude_families)):
                raise InvalidKnowledge("Invalid family exclusions.")
            vectors = self.embedder.embed([query])
            if not isinstance(vectors, (list, tuple)) or len(vectors) != 1:
                raise InvalidKnowledge("Embedding result count mismatch.")
            selected = rank(corpus, rows, vectors[0], dimensions=spec["dimensions"],
                            minimum_score=self.minimum_score, exclude_families=exclude_families)
            context, card_ids = reference_context(corpus, selected, budget=budget)
            return Retrieval("ready" if card_ids else "no_match", context, card_ids)
        except (InvalidKnowledge, IndexUnavailable, EmbeddingUnavailable, OSError, UnicodeError):
            return Retrieval("unavailable")
