"""Offline-only reframing authoring/index diagnostics; never contacts a provider."""
import argparse
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "backend"))

from app.features.reframing.corpus import load_corpus
from app.features.reframing.domain import (
    InvalidKnowledge, IndexUnavailable, MAX_VECTOR_FILE_BYTES, canonical, digest,
    embedding_spec, fields, rank, reference_context, search_documents, strict_json,
)
from app.features.reframing.storage import IndexStore


def read_bounded(path):
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_VECTOR_FILE_BYTES + 1)
    if len(data) > MAX_VECTOR_FILE_BYTES:
        raise InvalidKnowledge("Vector file too large.")
    return strict_json(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="Validate the corpus and print counts; no writes or API calls")
    plan = commands.add_parser("plan", help="Write original card search text to a NEW JSON file; no embeddings generated")
    plan.add_argument("--output", required=True, type=Path)
    publish = commands.add_parser("publish", help="Validate imported vectors and create a NEW standalone SQLite index")
    publish.add_argument("--vectors", required=True, type=Path)
    publish.add_argument("--output", required=True, type=Path)
    inspect = commands.add_parser("inspect", help="Read-only validation of an existing index")
    query = commands.add_parser("query-vector", help="Search with an explicitly supplied vector; no text embedding/API calls")
    for command in [inspect, query]:
        command.add_argument("--index", required=True, type=Path)
        command.add_argument("--model", required=True)
        command.add_argument("--dimensions", required=True, type=int)
    query.add_argument("--vector-file", required=True, type=Path, help="JSON array of finite numbers")
    query.add_argument("--minimum-score", required=True, type=float)
    args = parser.parse_args(argv)
    try:
        corpus = load_corpus()
        documents = search_documents(corpus)
        if args.command == "validate":
            result = {"revision": corpus.revision, "corpus_sha256": corpus.fingerprint,
                      "active_cards": len(corpus.active), "reference_only_cards": len(corpus.cards) - len(corpus.active),
                      "search_documents": len(documents), "network": "none"}
        elif args.command == "plan":
            payload = {"schema_version": 1, "corpus_sha256": corpus.fingerprint,
                       "documents_sha256": digest(documents), "documents": documents}
            # No mkdir/overwrite or hidden upload: the caller chooses a new project file.
            destination = args.output.resolve()
            if not destination.is_relative_to(PROJECT):
                raise InvalidKnowledge("Outputs must remain inside this project.")
            with destination.open("x") as stream:
                stream.write(canonical(payload) + "\n")
            result = {"status": "plan_written", "documents": len(documents), "network": "none"}
        elif args.command == "publish":
            payload = read_bounded(args.vectors)
            fields(payload, {"schema_version", "corpus_sha256", "documents_sha256", "spec", "rows"})
            if (type(payload["schema_version"]) is not int or payload["schema_version"] != 1 or
                    payload["corpus_sha256"] != corpus.fingerprint or payload["documents_sha256"] != digest(documents)):
                raise InvalidKnowledge("Embedding export does not match this corpus/plan.")
            fields(payload["spec"], {"provider", "model", "dimensions"})
            spec = embedding_spec(**payload["spec"])
            destination = args.output.resolve()
            if not destination.is_relative_to(PROJECT):
                raise InvalidKnowledge("Outputs must remain inside this project.")
            result = IndexStore(destination).publish(corpus, spec, payload["rows"])
        else:
            spec = embedding_spec("openai", args.model, args.dimensions)
            rows = IndexStore(args.index).snapshot(corpus, spec)
            if args.command == "inspect":
                result = {"status": "ready", "documents": len(rows), "spec": spec, "network": "none"}
            else:
                selected = rank(corpus, rows, read_bounded(args.vector_file), dimensions=spec["dimensions"], minimum_score=args.minimum_score)
                context, included = reference_context(corpus, selected)
                result = {"status": "ready" if included else "no_match", "card_ids": included,
                          "scores": [{"card_id": c["id"], "similarity": score} for c, score in selected if c["id"] in included],
                          "context": context, "network": "none"}
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (InvalidKnowledge, IndexUnavailable, OSError, TypeError) as exc:
        # No raw query, vectors, file contents or credential details in diagnostics.
        print(json.dumps({"error": {"code": "reframing_unavailable", "message": "Check the corpus, vector export, index compatibility and output path. Existing outputs are never overwritten."}}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
