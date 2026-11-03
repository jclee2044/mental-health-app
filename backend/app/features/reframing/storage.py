"""A standalone immutable SQLite index. Runtime reads never create/write files."""
import sqlite3
import os
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from .domain import (InvalidKnowledge, IndexUnavailable, canonical, digest,
                     embedding_spec, search_documents, strict_json, unit_vector)


class IndexStore:
    def __init__(self, path):
        self.path = Path(path)

    @contextmanager
    def _read(self):
        # mode=ro, not just a prior exists() check: a disappearing file cannot be recreated.
        connection = sqlite3.connect(self.path.resolve().as_uri() + "?mode=ro", uri=True, timeout=.05)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA query_only=ON")
            deadline = time.monotonic() + .2
            connection.set_progress_handler(lambda: time.monotonic() > deadline, 1000)
            yield connection
        finally:
            connection.close()

    def publish(self, corpus, spec, supplied_rows):
        """Publish to a NEW file only. No overwrite/delete of an existing index."""
        spec = embedding_spec(**spec)
        documents = search_documents(corpus)
        if not isinstance(supplied_rows, list) or len(supplied_rows) != len(documents):
            raise InvalidKnowledge("Embedding count mismatch.")
        expected = {d["id"]: d for d in documents}
        prepared, seen = [], set()
        for row in supplied_rows:
            if not isinstance(row, dict) or set(row) != {"id", "sha256", "vector"}:
                raise InvalidKnowledge("Invalid embedding row.")
            key = row["id"]
            if not isinstance(key, str) or key in seen or key not in expected or row["sha256"] != expected[key]["sha256"]:
                raise InvalidKnowledge("Embedding document mismatch.")
            seen.add(key)
            vector = unit_vector(row["vector"], spec["dimensions"])
            prepared.append((key, expected[key]["card_id"], row["sha256"], canonical(vector)))
        metadata = {"schema_version": 1, "corpus_sha256": corpus.fingerprint,
                    "documents_sha256": digest(documents), "spec": spec, "count": len(documents),
                    "built_at": datetime.now(timezone.utc).isoformat()}
        # Build privately, then atomically publish with a no-clobber hard link.
        # Readers see a complete index; disk/SQL errors preserve an existing output.
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".reframing-build-", suffix=".sqlite3", dir=self.path.parent)
        os.close(fd)
        connection = None
        try:
            connection = sqlite3.connect(temporary)
            with connection:
                connection.execute("CREATE TABLE reframing_metadata (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)")
                connection.execute("CREATE TABLE reframing_vectors (id TEXT PRIMARY KEY, card_id TEXT NOT NULL, document_sha256 TEXT NOT NULL, vector TEXT NOT NULL)")
                connection.execute("INSERT INTO reframing_metadata VALUES (1, ?)", (canonical(metadata),))
                connection.executemany("INSERT INTO reframing_vectors VALUES (?, ?, ?, ?)", prepared)
            connection.close()
            connection = None
            os.link(temporary, self.path)
        finally:
            if connection is not None:
                connection.close()
            # Only the temporary file just created by this call is removed.
            Path(temporary).unlink(missing_ok=True)
        return metadata

    def snapshot(self, corpus, spec):
        spec = embedding_spec(**spec)
        documents = search_documents(corpus)
        expected = {d["id"]: d for d in documents}
        try:
            with self._read() as connection:
                # One read snapshot for metadata/vectors; readers cannot see a mixed build.
                connection.execute("BEGIN")
                metas = connection.execute("SELECT CASE WHEN length(payload)<=4000 THEN payload ELSE NULL END AS payload FROM reframing_metadata LIMIT 2").fetchall()
                if len(metas) != 1 or not isinstance(metas[0]["payload"], str) or len(metas[0]["payload"].encode()) > 4000:
                    raise InvalidKnowledge("Invalid index metadata.")
                meta = strict_json(metas[0]["payload"])
                if not isinstance(meta, dict) or set(meta) != {"schema_version", "corpus_sha256", "documents_sha256", "spec", "count", "built_at"}:
                    raise InvalidKnowledge("Invalid index metadata.")
                if not isinstance(meta["spec"], dict) or embedding_spec(**meta["spec"]) != spec:
                    raise InvalidKnowledge("Incompatible embedding configuration.")
                if not isinstance(meta["built_at"], str) or len(meta["built_at"]) > 100 or datetime.fromisoformat(meta["built_at"]).tzinfo is None:
                    raise InvalidKnowledge("Invalid build timestamp.")
                if (type(meta["schema_version"]) is not int or meta["schema_version"] != 1 or
                        type(meta["count"]) is not int or meta["count"] != len(documents) or
                        meta["corpus_sha256"] != corpus.fingerprint or meta["documents_sha256"] != digest(documents) or
                        meta["spec"] != spec):
                    raise InvalidKnowledge("Stale or incompatible index.")
                rows = connection.execute("SELECT id, card_id, document_sha256, CASE WHEN length(vector)<=? THEN vector ELSE NULL END AS vector FROM reframing_vectors ORDER BY id LIMIT ?",
                                          (spec["dimensions"] * 40 + 100, len(documents) + 1)).fetchall()
            if len(rows) != len(documents):
                raise InvalidKnowledge("Incomplete index.")
            result, seen = [], set()
            for row in rows:
                doc = expected.get(row["id"])
                if not doc or row["id"] in seen or row["card_id"] != doc["card_id"] or row["document_sha256"] != doc["sha256"]:
                    raise InvalidKnowledge("Invalid index document.")
                if not isinstance(row["vector"], str) or len(row["vector"].encode()) > spec["dimensions"] * 40 + 100:
                    raise InvalidKnowledge("Vector encoding too large.")
                vector = unit_vector(strict_json(row["vector"]), spec["dimensions"])
                result.append({"id": row["id"], "card_id": row["card_id"], "vector": vector})
                seen.add(row["id"])
            return tuple(result)
        except (sqlite3.Error, OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
            raise IndexUnavailable("Reframing index unavailable or incompatible.") from exc
