# Voice negotiation contract

The October 22 backend broker is connected to the October 26 native-browser chat
feature, verified only with mocks. The user also authorized the independent typed
endpoint below because chat was a disabled placeholder. The subsequent Part 3.2
increment adds separate [typed persistence](PERSISTENCE.md); the provider routes
remain independent of SQLite. No tools or live testing. Fictional coursework only. Every response uses
`Cache-Control: no-store`.

## Application JSON

`GET /api/voice/config` returns 200 with exactly:

```json
{"status":"unconfigured","duration_seconds":300}
```

Status is `configured` if the backend process has both a nonempty, header-safe
`OPENAI_API_KEY` and a valid `VOICE_BACKEND_MODEL`, otherwise `unconfigured`.
The backend model is required with no automatic model choice or fallback. Its
identifier must be 1–128 ASCII letters/digits or `._:-`, starting with a letter
or digit. It is not exposed by configuration responses. Status does not verify access, credit,
model availability, or key validity. Neither startup nor GET contacts OpenAI.
Set the environment before starting FastAPI; restart to change it. The app itself
does not load dotenv. For a repository-root `.env`, launch Uvicorn from the root
with `--env-file .env`; its support is already installed in the existing project
environment, so no dependency was added. The key is not returned or logged by
this feature.

`POST /api/voice/sessions` requires `Content-Type: application/json` and exactly:

```json
{"sdp":"<browser-generated audio SDP offer>","history":[{"role":"user","content":"Earlier message in this chat"}]}
```

No profile/owner exists in this app, so those IDs are neither required nor
accepted. Reject all extra fields/query parameters, duplicate JSON keys,
non-string SDP, non-finite constants, and malformed JSON. The browser cannot
provide models, keys, URLs, prompts, tools, policy, storage, duration, event
permissions, or provider session configuration. GET also rejects query parameters.

The subsequent shared-conversation request authorizes optional `history` (default
[]), containing at most 16 user/assistant messages with nonempty content. Reject
developer/system roles, metadata/configuration and unknown fields. Content is
limited to 6,000 combined UTF-8 bytes (each message at most 8,000); wire/SDP bounds
still apply. This conservative byte budget leaves room below the provider's
rendered startup-history token limit; exact provider token rendering is unverified.
Only current-chat visible text/approximate captions are supplied by the client,
never stored records or an automatic database lookup. The browser copy discloses
context sharing. Earlier SDP-only/fresh-empty-context restrictions are superseded
for this authorized history field; all provider policy remains server-owned.

SDP is limited to **65,536 UTF-8 bytes**. Structural checks require version 0,
origin/name/timing lines, an audio media section, well-formed field lines, and
no unexpected control characters. These are not full SDP negotiability checks.
The JSON body is capped at **98,304 bytes before parsing**, including streamed
requests without Content-Length; escaping/encoding overhead counts. The provider
JSON response is capped at **131,072 bytes** and its SDP has the same SDP bounds.

Successful creation returns **201** with exactly:

```json
{"session_id":"live_fictional_123","sdp":"<validated SDP answer>","duration_seconds":300}
```

Require provider status 201, JSON, `session.id`, and
`transport: {type: "webrtc", sdp: ...}`. Validate an opaque 1–128-character session
ID using ASCII letters, digits, underscores/hyphens; preserve its value/prefix.
Discard other provider metadata. Return no configuration, secrets or raw errors.

### Explicit and late-session cleanup — October 26

`POST /api/voice/sessions/{session_id}/end` requires JSON `{}` and no query
parameters. Only a validated ID returned by this server process may be closed;
unknown IDs return 404 `voice_session_unknown`. Extra configuration/body fields,
invalid IDs and malformed JSON return 422; media/body limits remain 415/413.
No profile/owner or provider URL is accepted.

The adapter makes one POST to the fixed
`https://api.openai.com/v1/live/sessions/{session_id}/hangup`, with the server
credential and a 3-second I/O timeout, no redirects or retries. Empty-result
200/204 responses map to app 204 with no body. Repeated completed End returns
204 without another provider request; concurrent End returns 202
`{"status":"closing"}`. Failed closure returns sanitized 502/504
`voice_close_unconfirmed`; repeated requests do not retry a failed attempt.
The allowlist/close outcomes contain only IDs in process memory, never SQLite,
audio or transcripts. They are lost on restart, are not authentication, and are
intended for this single-process localhost prototype. TODO: bounded ledger
retention, multiworker ownership and provider reconciliation before broader use.

The browser preserves an already-sent, 15-second-bounded creation request after
End so it can read and close a late session ID. It never applies that SDP answer
or changes newer/disposed UI state. Close uses a bounded keepalive request.
If FastAPI observes a disconnected creation requester after provider success,
it attempts the same close and returns 409 `voice_start_abandoned` if deliverable.
An unknown ID after timeout, process/browser crash, or disconnect race cannot be
reconciled by these paths. Neither keepalive nor disconnect detection guarantees
delivery/termination.

Provider compatibility TODO: the official hangup reference describes SIP calls;
the general management guide names hangup as a close mechanism. Using it for
orphaned WebRTC sessions is an explicitly unverified assumption, covered here
only with mocks. Do not claim confirmed termination/cost reconciliation from
this fallback. The normal channel path confirms only on `session.closed`.

## Server policy and transport

One HTTP POST to `https://api.openai.com/v1/live/sessions` with a server-only
Authorization header, a **10-second I/O timeout**, and **no retries or redirects**.
Network failure may leave creation outcome unknown; do not automatically create
another session. The timeout bounds socket I/O, not strict total wall-clock time.

The server constructs `session.model: "gpt-live-1"`, fixed `marin` voice,
`store: false`, `triggers: []`, and `transport: {type: "webrtc", sdp: ...}`.
Every start creates a fresh transport/session with no fork or prior-session ID.
The server maps approved history to `session.input`, using one `input_text` part
for user messages and one `output_text` part for assistant messages, or [] if
empty. Neither history roles nor content can alter the model/instructions/policy
fields. Both prompt layers warn that captions can be approximate or interrupted
and must not be treated as confirmed playback/completion.
Responses delegation is now explicitly authorized. Its model comes only from
the backend process's `VOICE_BACKEND_MODEL`; `session.delegation` is
`{type: "responses", responses: {model, instructions, tools: [], tool_choice: "none"}}`.
No tools, native Decisions triggers, audio recording or transcript persistence
are added. Provider-managed delegation may use the current conversation context;
no history database or retrieval source is connected.

Both prompts live in `prompts.py` beside this contract. `LIVE_INSTRUCTIONS` is
sent only as `session.instructions`: flexible listening/answering, short speaking,
interruption/backchannel, minimum safety and `<|SpawnThinking|>` guidance.
`BACKEND_INSTRUCTIONS` is sent separately as
`session.delegation.responses.instructions`: the shared conversation/safety policy
plus reviewed scope, permission, age-sensitive wording, context/privacy limits and
nuanced response conditions. Both support short echoes, fuller reflections and
selective summaries using the user's own words without mechanical repetition.
Genuine questions invite answers; activity suggestions and deliberate reframes
still need permission unless specifically requested. No RAG is connected; future
supplied passages cannot override scope, safety or consent. See the readable
[system prompt](../../../../docs/chat-system-prompt.md). Neither prompt is accepted
from the browser.
The former all-in-one instructions/ban on delegation are superseded. Live has
no top-level `tools` field; the empty list belongs under delegated Responses.

Startup `session.client.data_channel` permissions are exactly:

| Direction | Event types | Intended next-interface use |
| --- | --- | --- |
| Client | `session.close` | Explicit stop |
| Server | `session.started`, `session.closed`, `error` | Startup, close and errors |
| Server | `session.input_transcript.delta`, `session.output_transcript.delta` | User/assistant caption bubbles |

Server selectors use `{ "type": "event.name" }`; neither direction uses `all`.
No browser session update/start, instruction/context append, delegation-command,
nested Responses or raw audio events are allowed. Delegated Responses runs at the
provider with the server-owned configuration, without widening browser permissions.
WebRTC carries audio. These permissions now drive the frontend chat controller.
Typed messages use separate HTTP without widening channel permissions.
Mute/Unmute only toggle local microphone tracks. They do not pause assistant
playback, end the provider session or stop billing; no provider mute events or
acknowledgments are needed or permitted.
Live transcript deltas use timeline intervals, with no Realtime item ID/final-turn
event; do not reuse the earlier Realtime transcript plan unchanged.

The **300-second duration** is a server-owned browser voice policy, separate from
the HTTP timeout and guided breathing duration.
The current Live creation schema has no configurable duration field; reporting
this value does not enforce provider expiry or bound total cost. The frontend
timer begins at Active, stops capture/playback at the limit and attempts graceful
close. Missing acknowledgment is reported. Provider reconciliation after browser
suspension/crash remains TODO.
It does not authorize a forced exit from open-ended text chat.

`store: false` disables later session forking/recording retrieval. It does **not**
establish general provider retention, no-training, zero-retention or fully local
processing. Audio goes to OpenAI when a configured client connects. HTTP collects
no audio; captions are transient and not saved. Account/data controls still need
review. The prompt is not a crisis detector or pre-playback check. Emergency/exits
are application-owned. Browser cleanup has mocked checks; transcript persistence,
retention/deletion and content evaluation remain TODOs. No clinical/monitoring claim.

## Independent typed messages — October 26

`POST /api/chat/messages` requires JSON with nonempty `message` (at most 8,000
UTF-8 bytes), optional `history` (default [], at most 16 items):

```json
{"message":"A fictional question","history":[{"role":"user","content":"Earlier fictional context"}]}
```

History permits only user/assistant roles and nonempty content strings, at most
8,000 bytes each/32,000 combined. Reject developer/system roles, extra fields,
query parameters and duplicate JSON keys; the 98,304-byte wire bound applies.
No owner/profile, SDP, microphone permission, voice session or saved record access.

The server makes one POST to `https://api.openai.com/v1/responses`, using only
VOICE_BACKEND_MODEL, the reviewed backend prompt plus a typed-channel instruction
that preserves the conversation policy,
current supplied typed context, store:false, tools:[], tool_choice:none and
max_output_tokens:1024. Same server credential, 10-second I/O timeout, no redirects
or retries. This provider endpoint does not itself persist messages; the separate
storage PUT saves completed typed pairs. No audio/caption persistence. Require provider 200,
completed response/assistant-message shapes, and nonempty output/refusal text at
most 8,000 UTF-8 bytes. Return only 200 `{"reply":"..."}`.

Typed errors use the sanitized envelope: 413 request_too_large, 415
unsupported_media_type, 422 validation_error, 503 chat_unconfigured, 502
chat_provider_unavailable/chat_provider_invalid_response, 504 chat_provider_timeout.
Frontend timeout is 15 seconds for creation/text, preserving the shared client's
8-second default elsewhere. The frontend supplies the same recent visible
conversation to either mode: completed typed messages and approximate voice
captions, at most 16 whole messages / 6,000 UTF-8 bytes. Failed/pending typed
messages are excluded; older context can be omitted. Sending text ends capture
and uses Responses; explicit microphone selection creates a new Live session
with that shared context. Messages stay visible across mode changes and voice
End/restart, then clear on End chat/navigation. No automatic resume or recording.

## Sanitized errors

```json
{"error":{"code":"voice_unconfigured","message":"Voice is not configured on the local server.","fields":{}}}
```

| Status | Codes |
| --- | --- |
| 413 | `request_too_large`, `sdp_too_large` |
| 415 | `unsupported_media_type` |
| 422 | `validation_error`, `invalid_sdp` |
| 503 | `voice_unconfigured` |
| 502 | `voice_provider_unavailable`, `voice_provider_invalid_response` |
| 504 | `voice_provider_timeout` |

Messages are fixed, never provider exception/status/body text, submitted field
names/values, URLs, keys or internal validation diagnostics.

## Verification

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 backend/.venv/bin/python -m pytest -p no:cacheprovider -q -c backend/pytest.ini backend/app/features/voice/tests backend/tests/test_boundaries.py backend/tests/test_shell.py
```

Tests use mocked provider HTTP responses plus a real-connection tripwire: missing
configuration, strict input/byte bounds, fixed policy/permissions, projected
success, failures/timeouts, malformed responses and no retries/redirects. Shell
and layer tests exercise stateless registration. No paid call, microphone/browser
check, live-model behavior or deployment verification is claimed.

Official documentation checked October 22/26, 2026:
[Live creation](https://developers.openai.com/api/reference/resources/live/methods/create),
[WebRTC](https://developers.openai.com/api/docs/guides/voice-webrtc),
[Live management](https://developers.openai.com/api/docs/guides/live-conversations),
[Hangup reference](https://developers.openai.com/api/reference/resources/live/subresources/sessions/methods/hangup),
[Live prompting](https://developers.openai.com/api/docs/guides/live-prompting),
[Responses delegation](https://developers.openai.com/api/docs/guides/live-delegation).


## Dictation increment — October 27, 2026

The user explicitly approved OpenAI recording transcription, replacing the failing
browser recognizer. POST /api/chat/transcriptions has a separate bounded JSON
contract in [DICTATION.md](DICTATION.md). It adds text to the editable draft only;
it does not create a Live/Responses conversation or persist audio. Existing voice,
typed generation and persistence behavior remains. This supersedes earlier
no-transcription-endpoint boundaries for this narrow increment.
