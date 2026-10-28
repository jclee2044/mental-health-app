# Conversation persistence contract

Current October 27 extension below adds spoken transcript text to the same chats;
older voice-transience statements in the October 26 section are superseded.

October 26, 2026. This increment supersedes earlier typed-message non-persistence.
Voice transport, audio and captions remain transient. No provider call is made by
these routes, and saving a pair does not certify its model provenance. Fictional
localhost data only; no authentication or cross-user separation.

`PUT /api/chat/conversations/{conversation_uuid}/turns/{turn_uuid}` accepts only:

```json
{"position":0,"user":"Explain the breathing steps.","assistant":"Four seconds in, six out, for six cycles."}
```

Position is a strict integer 0–99 within this conversation. Each string must be
nonblank and at most 8,000 UTF-8 bytes. Unknown fields, query parameters and
non-JSON requests are rejected. A bounded JSON parser caps the request at 96 KiB.
The server transaction creates the conversation if needed, then saves both
messages atomically with server UTC timestamps. Response is
`{"conversation_id":"uuid","turn_id":"uuid","saved":true}`: 201 when created,
200 for an identical retry. A changed pair, reused position, or turn ID belonging
to another conversation returns 409 `conversation_conflict`; nothing is overwritten.
Positions may have gaps after failed saves; review orders by position and role.

`GET /api/chat/conversations` returns `{"conversations":[...]}` newest-updated
first, with each item containing `id`, `created_at`, `updated_at`, `message_count`.
`GET /api/chat/conversations/{uuid}` returns those fields plus `messages`, each
with `turn_id`, `position`, `role` (`user`/`assistant`), `content`, `created_at`.
Review is read-only: no implicit provider lookup, resume, retrieval or personalization.
`DELETE /api/chat/conversations/{uuid}` atomically deletes its messages and header,
returning 204; missing records return 404. In-app confirmation is required.
Deletion affects this SQLite file, not backups or provider records. No automatic
expiry; saved typed pairs remain until deleted.

All routes use `Cache-Control: no-store` and the shared error envelope
`{"error":{"code":"...","message":"...","fields":{}}}`. Validation is 422,
oversized body 413, unsupported media 415, missing record 404, conflict 409,
unavailable storage 503. Response errors do not expose SQL or message contents.

SQLite tables: `chat_conversations` and `chat_messages`. There are two rows per
successful turn, identified by `(conversation_id, position, role)` and immutable
turn UUID; no audio/caption rows. They survive app/server restarts. The browser
queues only successful typed exchanges, separately from `POST /api/chat/messages`.
Failed model requests are not saved. Save status and manual Retry remain visible
across navigation in this loaded app; Retry repeats storage only. Pending/failed
pairs are memory-only and can be lost on reload/close. Late replies after leaving
chat are ignored. Do not represent that case as saved.

The provider endpoint still uses only bounded current-chat context, supplied by
the browser, with server-owned prompts/settings and `store:false`. Local SQLite
does not imply local model processing or any general provider retention/training
promise. Historical conversations are never automatically included.


## Unified typed and spoken text — October 27, 2026

User explicitly requested all chats and clarified that only transcribed text,
not audio recordings, should save and display like ordinary chat. This overrides
the previous voice-caption non-persistence boundary. Dictation remains ordinary
typed draft content, saved only through a completed typed pair after Send.

PUT /api/chat/conversations/{conversation_uuid}/voice-turns/{turn_uuid} accepts
exactly {"position":0,"messages":[{"role":"user","content":"A fictional day"}]}.
Strict integer position 0–99 shares the existing conversation save-slot sequence.
1–50 user/assistant messages, nonblank content, max 8,000 UTF-8 bytes each / 32,000
combined. No other fields, roles or query params. Same JSON/media/wire limits,
error envelope and storage statuses as typed saves. Source is server-fixed voice;
no audio or capture metadata is accepted. Same {conversation_id,turn_id,saved}
201/200 idempotency response; changed/reused IDs or positions conflict with both
text and voice records (409). One batch transaction is atomic. Typed pairs still
save atomically through their original route without mixing captions into pairs.

Additive table chat_voice_messages contains conversation_id, turn_id, position,
ordinal, role, content, created_at. Existing typed tables are preserved. Unified
listing counts both tables; detail orders by shared position then ordinal and
adds source:text/voice for provenance. No per-bubble source labels in the UI;
both render as ordinary speaker/message text. Conversation deletion removes both
text tables and header in one transaction. Existing records survive initialization.
Review remains read-only and never injects history into a provider request.

Browser queues accepted Live text when voice ends/errors or chat is disposed,
including navigation/Emergency/hidden handling. It preserves speaker/timeline
order from the current bubbles, uses bounded UTF-8 batches (max 8,000 combined
bytes on the client), and rejects stale events through existing transport guards.
Only text fields are queued; no fragments, timing/audio, provider usage or SDP.
Split long content at Unicode boundaries. Shared save slots cap at 100; failed
out-of-bound/storage writes remain visible in the feature retry queue rather
than silently disappearing. Manual retry repeats the same immutable save only,
never voice/session/model calls. Queues survive navigation in the loaded app;
reload/close can lose pending saves and an in-progress voice transcript. Browser
crash/closed-tab save delivery is not guaranteed. Saving is not continuous/live.

Accepted captions may be partial, approximate, overlapping or interrupted; their
storage does not certify completed user/assistant turns, heard audio or generated
behavior. Preserve this in privacy/contract notes without repeated bubble labels.
Earlier unsaved voice conversations cannot be recovered. No recording/audio files
or raw dictation clips are stored. Local deletion does not control provider data.
