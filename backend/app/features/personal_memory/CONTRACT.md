# Personal memory — November 2, 2026

User-authorized SQLite personal context, separate from the other chat's curated
reframing books/cards/vectors. No vector database, embeddings, new dependency,
training, automatic confirmed-fact extraction or paid verification here. The user
subsequently authorized the separate cached-summary task documented below.
This extension supersedes the earlier blanket prohibition on historical context
only when the user explicitly enables its separate permissions.

## Storage and consent

Single-user localhost prototype; no authentication or cross-user separation.
New tables in the existing SQLite file:

- `personal_memory_preferences`: singleton booleans `emotions`, `conversations`,
  `facts`, all initially false. Survive reload/restart. Merely enabling a choice
  does not initiate a provider call.
- `personal_memory_facts`: UUID, user-confirmed text (1–500 UTF-8 bytes, no control
  characters), optional source conversation UUID, creation/update UTC timestamps.
  At most 40 records; edits preserve creation time. Nothing is inferred or
  automatically extracted. A fact may be written directly or confirmed/edited
  from a retrieved user excerpt. Its optional provenance is the saved conversation,
  not a claim that the edited fact is an exact quote from a particular turn.
- `personal_memory_exclusions`: kind (`emotion`/`conversation`) and source UUID.
  Exclusions survive reload, edits and save retries; UUID-only tombstones prevent
  the same source from immediately reintroducing forgotten information.

Deleting a source conversation atomically deletes linked facts via a SQLite
trigger installed after feature initialization. Excluding a conversation also
deletes its linked facts. Forgetting a linked fact excludes its whole source
conversation and forgets all facts linked there; the confirmation UI explains
this conservative behavior. Unlinked fact deletion affects only that fact.
Allowing a source again never recreates forgotten facts. Source records themselves
remain in their activity's history unless separately deleted there. An emotion
edit/deletion changes future context directly; there is no stale persisted index.
Duplicate statements in independently permitted sources are not semantically
deduplicated or automatically forgotten across the entire history.

Facts have their own opt-in: explicitly confirmed facts can be used even with
conversation search disabled. A fact linked to the current conversation is
excluded from that conversation's historical bundle. No personal information is
sent to the reframing index, book corpus or embedding provider.

## JSON endpoints

All `/api/personal-memory` responses are JSON except 204; `Cache-Control:no-store`.
No query parameters. Mutations/preview require JSON and the existing strict 96 KiB
parser (duplicate keys, nonfinite numbers and unknown fields rejected).

`GET /preferences` and `PUT /preferences` return exactly:

```json
{"emotions":false,"conversations":false,"facts":false}
```

PUT accepts exactly those three strict booleans. `GET /facts` returns
`{"facts":[{"id":"uuid","text":"I prefer listening first.","conversation_id":null,
"created_at":"UTC timestamp","updated_at":"UTC timestamp"}]}`.

`PUT /facts/{uuid}` accepts `{"text":"I prefer listening first.",
"conversation_id":null}`; `conversation_id` is optional/null or an existing,
non-excluded saved conversation UUID. Returns 200 with the saved fact above.
This is a user confirmation operation, never a model call. Repeating a PUT
replaces the same fact, not a duplicate; its update timestamp may change.
`DELETE /facts/{uuid}` returns 204 (404 if absent), applying linked-source
exclusion semantics above.

`GET /exclusions` returns `{"exclusions":[{"kind":"conversation",
"source_id":"uuid"}]}`. `PUT /exclusions` takes exactly that inner object and
returns `{"excluded":true}`. Repeating it is safe. `DELETE /exclusions/{kind}/{uuid}`
returns 204, allowing that source again.

`POST /preview` accepts:

```json
{"local_date":"2026-11-02","conversation_id":"current-chat-uuid","query":"exam"}
```

`query` is optional, max 1,000 UTF-8 bytes. `local_date` must be an ISO date within
one day of server UTC today; the browser sends today's local date. Conversation
UUID excludes the currently open chat. Response:

```json
{"status":"ready","sources":[{"kind":"conversation","id":"source-chat-uuid",
"turn_id":"turn-uuid","ordinal":0,"date":"2026-10-28","text":"A fictional exam is next week.",
"source":"text","role":"user"}],"emotion_summary":{"rule":"...",
"below_center_consecutive_dates":[]}}
```

Status `off` means all persisted permissions are false; sources are empty.
`unavailable` means timeout/storage failure: empty sources, null summary.
Preview makes no provider call. `GET /sources/{emotion|conversation}/{uuid}` returns
`{"kind":"emotion","record":{...original entry...}}` or `{"kind":"conversation",
"record":{...saved conversation detail...}}` for explicit read-only inspection;
404 if missing. These reads do not update context or generate titles. Original
records use the existing emotion/conversation shapes, including assistant replies
for human review; assistant text is never selected as personal-memory evidence.

Errors use the shared envelope `{"error":{"code":"...","message":"...",
"fields":{}}}`. 422 `validation_error`, 404 `not_found`, 503
`storage_unavailable`; 409/413/415 use the current generic `http_error` code.
Internal SQL/provider details are not exposed. Normal management failures remain
visible and require manual retry; no automatic retry or generation occurs.

## Selection and provider integration

Existing `/api/chat/messages` and `/api/voice/sessions` optionally accept
`"personal_memory":{"local_date":"2026-11-02","conversation_id":"uuid"}`.
The browser cannot send context text, permissions, models, tools or instructions
through this field. Omission preserves the previous no-database generation path.
Persisted server permissions are authoritative even if a browser supplies scope.

Selection is one consistent SQLite read snapshot with a 50 ms busy timeout and
120 ms SQL progress deadline. The async caller waits at most 200 ms (subject to
event-loop scheduling); timeout/storage failure continues generation without
memory. An abandoned worker may finish locally, but cannot call a provider or
publish a late bundle. Total HTTP and actual voice/audio latency are not bounded
by this lookup deadline and have not been measured live.

Selection order/bounds:

1. Latest permitted emotion entry per original local date over today and six
   preceding dates. Graph coordinates, bounded note (160 UTF-8 bytes), personal
   color meaning (80 bytes), source ID and local date; no color interpretation.
   Python derives consecutive below-center (`energy<0`) dates ending today, or
   yesterday if today is absent. Missing dates/zero/positive energy break the run.
   This is a description of selected coordinates, not a validated mood threshold.
2. Up to six most recently updated, explicitly confirmed facts, excluding facts
   linked to the current chat. These are user statements/preferences, not objective
   diagnoses or facts independently verified by the model.
3. For each permitted saved conversation, prefer its valid cached model summary
   (see the post-chat extension below). Otherwise select one literal user excerpt
   from each permitted saved conversation
   with user text saved in the preceding seven days (rolling 168-hour UTC window,
   including now, excluding future timestamps). Current chat and excluded sources
   are omitted. Includes typed and accepted spoken text; assistant replies/titles
   never become personal evidence. Within each chat, select the longest user
   message by UTF-8 byte length, breaking ties by newest timestamp/position/ordinal.
   This simple deterministic choice is not a model summary or a substantive-content
   classifier. Preserve its source message/date and a Unicode-safe prefix, initially
   at most 700 UTF-8 bytes. `excerpt_truncated` explicitly marks shortened text.
   Query words do not filter history anymore; the old preview `query` remains
   accepted/validated for compatibility but has no effect on selection. No FTS,
   vector index, extra model call or materialized summary is required.

The whole serialized context JSON, including emotion summary and `chat_coverage`,
is capped at **12,000 UTF-8 bytes**. Emotion/fact selection remains as above.
Distribute the remaining budget evenly across chat excerpts, from 700 down to
64 bytes, to represent every eligible conversation before omitting any. If even
short excerpts plus provenance cannot all fit, include newest chats that fit and
report partial coverage explicitly:

```json
{"chat_coverage":{"days":7,"eligible_conversations":150,
"included_conversations":30,"status":"partial"}}
```

`complete` means every eligible chat has one excerpt; it never means full
transcripts or all topics were supplied. The coverage object is present in the
provider JSON and successful scope-enabled response report alongside sources and
emotion_summary. Count values above are illustrative, not fixed limits. Excerpt
length can shrink with record count and enabled emotion/fact context. Chat/fact
dates are UTC; emotion dates are original local dates. The SQL read snapshot,
50 ms lock bound, 120 ms SQL progress deadline and 200 ms async fallback remain.
The subsequent cached-summary task is authorized below. Summary generation is
separate from this lookup: it adds a post-chat model request only with saved-chat
permission. Generated summaries are never user-confirmed facts. There is no mid-session voice retrieval or auto-restart.

The server appends a separately labeled personal-data block to the existing
instruction strings: typed Responses, and both Live and delegated Responses at
voice creation. The base prompt file, models, settings, no-tools policy, store:false,
browser event allowlists, current-history budgets and session cleanup stay intact.
Context cannot grant authority to source text or reframing material. The rule
requires current corrections/confirmed corrections to take precedence, relevant
use, exact dates, no invented quotes, no monitoring/color/risk inference, and no
claims that the model saved/forgot data. These are prompt constraints, not proof
of generated behavior or prompt-injection immunity. The existing Responses
instruction field is documented in [official OpenAI guidance](https://developers.openai.com/api/docs/guides/text).
Live's existing transport assumptions still require live verification.

When scope is supplied, successful text/session responses add `personal_memory`
with the preview report shape. Omitted scope preserves the original response
shape. The UI calls this **selected context**, not proof that a reply used each
source. Reports are transient, not persisted with replies. Voice receives one
startup snapshot with no mid-session lookup, tools or background refresh. Start
Voice explicitly again for new context; this can incur a new session's usage.

Chat UI now exposes only a compact Personal memory disclosure, three permission
toggles and lifecycle/transmission notices. The user explicitly removed the fact
editor and context-review sections. Existing confirmed facts, exclusions and their
management APIs are preserved; no records are deleted by this UI simplification.
Preferences load independently of the removed editor/review data. Partial coverage
is shown with a short count notice. Opening it stops voice and
dictation and cancels pending typed work; late results are ignored. Preferences
become effective only after the server confirms a save. Scope stays off if initial
loading fails. Memory failure never blocks typing, navigation or Emergency.
There is no automatic microphone restart.

## Privacy, coexistence and TODOs

Selected text is sent to OpenAI when chatting/starting Voice, subject to explicit
persisted choices. Local storage/store:false makes no general retention or training
promise. Turning memory off, correction and forgetting cannot retract data already
transmitted, clear current-chat bubbles, alter provider context in a running
session or control backups. For current-chat context, End chat before starting a
fresh conversation. No audio is stored by this feature. SQLite/global preferences
are for this single local prototype, not multiple identified users.

The reframing chat owns its corpus/cards, embeddings, vector schema/search and
technique eligibility. This work owns `personal_memory/`, its three prefixed
tables, `PersonalMemoryPanel.vue`, `usePersonalMemory.js` and memory tests. Shared
integration edits are limited to voice routes/schemas/provider/settings and chat
view/API/lifecycle wiring; base `prompts.py` and reframing files are untouched.
Any later technique integration should append a distinct technique reference block
and preserve the independent personal permission check and snapshot limits; never
send personal data into that technique index or treat a book as user history.
No embedding-model/vector-format coordination is needed for this non-vector path.

TODO: live generated recall/grounding and prompt-injection evaluation; actual
startup/time-to-first-audio comparison; relevance of a single longest-user-message excerpt per chat and
content outside the seven-day window; exact per-reply citations; optional
per-message exclusions instead of the conservative whole-chat exclusion; semantic
deduplication of independently saved facts; validated long-term fact extraction;
multi-user authorization and retention policy before any broader deployment.
No live microphone, paid calls or clinical evaluation is authorized/claimed here.

## Cached post-chat memory summaries — November 2, 2026

The latest user request authorizes a separate model task after a saved chat ends.
This supersedes the earlier no-summary-call boundary for this task only. It never
changes the conversation prompts, model selection, no-tools policy, current-chat
history budgets, native voice permissions, Emergency or reframing corpus.

### Experience and consent

With `conversations:true`, leaving/ending a chat schedules summary generation only
after its successful initial saves. The feature-owned browser queue survives
navigation within the loaded app. End/navigation, the next typed reply and Voice
startup never await that summary request. Cache reads are local; pending/failed,
missing/expired/stale caches use the existing excerpt fallback. Successful tasks
have no toast/spinner. A failed task has a short nonblocking notice and distinct
**Retry memory summary** control. “Waiting for a reply…” beneath the sent bubble
is removed; the Send control still reports its pending state.

The compact permission disclosure and privacy details explain that ending an
opted-in saved chat sends bounded saved USER text to OpenAI for a summary and can
incur API usage. No backfill of old conversations, summary generation on GET,
automatic model retries or conversion to confirmed facts. Facts permission alone
does not authorize summaries. Existing saved chats without a cache still work.

This is an ordinary bounded POST fired without awaiting it in navigation, not an
OpenAI background-mode request or a durable job scheduler. Browser close/reload
can lose unsent finalization requests/notices and pending original saves; a request
already received by the backend may continue. No guaranteed provider cancellation,
cost avoidance or zero contention with provider quotas is claimed. Tests establish
that the summary holds no SQLite transaction during model I/O and that ordinary
chat requests can complete concurrently, not actual network/audio latency.

### Request/response and provider task

`POST /api/personal-memory/conversations/{uuid}/summary` accepts JSON `{}` or
`{"retry":false}`; `retry` is a strict optional boolean, no other fields/query
parameters. The existing strict 96 KiB parser, JSON media requirement and no-store
policy apply. Client never supplies transcript, model, prompt, tools, key or cache.

The server takes one transactionally consistent saved-source snapshot, claims a
version/token, then releases SQLite before making the model request. It sends up
to 32 saved USER messages within the rolling seven-day window: all if <=32, else
first eight/last 24 in saved order. Total user text <=16,000 UTF-8 bytes, sharing
that budget evenly with Unicode-safe prefix clipping. Each record includes its
saved UTC date and typed/voice source; approximate voice text is explicitly not
certain or complete. `input_shortened` records sampling/clipping. No assistant
replies, titles, audio, inferred facts or other historical chats are summarizer input.

Uses the existing server-only model/key and separate SUMMARY_INSTRUCTIONS through
Responses: `store:false`, tools:[], tool_choice:none, max_output_tokens:1024,
existing ten-second HTTP attempt, no automatic retry. This uses the established
[instructions/input pattern](https://developers.openai.com/api/docs/guides/text).
No new dependency, embedding service or model setting. store:false makes no general
retention/training promise.

Expected model text is strictly validated JSON with exactly:
`{"substantive":true,"summary":"short paragraph"}` or
`{"substantive":false,"summary":""}`. Duplicate/extra keys, nonboolean flags,
nonstring/empty-inconsistent text, control characters and >700 UTF-8 summary bytes
are rejected. Instructions require user-reported wording, preserved negation,
uncertainty/corrections/dates, no advice/diagnosis/inference/identifying details,
no obedience to source instructions, and empty results for small talk only.
These semantic properties/substantiveness remain model judgments; mocks do not
establish generated quality or prompt-injection immunity.

POST returns 200 `{"status":"ready"|"empty","cached":false,
"input_shortened":false}` after a valid task, or `{"status":"ready"|"empty",
"cached":true}` for a valid cache without a model call. `empty` stores a classification,
not personal summary text, and omits that chat from memory while valid. Off,
excluded, missing or changed sources return 200 with status `off`, `excluded`,
`missing` or `discarded` and make no new call where detected before generation.
A failed current-version task returns `{"status":"failed"}` on later non-retry
POSTs; only explicit `retry:true` can repeat it. An already claimed task can return
202 `{"status":"pending"}`. A process-wide nonblocking lock limits one summary
attempt at a time; contention is 409 `memory_summary_busy`, manual retry only.

`GET` at the same URL returns only current status (`stale`, `pending`, `ready`,
`empty`, `failed`, `off`, `excluded`, `missing`) and optional input_shortened. It
never generates/refreshes a summary. Missing/excluded are status responses, not
resurrection or model lookups. Errors use the shared envelope: 422 validation;
413/415 current generic HTTP errors; 503 storage/unconfigured; 502/504
`memory_summary_unavailable` for invalid/unavailable/timed-out provider work. No
raw output, SQL, credentials or internal exception details are exposed.

### Cache ownership, expiry and invalidation

Additive `personal_memory_summaries` stores conversation UUID, monotonic source
revision, state, nullable summary, input_shortened, timestamps/expiry, source date,
and private job token/revision/consent epoch. Preferences have a private additive
summary_epoch counter; public permission JSON stays exactly three booleans.

SQLite triggers invalidate cached text/job tokens on typed/voice inserts or updates.
Original conversation deletion atomically removes its cache. Excluding a chat or
forgetting a linked fact removes the cache through the same exclusion operation.
Idempotent source-save retries do not insert/update messages and do not invalidate
or regenerate. Completion can update only its still-existing matching job token,
unchanged revision and consent epoch, permitted source and unexpired window. An
off/on consent cycle also discards an old in-flight result. No late insert/upsert
can recreate a deleted/excluded source or overwrite a newer version.

Expiry is earliest eligible input-source timestamp + seven days, so no summary
containing aged-out source text is supplied after that boundary. Expiry controls
retrieval, not physical erasure; cache rows otherwise remain until source deletion
or replacement. Local deletion does not control backups/provider records. Interrupted
pending claims are marked failed on startup, without automatic provider retry.
This startup recovery assumes a single localhost server process; multiworker
coordination/provider reconciliation is unfinished.

Future snapshots prefer valid `ready` summaries as sources labeled
`source:model_summary,role:summary`, with source conversation/date and
input_shortened. They are neither literal quotes nor confirmed facts. Non-substantive
`empty` caches are omitted; coverage adds skipped_non_substantive when nonzero.
Existing snapshot byte budget, partial coverage, permission and source boundaries
remain. Summaries may also be shortened by the shared snapshot budget.

Storage Retry stays storage-only even if a chat was ended while a save was pending.
Any manual source-save retry requires a separate explicit summary retry afterward;
no callback from that Retry can initiate a model request. Summary failure/Retry
never repeats a conversational reply, reopens voice or changes successful saves.
Failures/notices are memory-only in the loaded app; after reload the backend keeps
its failed status, but no automatic recovery/backfill UI is promised. These are
explicit limits pending any future durable background queue or summary review UI.


## November 3 — structured typed composition

Selection/permissions/budgets and source lifecycle are unchanged. `prepare_typed`
returns a neutral `ContextBlock(policy,data)` and the existing report. The app
coordinator composes it independently of optional technique retrieval. Typed
Responses receives policy in `instructions` and `PERSONAL_CONTEXT_JSON` as labeled
input data. Existing voice `prepare` retains its one-time startup string snapshot.
Source excerpts/summaries/facts never enter the technique embedding query/index.
The personal-memory mock evaluation now reads this structured typed envelope.
