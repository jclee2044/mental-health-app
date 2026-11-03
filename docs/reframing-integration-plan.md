# Reframing integration plan after personal memory

November 2, 2026. Review baseline: commit `6242c3a` (`feat: add opt-in personal
memory and cached chat summaries`) plus the uncommitted independent reframing
package. This is a reviewed implementation plan, not activation or permission
to make provider calls. No application code was changed during this review.

**Recommendation:** retain the separate memory and technique stores, add a small
application-owned context coordinator, fix the integration boundaries first,
then connect typed reference retrieval. Preserve voice's existing startup-only
personal context until a separately scoped spoken-retrieval increment.

## Current implementation and verification

| Area | Current behavior |
| --- | --- |
| Current conversation | Bounded typed/spoken history; independent generation and storage; transient drafts/captions until accepted text saves. |
| Personal memory | Server-persisted opt-ins for logs, saved chats and confirmed facts. The browser supplies a scope, not records, model settings or tools. |
| Memory selection | Seven local dates of selected log details, up to six confirmed facts and one representation of each eligible saved chat in the rolling seven-day window. Current/excluded chats are omitted. |
| Cached summaries | A separately authorized post-chat model task, scheduled after initial saves and not awaited by navigation. User-only source text, strict output shape, source revision/job token/consent epoch checks, expiry and excerpt fallback. Summaries remain generated interpretations rather than confirmed facts. |
| Memory context | Up to 12,000 UTF-8 bytes, with explicit partial chat coverage. Lookup has local SQL and async fallback bounds. No personal embeddings or keyword filter. |
| Voice | Personal context is selected once when a Live session starts. No mid-session tools/lookups or automatic microphone restart. |
| Reframing | Nineteen active conversation cards, seven reference-only entries, 76 search representations, standalone index/adapter/build helper, disabled registration and no real vectors or chat wiring. |

Observed checks for this review:

- Backend: **306 passed**, one existing Starlette/httpx deprecation warning.
- Frontend: **136 passed**.
- Production build: passed; existing large-bundle warning remains.
- Non-mutating Oxlint and ESLint: passed.
- Relative-import AST inspection and a targeted mocked route/disconnect probe,
  described below. No real network/provider call or microphone was used.

Commands: project Python `pytest -c backend/pytest.ini backend/tests
backend/app/features -q`; `npm --prefix frontend test`; `npm --prefix frontend
run build`; from frontend, `npm exec --offline -- oxlint .` and
`npm exec --offline -- eslint . --no-cache`; `cat`, `rg`, numbered source reads,
Git status/log/diff, and project Python probes. The review did not rerun the
original checkpoint script: it passed during the preceding independent increment
and the personal-memory handoff records a later passing run. Repeat it for the
eventual code integration.

## Findings to address

### 1. Feature separation is already breached by relative imports

`voice/routes.py:19` imports `personal_memory.context`, `voice/schemas.py:4`
imports its `MemoryScope`, and `voice/provider.py:79` imports the memory summary
prompt. In the other direction, `personal_memory/routes.py:7` imports
`voice.http` and `personal_memory/summary_routes.py:8-9` imports voice exceptions.
Resolving relative AST imports confirmed all six dependencies.

The boundary test at `backend/tests/test_boundaries.py:31` inspects module names
without resolving `ImportFrom.level`. Consequently these imports pass a test
whose stated purpose is to prohibit them. This is a concrete maintainability/
installation-boundary defect, not evidence that the current running feature
fails: the complete suites pass. Do not extend this dependency cycle by adding
reframing imports to voice routes.

**Plan:** use application-owned contracts/composition and injected callbacks;
move genuinely shared strict HTTP parsing/provider error types to neutral modules;
resolve relative imports in the boundary check. Preserve feature-owned SQL and
domain logic. Avoid a generic plugin framework or unrelated refactor.

### 2. Disconnects are not checked before the next provider stage

`voice/routes.py:119-123` awaits memory selection and then starts typed generation
without checking whether the request disconnected. A direct Starlette Request
probe supplied a valid fictional body followed by `http.disconnect`, injected
an async memory selector and mocked reply provider. Observed: one provider call,
the disconnect still unread, and a fictional reply returned. This is an isolated
route probe, not a claim of a full browser/network cancellation test.

The frontend does reject late replies (`useChat.js:71-72`), which prevents stale
bubbles. It cannot by itself prevent a provider call that the server starts
after a request is abandoned. Voice has late-session cleanup after creation;
neither case justifies adding more unchecked work between awaits.

**Plan:** check request/disposal state before lookups and again before generation;
make the coordinator own continuation. A timed-out retrieval worker may finish
its current bounded embedding request but must not invoke generation, publish
context or restart audio. Do not promise cancellation of an already-sent request
or avoidance of all usage charges.

### 3. Dormant reframing limits do not match the existing chat

`voice/domain.py` accepts an 8,000-byte current message; reframing's
`domain.py:9` accepts 2,000 bytes and its adapter accepts 4,000 per input. Passing
a valid longer chat message directly into the current service would produce
`unavailable`. Quietly taking its first 2,000 bytes could drop a correction or
negation at the end.

**Plan:** align query embedding with the full accepted 8,000-byte current message,
validate against the selected model's limits, and keep build documents at their
existing 4,000-byte bound and batches at 24,000 bytes. Preserve the existing chat
limit. Test multilingual text and corrections near the end; do not silently
summarize/truncate a query or add a query-rewriting model task.

### 4. Lookup permission is not permission to change a perspective

`reframing/service.py:27-32` currently exposes `allow_reframe`; it is a literal
boolean guard, not an understanding of consent, refusal or the meaning of a
short reply such as "yes." No integration currently supplies it.

**Plan:** distinguish `allow_reference_lookup` from permission to apply a deliberate
reframe. A candidate card is optional reference material. Existing conversational
rules still ask and wait unless specifically requested; current correction,
refusal, stopping and no-questions requests take priority. Do not set the present
flag to true and describe that as consent enforcement. Do not treat a successful
vector match or a generated memory summary as consent.

For typed v1, recommend bounded backend pre-retrieval of optional references on
eligible, operator-enabled turns, with no extra model classifier/tool loop and
no required user mode selector. Application-known cancellation/disabled states
skip lookup deterministically. Conversational appropriateness and natural-language
permission remain model behavior requiring evaluation; this is not a hard intent
or safety classifier. If strict application-level semantic consent enforcement
is required, design an explicit consent interaction/state contract first rather
than infer it from loose keyword matching.

This choice has a real cost: without an intent classifier, optional lookup may
also run for typed greetings or requests that ultimately need no reframe. Do not
claim that free-text stopping or urgent wording is automatically recognized before
embedding. Keep the optional lookup delay short and test those cases explicitly.
An alternative is one read-only, model-requested lookup tool bound to the current
message by server code, but that changes the current no-tools response protocol
and adds a generation continuation on lookup turns. Do not introduce that extra
loop silently. Revisit the choice if measured unnecessary calls/latency outweigh
the simpler pre-retrieval path; Emergency and explicit UI exits never wait for it.

### 5. Data, policy, duration and context budgets need one composition boundary

`voice/provider.py:62` and `settings.py` append the personal-data block to the
instruction field. The block is labeled as untrusted data, but it still shares
the instruction channel with policy. This is a hardening concern, not a
demonstrated injection exploit. Do not append another opaque source string there.
The [official text-generation guide](https://developers.openai.com/api/docs/guides/text)
distinguishes high-level `instructions` from message input.

The typed browser timeout is 15s; generation has a 10s socket timeout and the
prepared embedding adapter has a 5s socket timeout. Adding those serially leaves
no margin. Those socket timeouts are not full wall-clock guarantees. The existing
backend policy alone is 16,549 UTF-8 bytes; personal data can add 12,000 and the
technique service currently allows another 10,000, before current/history text.

**Plan:** separate stable policy from labeled context data, preserve the personal
memory allowance, cap technique context independently, and put a short optional
retrieval deadline ahead of generation. Measure actual latency and model tokens;
byte budgets alone do not establish model context fit or cost.

## Architectural assessment from three perspectives

### Fast delivery and a simple coursework app

Optimize for a working typed path with few new moving parts; fear a rewrite that
delays the core experience. Reusing the current cards, SQLite and provider is
strong. A full vector server, extra intent model or a new chat mode would add
unnecessary work. The main likely failure is overbuilding routing while leaving
real retrieval unmeasured. Recommend a small coordinator, pre-retrieval and
typed-only rollout; preserve the existing app flow. Accept that the model's use
of optional references remains a separately tested judgment.

### Reliability, cancellation and data boundaries

Optimize for predictable fallbacks, current permissions and no work after an
abandoned stage. The memory snapshot/cache rules and immutable technique index
are good foundations. The critical concerns are the new serial API delay,
data/policy mixing, query-size mismatch and treating retrieval as permission.
The likely failure is a late/failed embedding delaying or invalidating an otherwise
valid reply. Recommend deadline/concurrency limits, disconnect tests, labeled
input, no retries and a failed-reference path that leaves ordinary chat usable.

### Long-term feature ownership

Optimize for separately testable features and understandable change ownership;
fear voice becoming the application-wide integration container. Separate stores
and original card provenance are strong. Mutual imports and an ineffective
boundary test already contradict the intended architecture. The likely failure
is every new feature needing edits inside voice and preventing independent
installation. Recommend neutral contracts, injected services and a strengthened
relative-import check before adding the next dependency.

The genuine tension is between less code now and explicit ownership/deadlines.
The small coordinator is worth doing; a general framework is not. Dedicated
vector infrastructure is a low-priority scalability concern for 76 documents.
The highest-value unknowns are actual relevance, end-to-end latency and whether
the model respects conversational permission when sources are present. None is
settled by the passing mocked suite.

## Concrete integration design

### Ownership and data path

Keep `personal_memory/` responsible for permissions, source selection, summaries,
SQL and source lifecycle. Keep `reframing/` responsible for cards, embeddings,
index validity, ranking and reference notes. Put a small context coordinator and
neutral context/scope types at the backend application layer. Route handlers
invoke that coordinator through app state; it receives feature services through
composition, not imports between sibling features.

```text
Validated typed message + current-chat history
  -> request still active?
  -> personal-memory selection (existing persisted permissions)
     + independent optional technique lookup (current message only)
  -> request still active? discard late lookup results
  -> stable policy + labeled personal data + labeled technique data
     + unchanged bounded current-chat conversation
  -> one ordinary reply generation
  -> transient source/status reports
  -> existing independent transcript-save path
```

Do not embed saved excerpts, cached summaries, confirmed facts, emotion logs or a
combined context bundle. The current message itself can contain personal text;
hosted embedding transmission/API usage needs disclosure and operator authorization
before enabling it. Personal-memory opt-ins neither enable nor disable the
technique library; the two permissions must not become conflated.

### Typed prompt and response contract

For typed Responses, recommend keeping stable conversation/safety/permission
policy in `instructions`. Supply personal data and technique reference JSON as
distinct labeled input content before the current message, with policy explicitly
defining their meaning and authority. Preserve the original user/assistant
history separately. Do not parse a concatenated policy string to recover data;
have the memory preparation interface return a structured bundle/report.

Maintain the distinction between literal user excerpts, user-confirmed facts and
unverified generated summaries. Nothing in a book describes a fact about the
user. Nothing in a summary selects a technique or grants consent. Current user
corrections win over older memory. Summarization still receives only saved USER
text; assistant technique suggestions must never become memory evidence.

Update the base prompt's old prohibition on the reviewed pattern capability only
for supplied conversational cards. Retain fixed skill steps and the exclusion of
guided procedures. With no supplied references, do not invent retrieval or claim
source-backed use. Keep the user's neutral reframing terminology and accurate
source attribution. Replies remain natural; no required technique names, card
menus, worksheets or mechanical sequence.

Keep the existing request JSON shape; the browser cannot submit retrieved text,
source eligibility, model IDs, prompts or similarity thresholds. Add an optional
`reframing` response report, for example:

```json
{"reply":"...","personal_memory":{"status":"ready","sources":[]},
 "reframing":{"status":"ready","card_ids":["counterexample"]}}
```

This is an illustrative response, not a change implemented here. Report statuses
remain off/skipped/ready/no_match/unavailable; they describe supplied references,
not proof of response use or applicability. Keep reports transient initially;
do not add new personal-history tables just to save debug metadata. A small
nonblocking unavailable notice is sufficient. Normal source/permission controls,
End, Emergency and editable drafts must remain usable throughout.

### Proposed budgets and failure behavior

- Personal data: preserve its existing 12,000-byte allowance and coverage logic.
- Technique data: initially at most two complete cards within **6,000 bytes**.
  Omit a whole card if it does not fit; never cut JSON or remove its safeguards.
  This is a proposed allocation to test, not a measured optimum.
- Query: the full accepted current message, up to 8,000 UTF-8 bytes. No stored
  history is concatenated or sent for embeddings.
- Lookup: propose a **2s async optional-reference budget**, running independently
  of the existing 200ms memory selection. On deadline/index/provider/configuration
  failure, continue without technique context and return an unavailable report.
- Generation: retain one reply call and no automatic retries. Verify the combined
  route fits the 15s browser budget with margin; adjust only on measured evidence.
- Bound concurrent embedding workers (initially propose two per localhost process).
  A worker slot remains occupied until its actual request exits, even when the
  async caller has fallen back. Do not queue unbounded abandoned calls or cache
  personal query text for convenience.

Model input tokens, real time-to-response, concurrent summary activity and API
usage remain measurement items. Existing summaries can run independently and
share provider/account resources; "not awaited" does not prove zero latency impact.
Disabling the feature or rolling back the index path must immediately restore
the previous typed path for new requests. Existing index publication refuses
overwrite, making a path switch reversible.

### Voice boundary

Keep voice unchanged in typed v1: existing memory startup snapshot, no new tools,
events, microphone behavior or session restart. A snapshot of selected technique
cards would be fixed for that session and may not cover later topics. It must
not be presented as ongoing lookup.

For a later spoken-retrieval increment, compare a server-owned sideband/function
continuation path with client delegation. Both need task identity, cancellation,
bounded tool results and permission checks. Current `tools:[]`/`tool_choice:none`
and browser event allowlists do not implement that path. Official documentation
supports application-executed custom tools and server-side context updates, but
those capabilities require actual application integration and verification:
[Live delegation and tools](https://developers.openai.com/api/docs/guides/live-delegation).
No automatic microphone restart or streaming-caption-triggered paid calls.

## Ordered implementation checkpoints

| Checkpoint | Concrete work | Completion evidence |
| --- | --- | --- |
| 1. Composition and regression repair | Neutral shared JSON/scope/error contracts; injected memory/summary/context services; resolve relative imports in boundary tests; pre-generation disconnect guards. | Existing request/response and summary behavior unchanged; no sibling imports; queued disconnect before generation makes zero new provider calls. |
| 2. Retrieval interface alignment | Separate lookup permission from deliberate-reframe consent; support full accepted message size; structured personal/technique bundles; async deadline and bounded workers. | Off/missing index sends zero embeddings; multilingual 8KB input works; timed-out/abandoned lookup cannot start generation or publish late references. |
| 3. Typed integration behind the disabled flag | Compose labeled input; update reviewed prompt scope; return optional report; add a minimal unavailable status; preserve memory/summary and save behavior. Use injected mocked retrieval while real vectors are absent. | Correct personal permissions with technique on/off; memory unchanged when technique fails; no prompts/model fields accepted from browser; no extra calls on save Retry. |
| 4. Combined mocked evaluation | Exercise all fifteen scenarios plus cross-case invariants, interruption and simultaneous summary activity. | Expected/observed records; source isolation, draft/late-result handling, End/Emergency and source/procedure eligibility checked. Generated consent/refusal behavior remains a later live-model check. |
| 5. Real index and relevance evaluation | Choose an explicit model/dimension, generate 76 document vectors, evaluate fictional paraphrases and no-match cases, select threshold and publish immutable index before activation. | Version/hash/model/dimension checks pass; observed acceptable-family rankings, misses and threshold rationale recorded. Requires separately authorized API usage. |
| 6. Small live fictional sample | Observe ranking plus a separately bounded generated-reply selection after authorization; record variation and time-to-response. | No claim of generated behavior from mocks; no microphone; distinguish embedding calls, reply calls and cached-summary calls. |
| 7. Optional spoken retrieval | Separate transport/contract proposal and explicit scope choice. | Startup snapshot limitations or dynamic continuation/cancellation demonstrated without silently expanding browser permissions. |

The initial embedding candidate remains `text-embedding-3-small`, 1536 dimensions,
subject to account access and observed task fit; the existing adapter supplies no
default. An initial budget can be six embedding HTTP requests: five corpus batches
and one batch for fifteen short fictional query inputs. Validate batch byte bounds
first. No automatic retries, real-user text, live microphone or reply-generation
calls are included in that budget. Further iterations/reply samples need their
own explicit bounded allowance. No paid work was performed for this plan.

## Neutral assessment and decision

| Dimension | Assessment |
| --- | --- |
| Architectural coherence | Good separate stores; revise composition ownership. |
| Simplicity | Good if typed pre-retrieval stays small; avoid an extra intent model/framework. |
| Operational realism | Conditional on explicit timing, cancellation and usage limits. |
| Scalability | Exact scoring fits the current small catalogue; measure before adding infrastructure. |
| Maintainability | Improve sibling boundaries and structured context before expansion. |
| Migration safety | Additive optional reports, unchanged memory semantics, default-off feature and immutable index versions. |
| Team ergonomics | Separate module ownership with a short, explicit list of shared integration edits. |
| Observability | Transient status/reference IDs and fictional validation evidence; no personal-query logs. |
| Testability | Strong mocked baseline; semantic and generated behavior remain unverified. |
| Adaptability | Separate provider/index interfaces; voice can evolve without changing personal storage. |

The reliability and feature-ownership critiques identify the most concrete
issues. A scalability-driven demand for a dedicated vector server is premature.
The original plan under-specified conversational permission, combined latency,
source-data placement and the already evolving summary path; the checkpoints
above address those gaps.

**Verdict: revise, then proceed with checkpoint 1.** The approach is sound when
source separation, fallback and user control remain explicit. It would fail if
retrieval becomes implicit permission, historical interpretations become facts,
or an optional lookup delays/cancels otherwise usable chat.

Top three changes: (1) repair composition/import/cancellation boundaries;
(2) separate lookup, source data and conversational permission; (3) calibrate real
retrieval and its latency/usage budget before enabling it.

Reversible decisions: feature flag, threshold, card eligibility, model/index path
and typed-only rollout. External transmission and incurred API usage cannot be
undone; do not perform them as part of an unapproved build or evaluation.

## Scope and remaining decisions

This request authorizes review and planning. This document does not fix the
findings or activate the library. Full books stay outside Git; original card
summaries/examples retain source references. No dependency, schema or endpoint
expansion is needed merely to approve the plan.

TODO before activation: confirm hosted embedding usage/transmission and budget;
observe model access/relevance; select threshold; finalize exact typed context
placement and optional status schema; record cancellation/latency observations.
Keep strict semantic consent interaction and dynamic voice retrieval as explicit
scope decisions rather than imply that the current boolean/no-tools setup solves
them. The next deliverable is the small composition/guard refactor and its
regressions, followed by mocked typed integration; paid evaluation is a separate step.
