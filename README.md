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
| Interface | Responsive cream/lavender design, skippable introduction, independent Home choices, history shortcuts and persistent Emergency access. Appearance offers accent, larger text and reduced motion; it does not dynamically infer distress or adapt the layout. |
| Emotion log | Explicit pleasantness × energy placement by tap/drag, with keyboard and slider alternatives; required personal color and optional notes. One-page Save, calendar/history, edit and delete. New entries have no feeling category; legacy labels are preserved. Color meaning belongs to the user. |
| Guided breathing | Hold the circle through a 3–2–1 countdown and six four-second inhale/six-second exhale cycles. Release early to end and return Home; release after completion keeps the result. Mouse/touch/pen and held Space/Enter are supported in code. Pause/Resume while holding, End, mute, reduced-motion cues, bundled human breath audio, retryable saving and separate session history are included. |
| Typed chat | Model replies using bounded current-chat context, editable drafts retained after failure, End chat, automatic transcript scrolling and leading-space cleanup. Completed exchanges save separately from generation. |
| Voice conversation | Explicit Voice mode selection, WebRTC speech/captions, seven visible lifecycle states, local Mute/Unmute, End, playback recovery and cancellation/cleanup. Switching to text stops voice; explicitly restarting voice carries recent visible context. |
| Dictation | Separate microphone captures up to 30 seconds for OpenAI transcription into the editable draft. Finish/cancel controls, size bounds and typing fallback; no automatic Send or restart. |
| Saved chats | Typed pairs and accepted spoken text share SQLite conversation history, read-only review and confirmed deletion. No audio recordings are saved. Older chats are not automatically reused as model context. |
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
| Server-fixed Live settings | `gpt-live-1`, voice `marin`; browser requests cannot choose models, prompts or tools. |
| Server-fixed dictation model | `gpt-transcribe`; transcription needs the credential, independently of `VOICE_BACKEND_MODEL`. |

`GET /api/voice/config` reports configured/unconfigured and the voice duration
policy; it does not contact the provider or verify model access. It is not a
transcription-readiness check. The coding model disclosed in AI-USE is separate
from the configured application model.

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

Appearance preferences alone use browser local storage (`still.preferences`,
retained across the rebrand). Personal API responses are not cached by the PWA.
Only the built shell is cached; About reports offline readiness. Offline chat,
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
breathing has an implemented guided sequence. No RAG, dataset ingestion, model
training or automatic historical-context retrieval is connected.

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

Latest recorded full verification: **188 backend tests, 101 frontend tests**,
production build, non-mutating lint and all three original cumulative checkpoints
passed. The existing Starlette/httpx deprecation warning remains. These results
precede this documentation update; they were not rerun for it.

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

Still unfinished: dynamic UI/personalization, automatic history reuse, reviewed
retrieval, separate entry/setup timing, broader emotion-flow/accessibility/device
checks, clean-checkout verification and the Part Three fifteen-fictional-scenario /
three-behavior-check evaluation with bounded live variation and recordings.
Guided grounding, STOP and cognitive reframing do not yet have application-owned
steps, exits and timing. The proposed fourteen patterns from Robert Dilts's
*Sleight of Mouth* and Doug O'Brien's *The User's Guide to Sleight of Mouth* remain
subject to source/rights/evidence review, distinct from validated CBT. Eye tracking,
passive emotion inference and additional breathing patterns remain unimplemented
and require scope decisions before development.
