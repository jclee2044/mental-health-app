# Guided breathing JSON contract

`PUT /api/sessions/{uuid}` creates (201) an immutable record or returns the existing record (200) on retry; it never duplicates or overwrites a recorded session. `GET /api/sessions` returns `{ "sessions": [...] }` newest-first. Same JSON error envelope as entries. Required body fields (response adds `id`):

```json
{
  "pattern": "paced-4-6-v1",
  "status": "completed",
  "started_at": "2026-10-21T15:00:00.000Z",
  "ended_at": "2026-10-21T15:01:03.000Z",
  "local_date": "2026-10-21",
  "sequence_seconds": 63,
  "active_seconds": 60,
  "pause_seconds": 0,
  "instruction_seconds": 73
}
```

`status` is `completed` or `ended`. Fixed pattern only. Finite nonnegative durations: sequence includes the 3-second countdown (max 63); active excludes it (max 60). Completion requires 63/60 seconds. Instruction duration includes ready-screen reading, countdown, actual application delays, and the final step, excluding explicit pauses and overlays; entry/splash/navigation time is separate. Long voluntary reading may exceed 90 seconds; no forced exit. Timestamps require offsets and ordered start/end. The API checks record consistency; these self-reported browser timings are not server-observed adherence or clinical outcomes.

SQLite `skill_sessions` columns match this object, `id` primary key. Session records persist across server restarts. Failed saves are retained in the current app's memory with Retry; they are not durably queued and will be lost on reload or closing the app. Forced process termination/browser crash may prevent an ended record. No background sync or personal-data cache. TODO: user-facing deletion/retention controls for session records before broader persistence work.


All routes use `/api`, JSON and `Cache-Control: no-store`. Errors use `{ "error": { "code": "validation_error", "message": "Check the highlighted fields.", "fields": {} } }`: 422 for shape/domain errors, 404 for missing routes, 503 for unavailable SQLite. HTTP transport is implemented only in the shared frontend API client.
