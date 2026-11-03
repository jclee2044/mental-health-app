"""Explicit, request-capped embedding build. Never called at registration/startup."""
from .domain import (InvalidKnowledge, canonical, digest, embedding_spec,
                     MAX_VECTOR_FILE_BYTES, search_documents, unit_vector)


def build_export(corpus, embedder, *, allow_api_usage=False, max_requests=None):
    """Return an in-memory export; no index/output writes and no automatic retries.

    A failed batch raises without returning a partial export. Earlier provider
    requests may already have incurred usage; an explicit later rebuild is new
    usage, not a storage retry.
    """
    if allow_api_usage is not True:
        raise InvalidKnowledge("Explicit embedding API-usage authorization is required.")
    if type(max_requests) is not int or not 1 <= max_requests <= 100:
        raise InvalidKnowledge("An explicit build request cap is required.")
    spec = embedding_spec(**embedder.spec)
    documents = search_documents(corpus)
    batches, batch, size = [], [], 0
    # Prepare and validate EVERY batch and its request budget before any network call.
    for document in documents:
        length = len(document["text"].encode("utf-8"))
        if not length or length > 4000:
            raise InvalidKnowledge("Build document outside embedding input bounds.")
        if len(batch) == 16 or size + length > 24000:
            batches.append(batch)
            batch, size = [], 0
        batch.append(document)
        size += length
    if batch:
        batches.append(batch)
    if len(batches) > max_requests:
        raise InvalidKnowledge("Build exceeds the authorized request cap.")
    rows = []
    for batch in batches:
        vectors = embedder.embed([document["text"] for document in batch])
        if not isinstance(vectors, (list, tuple)) or len(vectors) != len(batch):
            raise InvalidKnowledge("Embedding build result count mismatch.")
        for document, vector in zip(batch, vectors):
            rows.append({"id": document["id"], "sha256": document["sha256"],
                         "vector": unit_vector(vector, spec["dimensions"])})
    result = {"schema_version": 1, "corpus_sha256": corpus.fingerprint,
              "documents_sha256": digest(documents), "spec": spec, "rows": rows}
    if len(canonical(result).encode()) > MAX_VECTOR_FILE_BYTES:
        raise InvalidKnowledge("Embedding build exceeds export bounds.")
    return result
