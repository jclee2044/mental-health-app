# Typed reframing reference contract

Implemented November 3, 2026, following `docs/reframing-integration-plan.md`.
Observed results live in `docs/reframing-implementation-evidence.md`; mock results
are distinct from real embedding relevance and generated replies.

## Ownership and configuration

This feature owns original cards, source metadata, embedding HTTP, complete-index
validation, scoring and optional async lookup. It has no browser endpoints and no
access to the personal-history database. Shared `conversation_context.py` composes
injected feature callbacks; sibling features do not import each other.

`REFRAMING_ENABLED` defaults to `0`: no corpus/index/network work. To enable, supply
`REFRAMING_ENABLED=1`, `REFRAMING_INDEX_PATH`, `REFRAMING_EMBEDDING_MODEL`,
`REFRAMING_DIMENSIONS`, `REFRAMING_MINIMUM_SCORE` and the existing `OPENAI_API_KEY`.
Paths must resolve inside the project with `.sqlite3` suffix. No default model,
dimension or similarity threshold; invalid enabled configuration returns unavailable
without embedding. Configuration is read at app construction; restart after changes.
Index paths and keys never come from the browser or appear in public errors.

## Corpus and SQLite

`data/cards.json`: 26 original summaries/examples, 19 active conversational cards
and seven reference-only variants/procedures. Fourteen core families remain
represented. Each active card has one summary plus three ordinary-language search
expressions: 76 vector documents. Source editions/hashes and EPUB section or PDF
positions retain attribution; the original books are neither ingested at runtime
nor shipped. `docs/reframing-content-review.md` records the review.

Strict validation rejects unknown fields, missing sources/families, invalid text,
duplicate IDs and active procedures. Eligibility cannot be overridden by similarity.
All cards/metadata contribute to the corpus hash, including reference-only notes.

Standalone SQLite tables: `reframing_metadata(id,payload)` and
`reframing_vectors(id,card_id,document_sha256,vector)`. Complete IDs/hashes, corpus
hash, embedding provider/model/dimensions and finite nonzero normalized vectors
must match. Publication builds a complete temporary file and uses an exclusive
atomic hard link; never overwrite an existing index. Reads use `mode=ro`, query-only,
50ms busy timeout, a 200ms SQL progress limit and a consistent read transaction.
Missing/stale/corrupt/partial indexes fail before any query embedding. No query or
retrieved personal text is saved. SQLite is the vector store; exact cosine scoring
and family deduplication run in framework-free Python. No vector extension/server.

## Internal lookup and budgets

```python
result = service.prepare(current_message, allow_reference_lookup=True, budget=6000)
```

The literal-True guard controls lookup only. It is not a semantic intent, refusal,
safety or consent classifier. Typed v1 performs operator-enabled pre-retrieval on
active requests, including some turns which need no reframe. Natural-language
stopping/refusal/urgency is governed by the existing reply policy, not recognized
by this guard before embedding. Explicit UI cancellation/disabled states skip work.
Do not claim zero embedding delay for an urgent sentence submitted as ordinary chat;
independent Emergency and exits remain immediate. No additional classifier/tool loop.

Full current message: at most 8,000 UTF-8 bytes, with line breaks/tabs preserved.
No query truncation, rewriting model call, concatenated personal sources or history.
Malformed Unicode/control characters are rejected. Search takes at most two eligible
families above the explicit threshold. Whole cards, their safeguards and provenance
must fit the typed **6,000-byte** allocation; omit a whole card rather than slice JSON.
The standalone formatter supports a configurable maximum of 10,000 bytes. Similarity
is not a probability, and `ready` does not prove appropriateness or response use.

`BoundedLookup` waits at most two seconds asynchronously, with at most two actual
workers per app/process. It rejects excess work instead of queuing. A timed-out or
cancelled caller leaves its slot occupied until the actual worker exits. Workers
only retrieve, never invoke generation; late references are discarded. Shutdown
rejects new work without waiting for an already-sent bounded HTTP attempt.
Socket and SQL timeouts are not total operating-system latency guarantees.

`OpenAIEmbedder` uses fixed `https://api.openai.com/v1/embeddings`, no redirects,
no automatic retries, a five-second socket timeout and a 4MiB projected JSON response.
One query may be 8,000 bytes; multi-input batches remain at most 16 × 4,000 bytes and
24,000 total bytes. Exact returned model, dimensions and unique complete indices
are checked. `builder.build_export(...,allow_api_usage=True,max_requests=N)` preflights
all batches and an explicit request cap. The 76-document build is five requests
(16/16/16/16/12). A failure publishes no partial export; earlier calls may cost usage.
Neither registration nor storage Retry invokes the builder.

## Typed JSON and source placement

`POST /api/chat/messages` retains its existing request:

```json
{"message":"Can we examine this fictional thought?","history":[],"personal_memory":{"local_date":"2026-11-03","conversation_id":"a valid UUID"}}
```

`history` and `personal_memory` are optional. Existing strict field/role/byte and
server-authoritative personal permissions apply. Browser prompts, model IDs,
references, lookup flags and thresholds are forbidden. Existing sanitized error
shape remains `{"error":{"code":"...","message":"...","fields":{}}}`.
An abandoned request returns HTTP 409 `request_abandoned` before generation.

Response adds an optional report:

```json
{"reply":"A fictional reply.","reframing":{"status":"ready","card_ids":["counterexample"]}}
```

The existing optional `personal_memory` report remains independent. Disabled library
reports are omitted for backwards compatibility. Statuses: `off` (internal disabled),
`skipped` (internal explicit lookup guard), `ready`, `no_match`, `unavailable`.
Reports contain no scores, queries or credentials and remain transient. The browser
shows a nonblocking unavailable notice; ordinary replies/saves remain usable.

Stable source policies go in Responses `instructions`; two separately labeled input
messages hold `PERSONAL_CONTEXT_JSON` and `REFRAMING_TECHNIQUE_REFERENCE` data before
bounded current-chat history and the current user message. Values never become
instructions. Preserve literal user excerpts, dated confirmed facts and unverified
model summaries as distinct source types. Personal allowance remains 12,000 bytes.
Personal permission failure does not enable access; technique failure does not
change memory permissions. Selection runs independently/in parallel. The coordinator
checks disconnect before selection and before one ordinary reply call. No extra
intent/rewrite/generation call or automatic retry. Existing browser 15s timeout and
10s generation socket timeout remain; real elapsed time requires measurement.

Current request/correction/refusal/stop/no-question policy overrides any reference.
Ask and wait before a deliberate reframe unless specifically requested. At most one
relevant conversational move; listening/clarifying/no reframe remain valid. No new
guided procedure, hidden-motive inference, or attempts to overcome refusal. Replies
need not name techniques. Only supplied source metadata may be attributed.

Save Retry remains storage-only/idempotent. Personal summaries still consume saved
USER text only; assistant technique suggestions never become user evidence.
End/Emergency/overlays abort pending typed work and ignore late replies/reports;
drafts edited during a request remain unchanged on failure. Voice can receive the compact startup catalogue described below; no tools,
mid-session lookup or automatic microphone restart.

## Offline operations

The CLI remains offline and refuses output overwrite:

```sh
backend/.venv/bin/python scripts/reframing_kb.py validate
backend/.venv/bin/python scripts/reframing_kb.py plan --output backend/app/features/reframing/private/plan-new.json
backend/.venv/bin/python scripts/reframing_kb.py publish --vectors backend/app/features/reframing/private/embeddings.json --output backend/data/reframing-v1.sqlite3
backend/.venv/bin/python scripts/reframing_kb.py inspect --index backend/data/reframing-v1.sqlite3 --model MODEL --dimensions 1536
```

Exports include schema_version, corpus_sha256, documents_sha256, spec and every row's
id/sha256/vector. Imports are capped at 16MiB, reject duplicate keys/nonfinite values
and must be complete. CLI outputs must stay within the project. Errors use
`reframing_unavailable`, exit 2, without untrusted contents or paths. Do not publish
synthetic test vectors as an operational knowledge base. `private/` is ignored.

Official API field/response basis: [OpenAI embeddings](https://developers.openai.com/api/docs/guides/embeddings)
and [create embeddings](https://developers.openai.com/api/reference/resources/embeddings/methods/create).
Embedding matching and generated policy compliance require their own observed
checks, beyond the mocked/synthetic software tests.


## November 3 — approved voice startup catalogue

The user confirmed the feedback conversation was Voice and explicitly requested
library access. `prepare_voice_catalogue` supplies all 19 active operation
definitions, their complete `avoid` boundaries and bibliography at startup. It
omits extended notes/examples and page/section locators; never invent those locators.
Source indices refer to a source array; revision/hash identify the reviewed snapshot.
Seven reference-only entries remain excluded. This compact catalogue is not a
per-turn vector search. Typed vector retrieval is unchanged. The existing
`REFRAMING_ENABLED` server flag controls it; no browser configuration is added.

Catalogue JSON is labeled `session.input` user data before current-chat history,
separate from policy instructions. Stable policy goes to Live and its Responses
backend; Responses delegation supplies conversation context. No personal data is
placed in the catalogue or embedded. No tool/event/sideband or automatic microphone
restart. Catalogue preparation is local only, parallel to personal selection, with
a 200ms optional wait; no embedding/provider call. Bad corpus/timeouts fall back.

Catalogue content plus history must fit 7,500 UTF-8 bytes, leaving framing headroom
under Live's documented 8,192 startup-input-token limit. If the whole catalogue
cannot fit, preserve all accepted history, omit references and report unavailable.
Switching a longer typed chat into Voice can therefore lack references; use a fresh
chat for the full catalogue. Definitions/boundaries are never sliced to fit.

`POST /api/voice/sessions` can return `reframing:{status,card_ids,delivery:
"startup_catalogue"}`. Ready means listed operations were supplied, not selected,
applied or heard. Reports are transient and abandoned sessions cannot update them.
Existing explicit microphone selection, cleanup, End/Emergency and storage rules
remain. Existing voices retain their original snapshot; start a new chat/session
after backend reload. Source presence/mocked payloads do not establish generated
operation use, provider acceptance or spoken delivery.

API basis: [Live context](https://developers.openai.com/api/docs/guides/live-conversations)
and [Responses delegation](https://developers.openai.com/api/docs/guides/live-delegation).
