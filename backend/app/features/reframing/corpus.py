"""Read only the bundled, reviewed corpus; no uploaded books or user databases."""
from pathlib import Path
from .domain import InvalidKnowledge, strict_json, validate_corpus

CORPUS_PATH = Path(__file__).with_name("data") / "cards.json"


def load_corpus(path=CORPUS_PATH):
    with Path(path).open("rb") as stream:
        raw = stream.read(512 * 1024 + 1)
    if len(raw) > 512 * 1024:
        raise InvalidKnowledge("Corpus file too large.")
    return validate_corpus(strict_json(raw))
