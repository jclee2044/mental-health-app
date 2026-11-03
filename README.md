# inspire

inspire is an IST 402 Assignment 3 coursework app running on localhost with Vue,
FastAPI and SQLite. Home offers three independent choices: Emotion log, Guided
breathing and Support chat. No check-in is required before breathing or chat.
The [assignment](docs/assignment-description.md) supplies the R1–R4 and D1–D6
research findings and requirements. Use fictional scenarios only; this prototype
must not be offered as a mental health support tool or claim therapy, diagnosis
or monitoring.

Repository: [mental-health-app](https://github.com/jclee2044/mental-health-app).

## Current implementation

| Area | Implemented behavior |
| --- | --- |
| Interface | Responsive cream/lavender design, skippable introduction, independent Home choices, activity-specific history shortcuts and persistent Emergency access. Appearance offers eight distinct soft theme colors that tint the app, larger text and reduced motion; it does not dynamically infer distress or adapt the layout. |
| Emotion log | Required personal color appears before explicit pleasantness × energy placement by tap/drag, with keyboard and slider alternatives; optional color meaning and notes. One-page Save, calendar/history, edit and delete. New entries have no feeling category; legacy labels are preserved. Color meaning belongs to the user. |
| Guided breathing | Hold the circle through a 3–2–1 countdown and six four-second inhale/six-second exhale cycles. Release early to show a gentle ending message and Return home button; release after completion keeps the result. Mouse/touch/pen and held Space/Enter are supported in code. Pause/Resume while holding, End, mute, reduced-motion cues, bundled human breath audio, retryable saving and separate session history are included. |
| Typed chat | Model replies using bounded current-chat context, editable drafts retained after failure, End chat, automatic transcript scrolling and leading-space cleanup. Completed exchanges save separately from generation. |
| Voice conversation | Explicit Voice mode selection, WebRTC speech/captions, seven visible lifecycle states, local Mute/Unmute, End, playback recovery and cancellation/cleanup. Switching to text stops voice; explicitly restarting voice carries recent visible context. |
| Dictation | Separate microphone captures up to 30 seconds for OpenAI transcription into the editable draft. Finish/cancel controls, size bounds and typing fallback; no automatic Send or restart. |
| Saved chats | Typed pairs and accepted spoken text share SQLite conversation history, model-generated summary titles with date/time, read-only review and confirmed deletion. Missing titles are generated when History opens using a bounded saved-text excerpt; title failures never block review or storage. No audio recordings are saved. Historical context requires the separate Personal memory opt-ins below. |
| Personal memory | Off by default, with separate permission for recent logs, saved chats and confirmed facts. After an opted-in saved chat ends, a separate model task caches a short summary when substantive. Future context reads that cache or falls back to a literal user excerpt across the seven-day window. No vectors/keyword filter; generation never blocks navigation or runs during voice startup. |
| Failures and offline use | Explicit request/save errors and storage-only Retry. After the production shell is cached, Emergency and breathing remain available without the server; saving/history need the local backend. Pending saves remain in memory and can be lost on reload/close. |

Emergency is application-owned and opens independently of model/classifier or
request success, including overlays and failures. It separates U.S. crisis
counseling from emergency services. Opening the panel does not contact anyone.
Never select real call links during testing; simulate call actions in demos.
Opening overlays, leaving the page or hiding it stops microphone activity with
no automatic restart. During an unfinished held breathing exercise, release,
cancellation, focus/page loss or Emergency ends the exercise through its save path.

The breathing clock and visual/audio loop do not wait for HTTP or SQLite. The
planned sequence is 63 seconds including countdown. Observed timing and usability
limits are listed under verification below; supporting an input in code does not
establish physical-device or assistive-technology usability.

## Requirements and installation

Run commands from the repository root unless stated otherwise. Use an existing
compatible Python and Node installation; project dependencies belong only in
`backend/.venv` and `frontend/node_modules`. Do not install them globally or
rerun the Vue generator on this checkout.

- Python 3.10 or newer; the existing project environment was verified with Python
  3.12.13. Choose a compatible interpreter when creating a new environment.
- Node matching `frontend/package.json`: `^22.18.0 || >=24.12.0`, with npm.
  The recorded environment used Node 26.6.0/npm 11.18.0.
- Direct backend dependencies: `fastapi[standard]` and `pytest`. Their declarations
  are unpinned; there is no Python lockfile, so a fresh install may resolve other
  versions. The frontend lockfile is committed and restored with `npm ci`.

For a new checkout, using `python3` only if it meets the requirement:

```sh
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install --no-cache-dir -r backend/requirements.txt
backend/.venv/bin/python -m pip check
npm_config_cache="$PWD/.npm-cache" npm --prefix frontend ci
```

Do not recreate an existing environment just to run the app. These are setup
instructions, not a claim that a fresh installation on another computer has
been verified. The [historical setup evidence](docs/setup-history.md) records the
original scaffold checks and tool choices.

## Run the application

Build the frontend, then serve it and the JSON API through FastAPI:

```sh
npm --prefix frontend run build
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). Without model configuration,
emotion logging, breathing, SQLite history and Emergency work; provider-backed
chat/voice/dictation report configuration errors. The ignored database
`backend/data/still.sqlite3` and feature tables initialize at startup without
seeded records. A build is required before startup to serve the frontend.

For configured chat, create a private, ignored root `.env` with these server-only
values, substituting your actual credential and chosen accessible backend model:

```dotenv
OPENAI_API_KEY=your-private-key
VOICE_BACKEND_MODEL=your-chosen-backend-model-id
```

Then use this backend command instead:

```sh
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --env-file .env --host 127.0.0.1 --port 8000
```

The command without `--env-file` uses only the process environment; it does not
automatically load `.env`. Restart your own backend after configuration/prompt
changes and start a fresh voice session to load the new policy. Keep credentials
out of Vue, screenshots, evidence and Git. Provider-backed actions can incur API
usage; use the mocked rehearsal below for routine checks.

| Setting | Role |
| --- | --- |
| `OPENAI_API_KEY` | Backend provider credential; required for transcription and model requests. |
| `VOICE_BACKEND_MODEL` | Responses model for typed replies and Live delegation. No default; both this and a valid credential are required for configured chat/voice status. |
| `CHAT_REASONING_EFFORT` | Optional `low` for typed replies only; unset/other values preserve the provider default. The current local Luna configuration uses the separately approved, sampled low setting. |
| Server-fixed Live settings | `gpt-live-1`, voice `marin`; browser requests cannot choose models, prompts or tools. |
| Server-fixed dictation model | `gpt-transcribe`; transcription needs the credential, independently of `VOICE_BACKEND_MODEL`. |

`GET /api/voice/config` reports configured/unconfigured and the voice duration
policy; it does not contact the provider or verify model access. It is not a
transcription-readiness check. The coding model disclosed in AI-USE is separate
from the configured application model.

Typed reframing references are implemented behind the server-only
`REFRAMING_ENABLED` flag (default `0`), independently of personal-memory opt-ins.
The real local index has 76 documents from 19 reviewed cards. Setup and rollback:
[reframing library](backend/app/features/reframing/README.md). Each implementation
checkpoint and observed limitation is recorded in
[reframing evidence](docs/reframing-implementation-evidence.md). The local ignored
`.env` enables the evaluated index and `CHAT_REASONING_EFFORT=low`; restart your
backend to load these settings. Voice receives a compact reviewed catalogue at startup; there is no dynamic
spoken retrieval. Start a fresh chat/session after loading updated backend prompts.

For frontend development, keep the backend on port 8000 and run in a second terminal:

```sh
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Open [http://127.0.0.1:5173/](http://127.0.0.1:5173/). Vite proxies `/api` to
port 8000; it is development tooling, not another middleware server. Service
workers register only in production builds. Rebuild and reload/update the PWA
after source changes when checking the production app.

Stop only processes you started, using Ctrl-C in their terminals. If a port is
occupied, leave other processes alone. Production may use another free port;
the development proxy remains fixed to 8000 unless deliberately changed.
A phone's localhost refers to the phone, not this computer. No LAN/public
hosting or authentication is configured.

## Mocked rehearsal and database inspection

For browser checks without provider calls or credentials:

```sh
npm --prefix frontend run build
backend/.venv/bin/python scripts/serve_submission_demo.py
```

Open [http://127.0.0.1:8001/](http://127.0.0.1:8001/). Use `--port 8013`, for
example, if you need another port. This server replaces the provider, labels
replies as mocks and uses separate ignored `backend/data/submission-demo.sqlite3`.
Send `demo:fail` for a controlled reply error. Voice is unsupported; do not select
Voice mode or dictation in this rehearsal. It does not establish generated-model
behavior, speech quality or provider compatibility.

Inspect an existing database read-only:

```sh
backend/.venv/bin/python scripts/inspect_submission_db.py
backend/.venv/bin/python scripts/inspect_submission_db.py --demo
```

Add `--messages` only for fictional content you intend to display. The inspector
cannot create a missing database and currently summarizes breathing sessions and
**typed** conversation rows; it does not include `chat_voice_messages` in its
counts/output. For unified spoken/typed evidence, inspect that table in DB Browser
or use the app's saved-chat view. See the
[persistence contract](backend/app/features/voice/PERSISTENCE.md) for the schema.

## Data, model boundaries and limitations

SQLite stores emotion entries, completed/ended breathing sessions, conversation
headers, atomic typed pairs and immutable spoken-text batches. Saves use UUIDs
and idempotent storage retries. Failed model requests are not saved as successful
exchanges; retrying a save does not regenerate a reply. Saved chats remain until
local confirmed deletion. Emotion entries also support deletion; breathing-session
deletion and automatic retention/expiry remain unfinished. Deletion makes no
promise about backups or provider records. No authentication or per-user isolation
is provided.

Appearance and app-sound preferences use browser local storage (`still.preferences`,
retained across the rebrand). Personal API responses are not cached by the PWA.
Only the built shell is cached. Offline chat,
transcription and history are not provided. Native phone installation and
standalone relaunch remain unverified.

Recent visible typed/voice text can be supplied to the model across mode switches,
bounded to 16 messages/6,000 UTF-8 bytes. Accepted voice text saves when voice
ends/errors or chat is disposed; it can be approximate, overlapping, partial or
interrupted. Saving is not continuous; browser crashes/reloads may lose pending
text or saves. Dictation audio is held in memory, capped at 2 MiB, and transcribed
into a draft; only a completed sent exchange becomes typed history. The backend
bounds audio size/format, not actual encoded duration.

OpenAI receives relevant text/audio for the chosen provider-backed action.
Local SQLite does not mean fully local processing. `store: false` on Live/text
requests does not establish general retention/no-training guarantees; no such
setting is asserted for transcription. Cancellation cannot guarantee provider-side
cancellation or avoid usage charges.

Voice Mute changes local microphone tracks only: playback, the provider session
and billing continue. End stops capture immediately and waits at most two seconds
for closure acknowledgment before releasing transports. The 300-second active
voice timer ends voice, not open-ended text chat; it is not a billing guarantee.
Server-side fallback hangup for WebRTC, crash reconciliation and provider data
controls remain unverified; see the [voice contract](backend/app/features/voice/CONTRACT.md).

The two [server-owned prompts](docs/chat-system-prompt.md) support active emotional
exploration and practical answers appropriate to the input. Each echo/reflection
requires one relevant question; requests to stop or have no questions take
priority. A model's closing acknowledgment does not itself stop capture or
navigate. The prompts contain the assignment's skill descriptions, but only
breathing has an implemented guided sequence. No curated technique retrieval,
dataset ingestion or model training is connected by the personal-memory increment.
Historical personal context is available only through explicit Personal memory choices.
History separately sends a bounded saved excerpt for missing summary titles.

## Architecture and contracts

- `frontend/src/features/`: emotion, breathing and chat each own presentation,
  styles, endpoint declarations, browser/domain logic and tests. The shell
  discovers `*/index.js`; sibling features do not import each other.
- `frontend/src/api/client.js`: the only browser HTTP transport; feature `api.js`
  files declare endpoints. The breathing loop is independent of requests.
- `backend/app/features/`: feature registration, routes/schemas, framework-free
  domain logic, SQL storage, contracts and tests. The backend `voice` feature
  also owns typed chat, dictation and conversation storage.
- Shared `main.py` composes installed features and serves the built frontend;
  `middleware.py` handles HTTP-wide policy; `database.py` handles connections.
- `docs/`, `handoffs/`, `prompts/` and `scripts/`: requirements, decisions/evidence,
  continuation notes, original setup instructions and checkpoint/demo helpers.

See [architecture](docs/architecture.md) and the [API index](docs/api-contract.md).
The documented JSON contracts include request/response/error shapes:
[emotion](backend/app/features/emotion/CONTRACT.md),
[breathing](backend/app/features/breathing/CONTRACT.md),
[voice and typed generation](backend/app/features/voice/CONTRACT.md),
[dictation](backend/app/features/voice/DICTATION.md) and
[conversation persistence](backend/app/features/voice/PERSISTENCE.md).

## Verification

The approved softened harp plays after a successful emotion save (including an
edit). The original 4.2s warm keys audition plays once when all six breathing
cycles finish. One volume control with an icon and Sound on/off text sits beside Appearance
in the bottom menu across the app and
overlays. It mutes breathing cues, completion/ending sounds and assistant voice
playback. The preference survives navigation and reloads when browser storage is
available; it defaults to on. Microphone mute remains separate; speaker mute
does not end capture, the voice session or billing. Failed saves, early exits and cancelled
actions do not play the harp. Breathing early release/End instead plays the
approved 4.4s descending open tones once, with an ending message and Return home
button. Mute, Emergency/overlays, hidden pages, window blur and navigation cancel
this cue; saving remains independent. Emergency/other overlays, hidden pages, mute and
navigation cancel pending/active completion audio. Audio failure does not block
the visible confirmation or exercise. Both completion cues are bundled for offline
playback; see [source, license and modifications](frontend/src/components/completion-sound/CREDITS.md).

November 2 completion-sound checks: 110 frontend tests, production build,
non-mutating lint and all three original cumulative checkpoints passed. These
include mocked SFC trigger and audio lifecycle checks, not speaker/browser
listening. Vite reports a large bundled-JS warning; the approved WAV is inlined
for offline use. No new dependency was added.

November 2 global-sound update: **113 frontend tests**, production build,
targeted non-mutating ESLint and all three cumulative checkpoints passed. Browser
checks confirmed persisted mute, assistant playback mute, the same icon position
in Emergency/Appearance and the retained early-end screen. No live microphone or
provider check was performed; see [evidence log](docs/evidence-log.md).

Run the existing project checks:

```sh
backend/.venv/bin/python -m pytest -c backend/pytest.ini backend/tests backend/app/features
npm --prefix frontend test
npm --prefix frontend run build
backend/.venv/bin/python scripts/verify_checkpoints.py
```

For non-mutating lint, run from `frontend/`:

```sh
npm exec --offline -- oxlint .
npm exec --offline -- eslint . --no-cache
```

`npm run lint` instead applies fixes and writes an ignored cache. The original
**interface → emotion log → guided breathing** checkpoint manifest remains
unchanged; isolated cumulative checks cover those scopes, while full-checkout
checks also cover chat. `backend/.venv/bin/python scripts/stage_checkpoint.py
interface` only previews; `--stage` modifies the index and never commits. See
[checkpoint instructions](docs/implementation-checkpoints.md).

Latest recorded full verification: **191 backend tests, 104 frontend tests**,
production build, non-mutating lint and all three original cumulative checkpoints
passed. The existing Starlette/httpx deprecation warning remains. These checks were rerun on November 2, 2026 for the appearance/history update.

[Part Two evidence](docs/part32-evidence.md) distinguishes user observations from
mocked checks: the supplied current completion screenshot shows 63.0s sequence /
63.9s instruction-to-finish excluding pauses; a current browser hold-release run
saved an `ended` record with 2.2s active breathing, and mocked reply failure kept
the draft with Emergency still usable. Earlier checks verified persistence after
restart, storage-only Retry and offline Emergency. Entry/setup timing remains
unmeasured separately. No forced exercise timeout is implemented.

These checks do not establish clinical effectiveness, reliable prompt compliance,
real-device microphone/autoplay behavior, transcription quality, full accessibility
or clean installation on another machine. User-supplied voice/SQLite observations
are recorded separately; no live provider/microphone test is claimed by mocks.

## Documentation and remaining work

- [Part Two report](submissions/part3.2/report.md), [curated prompts/screenshots](docs/part32-evidence.md),
  [earlier browser/SQLite results](docs/part32-verification.md) and
  [reproduction guide](docs/part32-validation.md). A recording is not explicitly
  required for Part Two; finished demonstration/process recordings are required
  for Part Three. No recording has been supplied here.
- [Design notes](docs/design-notes.md), [early static wireframes](docs/early-mockup.png),
  [redesign evidence](docs/inspire-theme.md), [emotion graph verification](docs/emotion-graph.md),
  [research notes](docs/research-notes.md) and [chat research](docs/chatbot-communication-research.md).
  Dated design/verification entries describe their own milestones; later source
  and revisions supersede earlier proposals.
- [AI-USE.md](AI-USE.md), [evidence log](docs/evidence-log.md),
  [agent rules](AGENTS.md) and [handoff](handoffs/current.md).
- [Historical Part One report](https://github.com/jclee2044/mental-health-app/blob/3177e4d7dc037a69f3eb7d1c073d466577a822b5/report.md).
  Root `report.md` is untracked/ignored and retained locally where present;
  the Part Two report remains tracked. Relative links render within GitHub;
  a standalone uploaded report needs full published image/document URLs.

Still unfinished: dynamic UI, live evaluation of personal-context retrieval, reviewed
retrieval, separate entry/setup timing, broader emotion-flow/accessibility/device
checks, clean-checkout verification and the Part Three fifteen-fictional-scenario /
three-behavior-check evaluation with bounded live variation and recordings.
Guided grounding, STOP and cognitive reframing do not yet have application-owned
steps, exits and timing. The proposed fourteen patterns from Robert Dilts's
*Sleight of Mouth* and Doug O'Brien's *The User's Guide to Sleight of Mouth* remain
subject to source/rights/evidence review, distinct from validated CBT. Eye tracking,
passive emotion inference and additional breathing patterns remain unimplemented
and require scope decisions before development.

## Personal memory — November 2, 2026

In Support chat, expand **Personal memory** to separately allow recent emotion
logs, saved user-message text and facts you confirm. Choices start off and persist
in SQLite. The compact disclosure contains only transmission/lifecycle information and three
permission toggles. Saved history remains available in each activity. Voice receives
one small startup snapshot; typed replies receive a fresh seven-day snapshot.
The later opted-in post-chat summary task adds a separate model call; lookup does
not. There is no vector database for personal context.
The reframing corpus/cards/vector work stays separate. See the
[personal-memory contract](backend/app/features/personal_memory/CONTRACT.md) for
JSON shapes, limits, provenance, forgetting and integration boundaries.

The log rule uses the latest permitted entry per local date across seven days;
below-center energy means `<0`, not a clinical interpretation. Each saved chat with
user text in the last seven days contributes a compact literal excerpt, without
keyword filtering. Excerpts share a 12,000-byte context budget with logs and up to
six existing confirmed facts. A short notice reports partial chat coverage if the
recent history cannot all fit. A valid cached summary is preferred; otherwise
these are literal excerpts. Generated summaries remain unverified interpretations,
separate from facts the user confirms.
A 200 ms local retrieval deadline falls back to ordinary chat on failure; actual
voice startup/audio latency and generated recall have not been measured.

Opening memory controls stops capture and cancels pending typed work. Changes
apply to future requests; Voice requires an explicit restart. Forgetting a linked
fact also excludes its whole source chat and related facts to prevent immediate
reintroduction. Exclusion keeps the original history record. Independently saved
duplicates are not semantically erased. Changes cannot retract provider context
already sent or remove current-chat messages; End chat starts a fresh conversation.
Selected context is transmitted to OpenAI; local storage is not a retention promise.

Observed checks for this increment: 216 backend tests, 122 frontend tests,
production build, non-mutating Oxlint/ESLint and all three cumulative checkpoints
passed. Browser checks used a separate fictional database and the labeled mock
provider: confirmed fact, context preview, correction/reload and independent
Emergency. No paid call, microphone or live generated-memory check was performed.
Known Starlette/httpx deprecation and bundled-JS size warnings remain.
For an isolated mock rehearsal:

```sh
npm --prefix frontend run build
backend/.venv/bin/python scripts/serve_submission_demo.py --port 8018 --database backend/data/personal-memory-demo.sqlite3
```

This mock accepts context but does not generate a memory-aware response. It cannot
establish voice latency, generated grounding or retrieval safety.

Simulated-memory follow-up: run
`backend/.venv/bin/python scripts/evaluate_personal_memory.py` for isolated
fictional scenarios and local mock timing. [Results](docs/personal-memory-validation.json)
record 24 functional passes and two reproduced search limits; full regression
suites pass 279 backend / 122 frontend tests. Testing fixed a keyword that could
be indexed beyond its transmitted excerpt: search now uses the first 700 UTF-8
bytes. At 2,000 fictional chats, the final run added about 2.4–3.0 ms median local
mock voice-start route time. This excludes live model/network/audio latency.

Latest chat refinement: Enter sends; Shift+Enter adds a newline (IME composition
is preserved). The composer clears immediately; a failed reply restores an
untouched draft without overwriting later typing. New bubbles use short entrance
transitions with OS/app reduced-motion alternatives. Personal memory no longer
shows its fact editor or context-review interface. The user's seven-day request
supersedes the earlier keyword/200-message selection described in historical
verification entries above. No automatic LLM memory-summary task was added.

Current refinement checks: 283 backend tests, 129 frontend tests, production build,
non-mutating lint and all three cumulative checkpoints passed. The updated fictional
evaluator passes 26 scenarios and writes
[seven-day results](docs/personal-memory-seven-day-validation.json). These supersede
its earlier lexical-search expectations, while old raw evidence remains historical.
Cached model-written memory summaries are a possible later increment; current
snapshots use literal user excerpts and disclose when not all recent chats fit.

## Cached memory summaries — latest November 2 update

With **Use saved conversation text** enabled, ending/leaving a saved chat queues a
separate summary request after its initial saves finish. Navigation and the next
chat never wait. The current server model summarizes bounded saved user text;
only substantive results are kept as summary text. SQLite caches the result for
future seven-day context. New source text, deletion, exclusion, consent changes
in flight and expiry prevent stale results from being reused. No automatic backfill
or model retries. Excerpts remain the fallback, and generated summaries never
become user-confirmed facts. See the [contract](backend/app/features/personal_memory/CONTRACT.md).

This task adds API usage and text transmission after an opted-in chat ends. It
has no intentional wait in the chat/voice startup path, but actual provider quota,
network and audio effects are not measured. Summary failures have a small separate
Retry control; Retry chat save remains storage-only. Closing/reloading can lose
unsent requests/notices, and cannot guarantee provider cancellation. The per-message
“Waiting for a reply…” caption is removed; Send retains its pending state.

Observed cached-summary checks: 306 backend tests (including 23 summary cases),
136 frontend tests, production build, non-mutating lint and all three cumulative
checkpoints pass. Browser/SQLite verification used only fictional records and the
fixed mock provider, not actual summary generation or live voice. The separate
[summary contract](backend/app/features/personal_memory/CONTRACT.md) documents API
usage, consent, failure fallback, expiry and delivery/recovery limitations.
