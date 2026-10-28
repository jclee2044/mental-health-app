# Emotion log JSON contract

All endpoints use `/api`, JSON, and `Cache-Control: no-store`. Vue uses a relative same-origin URL; Vite proxies `/api` to `127.0.0.1:8000` during development. Production is served by FastAPI on localhost. No CORS middleware is needed with this arrangement. UI components never call fetch directly.

## Emotion entries

`PUT /api/entries/{uuid}` creates (201) or replaces (200) the entry at a client-generated UUID. Reusing the UUID makes save retries safe. Edits preserve `recorded_at` and `local_date`; `updated_at` changes. `GET /api/entries` returns `{ "entries": [...] }` newest-first. `GET /api/entries/{uuid}` returns one entry. `DELETE /api/entries/{uuid}` returns 204; a missing entry returns 404. There is no hard-coded demonstration seed data.

PUT body:

```json
{
  "feeling": null,
  "color": "#8fa98d",
  "color_meaning": "A quiet shade",
  "pleasantness": 20,
  "energy": -30,
  "note": "A moment between tasks.",
  "recorded_at": "2026-10-21T15:10:00.000Z",
  "local_date": "2026-10-21"
}
```

Feeling is optional and defaults to null. The graph-first form no longer requests or infers a feeling category. Legacy explicit integers 1–5 (Very unpleasant, Unpleasant, Neutral, Pleasant, Very pleasant) remain accepted/readable for existing entries; editing preserves that legacy value. These labels are not a clinical scale. Color is a six-digit hex value chosen explicitly. Color meaning (max 80 characters) and note (max 2000) default to empty strings. Pleasantness/energy are required integers −100 through 100, with zero the center; untouched UI defaults are not explicit selections. `recorded_at` must include a UTC offset; the server normalizes UTC. `local_date` is the date at entry creation in the user's browser and must be within one calendar day of the UTC timestamp. Dates remain attached to the original entry when it is edited. No emotional or risk meaning is inferred from coordinates or colors.

Response is the same object plus `id`, `created_at`, and `updated_at` (UTC ISO timestamps). Unknown request fields are rejected. Client-generated IDs support retries; this single-user localhost iteration has no conflict-resolution/versioning protocol.

## Errors

```json
{
  "error": {
    "code": "validation_error",
    "message": "Check the highlighted fields.",
    "fields": { "feeling": "Choose a feeling." }
  }
}
```

422 = invalid shape or domain value; 404 = `not_found`; 503 = `storage_unavailable` with no internal database details. `fields` is always an object. Malformed JSON uses the same 422 envelope. Invalid route/method errors also use the envelope. Frontend transport timeouts/offline errors produce an API-client error, not a fabricated server response. Failed saves preserve the in-memory draft. No successful UI state precedes a confirmed HTTP success.

## Storage and deletion

For compatibility with existing NOT NULL databases, storage encodes an absent feeling as internal integer 0 and projects it as JSON null on every read/write response. Zero is never a feeling category and is rejected as API input; no existing rows are rewritten.

SQLite table `emotion_entries`: `id` primary key plus the above fields; dates/timestamps stored as text; selections/coordinates as integers. Deletion removes the row; this prototype does not promise forensic erasure or deletion from OS backups. Data is stored in ignored `backend/data/still.sqlite3`. No automatic retention expiry. No personal API response enters the service worker cache. Appearance preferences alone use browser localStorage. Drafts are lost on reload/exit.

Chat/model endpoints, conversation persistence, provider/transmission rules, and history-as-context consent are outside this iteration. A localhost database makes no promise about a future model provider.
