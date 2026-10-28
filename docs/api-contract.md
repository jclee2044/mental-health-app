# JSON API contracts

The shared request/error boundary is described in [architecture](architecture.md). Each feature owns its endpoint shapes and storage decisions:

- [Emotion entries](../backend/app/features/emotion/CONTRACT.md): explicit choices, calendar/history, edit/delete, safe retry.
- [Guided breathing](../backend/app/features/breathing/CONTRACT.md): fixed-pattern, completed/ended session records and timing.
- [Voice negotiation, cleanup and typed messages](../backend/app/features/voice/CONTRACT.md): `GET /api/voice/config`, `POST /api/voice/sessions`, `POST /api/voice/sessions/{session_id}/end` and independent `POST /api/chat/messages`; server-owned configuration, transient frontend state and mocked verification.
- [Typed conversation persistence](../backend/app/features/voice/PERSISTENCE.md): independent immutable turn PUT, conversation list/detail GET and confirmed DELETE; atomic SQLite message pairs, safe retries, no automatic model-history retrieval.

All API routes use JSON and `Cache-Control: no-store`. No personal response is cached by the PWA. Same-origin development uses Vite’s `/api` proxy; the production build is served by FastAPI on localhost.


### OpenAI dictation — October 27, 2026

POST /api/chat/transcriptions accepts exactly audio (base64) and mime_type
(audio/webm or audio/mp4), returning {"text":"..."}. Server policy, size bounds,
validation and error envelope are documented in
[DICTATION.md](../backend/app/features/voice/DICTATION.md). No browser model/key/
prompt/history is accepted, audio is not persisted and transcription never sends
a chat turn automatically. This user-approved endpoint replaces browser-only
dictation; existing Live/text/storage contracts remain unchanged.


### Unified spoken/typed text history — October 27, 2026

PUT /api/chat/conversations/{uuid}/voice-turns/{uuid} saves bounded voice text
batches without audio. GET history now combines typed pairs and spoken text in
shared sequence; detail includes source metadata, but both use normal chat UI.
DELETE removes both. See the October 27 extension in
[the persistence contract](../backend/app/features/voice/PERSISTENCE.md).
