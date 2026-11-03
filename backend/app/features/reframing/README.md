# Reframing library

Typed chat can retrieve original reframing cards by semantic similarity, independently
of opt-in personal memory. The feature is **disabled by default**. No book text,
personal-history vectors, dependency or vector server is required. Exact cosine
search over 76 documents is stored in a separate SQLite file.

- 19 active conversational cards cover 14 core families plus supporting patterns.
- Seven reference-only variants/procedures are excluded from search and replies.
- Source editions, positions and adaptations accompany complete selected cards.
- Missing/stale indexes, errors, saturation or a two-second wait continue ordinary
  chat without references. A nonblocking notice appears for unavailable references.
- The full current typed message alone is embedded; saved memory is never embedded.
- Retrieval provides optional references, not permission to apply a reframe.
- Voice receives a compact startup catalogue of all 19 active operations, safeguards
  and bibliographic sources. It performs no voice embedding or mid-session lookup.

Run from the project root:

```sh
backend/.venv/bin/python scripts/reframing_kb.py validate
backend/.venv/bin/python -m pytest backend/app/features/reframing/tests -q
```

Server environment (no browser configuration):

```text
REFRAMING_ENABLED=0
```

Before setting it to `1`, configure all of `REFRAMING_INDEX_PATH` (a project-owned
`.sqlite3` file), `REFRAMING_EMBEDDING_MODEL`, `REFRAMING_DIMENSIONS` and
`REFRAMING_MINIMUM_SCORE`, with the existing `OPENAI_API_KEY`. No model, dimensions
or threshold is assumed. Use a real, compatible, evaluated index; see
[implementation evidence](../../../../docs/reframing-implementation-evidence.md).
The current ignored local `.env` selects the validated `reframing-2026-11-03.sqlite3`
index, `text-embedding-3-small` / 1536 dimensions / 0.45, enables retrieval and sets
`CHAT_REASONING_EFFORT=low` for the separately approved typed latency experiment.
The code default remains off. Restart the local backend after environment changes. Setting the flag back to `0`
restores ordinary typed chat for new requests. This cannot undo requests already sent.
Hosted matching transmits the current typed message and incurs API usage.

[CONTRACT.md](CONTRACT.md) documents JSON, limits and failure behavior. Local
`private/` vectors/exports and handoff documents are ignored; full books are not
runtime dependencies or shipped corpus content.
