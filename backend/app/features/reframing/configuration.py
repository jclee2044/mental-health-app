"""Explicit server-only opt-in. Invalid enabled configuration fails without lookup."""
import os
from pathlib import Path
from .domain import InvalidKnowledge, selection_settings
from .embeddings import OpenAIEmbedder
from .service import ReframingService
from .storage import IndexStore

PROJECT = Path(__file__).resolve().parents[4]


def configured_service():
    store = IndexStore(PROJECT / "backend/data/reframing.sqlite3")
    flag = os.environ.get("REFRAMING_ENABLED", "0")
    if flag == "0":
        return ReframingService(store)
    try:
        if flag != "1":
            raise InvalidKnowledge("Invalid feature flag.")
        path = Path(os.environ["REFRAMING_INDEX_PATH"])
        path = (PROJECT / path).resolve() if not path.is_absolute() else path.resolve()
        if not path.is_relative_to(PROJECT) or path.suffix != ".sqlite3":
            raise InvalidKnowledge("Index must be a project-owned SQLite file.")
        minimum = float(os.environ["REFRAMING_MINIMUM_SCORE"])
        selection_settings(minimum)
        embedder = OpenAIEmbedder(os.environ["OPENAI_API_KEY"], os.environ["REFRAMING_EMBEDDING_MODEL"], int(os.environ["REFRAMING_DIMENSIONS"]))
        return ReframingService(IndexStore(path), embedder=embedder, minimum_score=minimum)
    except (KeyError, ValueError, OSError):
        return ReframingService(store, configuration_error=True)
