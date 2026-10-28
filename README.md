# Mental Health Skills Application

IST 402 Assignment 3: a localhost coursework prototype exploring short, user-controlled mental health skills experiences informed by the supplied R1–R4 and D1–D6 study findings. The source of truth is [the assignment](docs/assignment-description.md). Test only with fictional scenarios; this prototype must not be offered as a mental health support tool or claim to provide therapy, diagnosis, or monitoring.

Repository: [mental-health-app](https://github.com/jclee2044/mental-health-app.git), configured locally as `origin`.

## Emotion graph update — October 28, 2026

Emotion log now opens directly with pleasantness × energy, replacing the feeling
cards and separate graph step. Tap or drag to place the dot; movement follows with
a short 90ms transition (instant with reduced motion). No selection summary is
shown. Color remains required; notes are optional. Sliders and keyboard controls
remain available. Existing feeling labels are preserved in history; new entries
save without a category. See the [current design revision](docs/design-notes.md#october-28-2026--graph-first-emotion-log-revision)
and [JSON contract](backend/app/features/emotion/CONTRACT.md).
Restart an already-running backend to load the optional feeling contract.

## inspire visual theme — October 28, 2026

The application is now branded **inspire**, with a soft cream/lavender theme, minimal sage/peach accents, filled
waves and a thinner lilac/violet lowercase wordmark across its existing screens. Routes,
Emergency access and feature behavior remain unchanged. Existing appearance
preferences and personal emotion colors are preserved; new preferences default
to Violet. See [theme implementation and verification](docs/inspire-theme.md).
Earlier names and appearance descriptions below are historical where superseded.

## Chat history update — October 27, 2026

Saved chats now includes typed and spoken conversation text in the same history.
Spoken text saves when voice ends or you leave chat; no audio recordings are
saved. Both modes display as ordinary chat messages. New is at the top right of
history. Review does not resend history to a model. Spoken text can be approximate;
pending/in-progress text may be lost on reload/close. Earlier unsaved voice chats
cannot be recovered. The older notes below are historical where superseded.
See [persistence contract](backend/app/features/voice/PERSISTENCE.md).

## Part 3.2 submission increment — October 26, 2026

Guided breathing is the submission focus. Completed typed exchanges now save
as atomic user/assistant pairs in SQLite, separately from model generation.
Support chat → View saved typed chats provides read-only review and confirmed
deletion. Old chats are never automatically sent to the model. Voice captions
remain transient. Save status/Retry survives navigation in the loaded app;
unsaved queues are lost on reload/close. Typed records remain until deleted.
No dependency was added. Earlier implementation notes below are historical where
this section supersedes them.

Use the build/run commands below for the normal app at port 8000, using ignored
`backend/data/still.sqlite3`. New chat tables initialize when the updated backend
starts. Model requests require server-only `OPENAI_API_KEY` and
`VOICE_BACKEND_MODEL`; SQLite does not establish provider privacy/retention.

For a no-cost rehearsal, build then run
`backend/.venv/bin/python scripts/serve_submission_demo.py` and open
`http://127.0.0.1:8001/`. This uses **mocked text**, no provider calls, no supported
voice, and separate ignored `backend/data/submission-demo.sqlite3`. Send
`demo:fail` to rehearse a reply error. It is not live-model evidence.
`backend/.venv/bin/python scripts/inspect_submission_db.py` inspects the normal
database read-only; add `--demo` for the rehearsal file and `--messages` only for
fictional text you intend to show.

Follow [browser and SQLite validation](docs/part32-validation.md). Observed
results: [Part 3.2 verification](docs/part32-verification.md). The submission draft
is [submissions/part3.2/report.md](submissions/part3.2/report.md); root `report.md`
remains Part 3.1. Before uploading, supply actual live-model evidence, recording
links and a reviewed/pushed submission commit. No live call is claimed by the
mocked tests or rehearsal. [Typed persistence contract](backend/app/features/voice/PERSISTENCE.md).

## Current implementation — October 21, 2026

The first iteration now implements the responsive interface, emotion log/calendar/edit/delete, SQLite persistence, and guided breathing with synchronized circle motion and locally bundled CC0 human inhale/exhale recordings identified by the user. Support chat is an honest frontend stub. Emergency replaces Help throughout the current interface. About retains the assignment-required role description. The Part 3.1 notes below are historical design/scaffold evidence.

The code is split for three independently buildable commits: **interface → emotion log → guided breathing**. See [checkpoint instructions](docs/implementation-checkpoints.md), the [exact file scopes](scripts/checkpoints.json), and [layer boundaries](docs/architecture.md). The shell imports no feature directly; frontend/backend feature folders register themselves. Breathing history is independent of emotion history. No dependency declarations were added/removed/upgraded; the existing project environments are reused.

From the repository root, build and serve the full production PWA on localhost
with the chat credentials/model in the private root `.env`:

```sh
npm --prefix frontend run build
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --env-file .env --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/`. The offline shell becomes available after a successful initial load/activation; About reports readiness. Native installation uses the target browser's install/Add to Home Screen controls, whose availability varies by browser. Native install/standalone relaunch on a real phone has not been verified. Cached assets contain no personal API responses. Offline breathing and Emergency work; saving/history require the local server. A phone's own localhost is a different host from this computer; no LAN/public deployment is configured.

If no `.env` exists and you only want the offline activities, omit `--env-file
.env`. Chat requires both `OPENAI_API_KEY` and `VOICE_BACKEND_MODEL` in the server
environment. The full chat-enabled command is:

```sh
backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --env-file .env --host 127.0.0.1 --port 8000
```

The application reads process environment at startup; the launch command without
`--env-file` does not load `.env` automatically. The existing project environment
already includes Uvicorn's dotenv support; no dependency was added. Keep `.env`
private and ignored. Restart after changing it; `GET /api/voice/config` should
report `configured` when both required values are present/valid. This check does
not contact the provider or verify provider access. If a port is occupied, leave
unrelated processes alone; use a free port (or `--port 0` and the URL Uvicorn
prints). Production frontend requests use that same origin.

For development, run the same backend command in one terminal and `npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173 --strictPort` in another. Vite proxies `/api` to port 8000. It is tooling, not middleware. Service workers register only in production builds. Stop only the terminal processes you started. A feature-free interface checkpoint can use `npm --prefix frontend run preview -- --host 127.0.0.1` without the backend.

Verification:

```sh
npm --prefix frontend test
backend/.venv/bin/python -m pytest -c backend/pytest.ini backend/tests backend/app/features
backend/.venv/bin/python scripts/verify_checkpoints.py
backend/.venv/bin/python scripts/stage_checkpoint.py interface
```

For non-mutating lint, run `npm exec --offline -- oxlint .` and `npm exec --offline -- eslint . --no-cache` from `frontend/`.

The last command previews the stage scope; it does not stage or commit. Add `--stage` only when ready to stage that checkpoint. Commit interface first, then emotion, then breathing; the helper never commits. Root documentation had prior changes and remains outside these staging scopes for separate review. Existing `frontend/package-lock.json` and backend requirements remain unchanged; normal clean-checkout installation instructions below still apply.

Contracts: [API index](docs/api-contract.md), [emotion](backend/app/features/emotion/CONTRACT.md), [breathing](backend/app/features/breathing/CONTRACT.md). SQLite lives in ignored `backend/data/still.sqlite3`, initialized at startup with no seeded records. Entries can be deleted in the app. Session retention/deletion controls remain TODOs; deletion does not promise erasure from backups. Failed session saves remain retryable in memory and are lost on reload/close. No authentication, model provider, passive sensing, or external API is implemented. Do not send real personal data. Chat/model contribution and conversation persistence still do not meet those Part 3.2 requirements.

Observed checks and their limits are recorded in [iteration verification](docs/iteration-verification.md) and [the evidence log](docs/evidence-log.md). Healthy browser runs measured 63.0s for countdown plus six cycles, with 63.1s and 64.0s instruction-to-finish examples excluding pauses. Speaker quality, native installation, clean dependency installation on another machine, and live-model behavior remain unverified. The three code checkpoints were subsequently committed at the user’s request: `415310c` (interface), `b003173` (emotion), and `f9f7782` (breathing). They have not been pushed. Broader documentation/evidence edits remain unstaged.

## Chat communication policy — October 26, 2026

The [readable system prompt](docs/chat-system-prompt.md) reflects the user's chosen
middle between listening and offering help. Explaining/venting favors short
echoes, fuller reflections or selective summaries using the user's own words;
genuine questions invite relevant answers and tentative practical options.
Both server-owned prompt layers preserve consent, safety, age-sensitive wording
and user control. The typed-channel hint follows the same policy. No RAG is
connected; reviewed technique material is a future separate increment. Runtime
source is `backend/app/features/voice/prompts.py`; restart the backend and start
a fresh session to load changed instructions. No running process was restarted
or live model/microphone behavior verified by this prompt task.

## Chat voice/text increment — October 26, 2026

The latest refinement keeps spoken and typed messages in one visible conversation.
Each speaker's captions form bubbles using timeline gaps/speaker changes, with
late fragments placed back in the right group. Sending text stops capture and
shares recent text/captions with Responses; selecting the microphone again creates
a fresh Live session carrying the same bounded current-chat context. Bubbles stay
visible until leaving chat. Context is at most 16 messages / 6,000 UTF-8 bytes;
caption/turn boundaries remain approximate. This supersedes the separate-context
and clear-captions-on-Start behavior described in the earlier increment below.

Chat now has a self-registering frontend with text bubbles and opt-in native WebRTC voice. Only selecting Start voice checks configuration/requests the microphone; Active waits for `session.started`. Permission, connecting, active, muted, closing, closed and error states, blocked-playback recovery, cancel/stop and resource cleanup are checked with mocks. The user additionally authorized `POST /api/chat/messages` for typing without microphone/WebRTC. Set backend `OPENAI_API_KEY` and `VOICE_BACKEND_MODEL`; no model/key/settings are accepted from the browser. See [chat behavior and limits](frontend/src/features/chat/README.md) and [HTTP contracts](backend/app/features/voice/CONTRACT.md).

No audio, transcript or typed-message persistence is added. Sending text ends voice and uses recent typed context only; voice starts a separate provider session. Emergency remains independent and opening a panel stops voice without automatic resume. The 300-second client timer ends voice only, not chat, and is not a provider billing guarantee. Tests use fake media/peer/audio/HTTP and mocked Vue rendering; no real microphone, paid call, or device/browser compatibility result is claimed. Existing checkpoints are unchanged and omit these new modules; full-checkout tests/build cover chat separately. No dependencies were installed.

The lifecycle refinement makes Mute/Unmute local microphone toggles: assistant playback, the provider session and billing continue. End stops capture immediately, sends session.close once and waits at most 2s before transport cleanup. Unmount/navigation/page exit, Emergency and the duration limit also clean up. Late creation IDs use the server-owned `POST /api/voice/sessions/{session_id}/end` fallback without restoring stale UI. Its WebRTC hangup applicability remains an explicit unverified assumption; see the contract. Duplicate Start/repeated End are guarded, and each new voice session starts with empty input and clears previous captions. Backend close tracking holds only IDs/outcomes in process memory, never audio/transcripts or SQLite.

The [voice verification and manual checklist](docs/voice-verification.md) records the subsequent 134 backend / 41 focused frontend mock passes and production build, model/prompt locations, and a planned single live conversation ending by 45s with microphone release checked by 55s. The live procedure has not been run; no paid call or real microphone check is claimed.

## Backend voice increment — October 22, 2026 (historical)

`GET /api/voice/config` and `POST /api/voice/sessions` now provide server-owned GPT-Live (`gpt-live-1`) negotiation. Set both `OPENAI_API_KEY` and `VOICE_BACKEND_MODEL` in the backend process environment before startup; either missing/invalid value reports `unconfigured`. No delegated model is chosen automatically. Config checks do not contact the provider. The browser can send only a bounded SDP offer; no owners/profiles exist. See the [voice contract](backend/app/features/voice/CONTRACT.md) for payloads, errors, permissions and the focused mocked-test command. The two [server prompts](backend/app/features/voice/prompts.py) separately control Live speech and delegated Responses reasoning, which has no tools. No audio/transcript persistence is implemented.

This is backend-only: the existing text-chat placeholder/frontend is unchanged. No dependencies or paid calls were added during implementation. The reported 300-second voice duration is a policy for future client handling, not an enforced provider expiry or a forced text-chat exit. `store: false` controls session retrieval, not general provider retention. Voice cleanup, conversation persistence and browser/live evaluation remain TODOs. Existing interface/emotion/breathing checkpoint scopes are unchanged.

## Part 3.1 research and design (historical)

Current milestone: Research and Design, due October 15, 2026 at 11:59 PM Eastern. The imagined audience includes people experiencing anxiety or intrusive thoughts who face cost or apprehension barriers to therapy. This motivation informs the design; actual use remains fictional coursework testing.

The proposed phone interface opens with a brief, skippable logo screen and three wide buttons stacked vertically: Emotion log, Guided breathing, and Support chat. Help remains available throughout. Logging requires a feeling selection, personal color, and point on a separate pleasantness/energy graph, with optional text and a calendar for reviewing entries. Breathing uses six four-in/six-out cycles after a 3–2–1 countdown, with pause/end controls. Chat is open-ended, with visible End chat and a reply-settings control; no forced conversation timeout.

Optional appearance preferences cover accent color, text size, and reduced motion. Adaptive UI remains an open question. Eye tracking, passive emotion inference, voice, and additional breathing patterns are deferred. The selected supplied skill is paced breathing; the user's proposed Sleight of Mouth influence on chat needs further content/evidence review and is distinct from CBT.

| Deliverable | Location and status |
| --- | --- |
| Part 1 report | [report.md](report.md); tracked submission file with direct GitHub documentation/image links |
| Low-fidelity wireframes | [Early mockup](docs/early-mockup.png), created with ChatGPT image generation; static review board |
| Design decisions and flow | [Design notes](docs/design-notes.md); research traceability, timing budget, data proposal, model boundaries, tradeoffs, and TODOs |
| Additional research | [Research notes](docs/research-notes.md); studies, official resources, design implications, and evidence limits |
| Agent rules | [AGENTS.md](AGENTS.md); durable project rules and current design boundaries |
| AI use and evidence | [AI-USE.md](AI-USE.md) and [evidence log](docs/evidence-log.md) |
| Current handoff | [handoffs/current.md](handoffs/current.md); current scope, writing preferences, image review, and next work |
| Design evidence and submission | Mockup and repository linked; the report records the reviewed content commit |

The user used ChatGPT's image generation tool to create the low-fidelity wireframes. The supplied review board has been visually inspected and linked in the report. Its Help panel still shows a pending-number placeholder; the confirmed design uses separate U.S. crisis-counseling and emergency-services options. Static images do not demonstrate working navigation or animation. At the Part 3.1 checkpoint, no project-specific UI, backend, model, SQLite persistence, or API integration had been implemented. Existing setup evidence below records those earlier scaffold checks; current implementation evidence is linked above.

## Architecture

- `backend/`: Python domain logic, independent of frameworks, with FastAPI as the JSON API boundary. SQLite persists emotion entries and skill sessions using Python's standard library. Conversation storage remains unfinished. Shared middleware handles HTTP policy only; feature folders own domain, routes and storage.
- `frontend/`: Vue presentation, with backend-request code kept separate from components. Node.js and npm provide development tooling and builds, not a separate application server.
- `docs/`: project requirements and design/verification notes.
- `prompts/`: the ordered setup instructions used to prepare this scaffold.
- `handoffs/`: current project handoff and continuation notes.

Backend and frontend dependencies are project-owned: `backend/.venv` and `frontend/node_modules`. Do not install project dependencies globally. Future Vue–FastAPI communication must use a documented JSON contract covering payloads, responses, and errors before integration.

## Setup and verification

Initial setup followed [the setup prompts](prompts/setup-prompts.md) in order. That phase is complete; current feature startup and verification commands are above.

### Backend

Use Python 3.10 or newer. This machine's environment was created with `/opt/homebrew/bin/python3.12` (Python 3.12.13), the newest available compatible patch release. The default `python3` is also compatible (3.12.10), but the system `/usr/bin/python3` (3.9.6) is too old.

Run from the repository root, substituting the path to your compatible Python when needed:

```sh
/opt/homebrew/bin/python3.12 -m venv backend/.venv
backend/.venv/bin/python -m pip install --no-cache-dir -r backend/requirements.txt
backend/.venv/bin/python -c 'import sys, pathlib, fastapi, pytest; assert pathlib.Path(sys.prefix) == pathlib.Path("backend/.venv").resolve(); assert sys.prefix != sys.base_prefix; print(sys.executable, fastapi.__version__, pytest.__version__)'
backend/.venv/bin/python -m pip check
```

The only direct dependencies are `fastapi[standard]` (API tooling and development server) and `pytest` (future backend verification); their transitive dependencies are installed automatically. Verified: FastAPI 0.143.0 and pytest 9.1.1 import from the project environment. The prompt requires unpinned declarations, so this reproduces the setup procedure rather than guaranteeing identical future Python package versions. No Python lockfile was added.

The implemented FastAPI application is `backend/app/main.py`; startup and test commands are provided in the current implementation section.

### Frontend

Verified computer-level tooling: Node.js v26.6.0 at `/opt/homebrew/bin/node` and npm 11.18.0 at `/opt/homebrew/bin/npm`. Node.js satisfies the current [official Vue Quick Start](https://vuejs.org/guide/quick-start.html) requirement `^22.18.0 || >=24.12.0` (checked October 8, 2026). No machine-level installation is needed.

The official `create-vue` v3.24.0 generator created a bare JavaScript starter in the existing `frontend/` directory, with ESLint and its bundled Oxlint (approved). Router, Pinia, TypeScript, JSX, testing frameworks, formatters, and experimental features were omitted. The generator also includes its standard Vue DevTools Vite plugin. Vue is the runtime dependency; Vite, its Vue plugins, ESLint/Oxlint integrations, parser, globals, and the lint script runner are development dependencies. They support the requested Vue development/build and lint workflow.

For a clean checkout, run from the repository root:

```sh
cd frontend
npm_config_cache="$PWD/../.npm-cache" npm ci
npm run lint
npm run build
npm run dev -- --host 127.0.0.1
```

`npm ci` restores the retained `frontend/package-lock.json` without changing dependency declarations. The generator's `npm run lint` automatically fixes code and writes an ignored ESLint cache. To verify without changing source or writing that cache, use:

```sh
npm exec --offline -- oxlint .
npm exec --offline -- eslint . --no-cache
npm run build
npm ls --depth=0
```

The build writes ignored `frontend/dist/`. At scaffold time the development server served the starter without a backend. The implemented version now uses the documented API proxy. Stop it with Ctrl-C in the terminal that started it. A production build can be served locally with `npm run preview -- --host 127.0.0.1`. Browser rendering and interactive behavior have not been checked; scaffold verification covers imports, dependency consistency, lint, and compilation.

## Setup evidence (October 8, 2026)

Steps 1–8 of the setup guide are complete. The user approved the current generator's bundled Oxlint on October 8, 2026. Step 9 was subsequently completed with user authorization on October 15; see the Git checkpoint below.

### Read-only preflight and tool checkpoints

The preflight was run after creating only `README.md`, `AGENTS.md`, and `.gitignore`; `backend/`, `frontend/`, `docs/`, `prompts/`, and `handoffs/` already existed. The preflight itself changed no files or environments.

| Check | Preflight status | Evidence |
| --- | --- | --- |
| Operating system | Passed | macOS 26.6.2, Darwin 25.6.0, arm64 |
| Python >=3.10 available | Passed | Python 3.12.10 and 3.12.13 available; system 3.9.6 is incompatible |
| Backend environment | Missing | No `backend/.venv` existed at preflight; created in step 5 |
| FastAPI/pytest manifest | Missing | No backend manifest existed at preflight; created in step 5 |
| Node.js/npm | Passed | Default Node.js v26.6.0 and npm 11.18.0 meet Vue's requirement |
| Frontend manifest/lock/dependencies | Missing | `frontend/` was empty |
| Git installation | Passed | `/usr/bin/git`, version 2.50.1 (Apple Git-155) |
| Git repository/status | Not applicable | No enclosing repository; status/history not available |
| Inventory | Passed | Existing assignment, setup prompts, and empty backend/frontend/handoff directories reviewed |

Available Python executables on PATH were enumerated, resolved, and checked individually:

| Path | Version | Installation |
| --- | --- | --- |
| `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3` | 3.12.10 | python.org framework (alias) |
| `/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12` | 3.12.10 | python.org framework |
| `/usr/local/bin/python3` | 3.12.10 | Same framework (alias) |
| `/usr/local/bin/python3.12` | 3.12.10 | Same framework (alias) |
| `/opt/homebrew/bin/python3.12` | 3.12.13 | Homebrew framework; selected for the venv |
| `/usr/bin/python3` | 3.9.6 | System interpreter; not used |

Additional PATH alternatives: `/usr/local/bin/node` v24.21.0 and `/usr/local/bin/npm` 11.19.0. The default tools were retained. These are computer-level tools, not project-owned dependencies. A fallback Git executable also appears on PATH under the Codex runtime; `/usr/bin/git` was used.

Read-only commands used: `pwd`, `ls -la`, `rg --files` (including hidden files and targeted patterns), `find docs -maxdepth 2 -type f -print`, `cat prompts/setup-prompts.md`, `cat docs/assignment-description.md`, ancestor `AGENTS.md` checks, `cat AGENTS.md README.md`, `uname -a`, `sw_vers`, `whence -a`/`whence -pa` for Python/Node/npm/Git, individual executable `--version` calls, `command -v node npm`, `git rev-parse --show-toplevel`, `git rev-parse --is-inside-work-tree`, and `git config --get user.name`, `git config --get user.email`, `git config --get-regexp '^user\.(name|email)$'`. Python inline inspection enumerated executable names on PATH and checked whether the environment, manifests, lockfile, and dependency directory existed. Git identity was unset at that preflight checkpoint; the user later supplied project-local identity for the approved initial commit. No global configuration was changed.

### Backend installation and verification

- Created `backend/.venv/` and `backend/requirements.txt`; updated this README with the setup commands above.
- Ran the documented venv creation and pip installation. The first sandboxed download failed because PyPI DNS was inaccessible; the same project-only install succeeded with approved network access. No global packages or machine-level tools were installed.
- Ran the documented import/prefix assertion, `backend/.venv/bin/python -m pip check`, `backend/.venv/bin/python -m pip show fastapi pytest`, and `backend/.venv/bin/python -m pip --disable-pip-version-check --no-cache-dir list --format=json`.
- Passed: `sys.prefix` equals the project `backend/.venv`; `sys.prefix` differs from `sys.base_prefix`; both modules import; package locations are inside the venv; pip reports no broken requirements. Only the two declared dependencies and their resolved transitive dependencies were installed.
- No backend functions, API routes, or tests were created. Backend behavior is not yet testable.

### Frontend generator inspection

Read the official Vue Quick Start and [create-vue source/usage](https://github.com/vuejs/create-vue). Ran `npm_config_cache="$PWD/.npm-cache" npm create --yes vue@latest -- --help` with approved network access; its help confirms Oxlint is always included with ESLint. Ran the same command with `--version`, and read the cached generator's package version using `node -p` (v3.24.0). The npm generator cache is project-owned and ignored. No global npm packages were installed.

### Frontend installation and verification

Ran, in order:

```sh
# From the repository root; frontend was confirmed empty first:
npm_config_cache="$PWD/.npm-cache" npm create --yes vue@latest -- frontend --eslint --bare
# From frontend/:
npm_config_cache="$PWD/../.npm-cache" npm install
npm run lint
npm run build
npm ls --depth=0
```

- Installation succeeded: 222 packages added; npm audited 223 packages and reported zero vulnerabilities at setup time. The generated lockfile is retained. No extra dependencies were manually added.
- Lint passed for both Oxlint and ESLint. The Vite production build passed, transforming 11 modules.
- Inspected the generated manifest, Vite configuration, lint configuration, starter components, and other starter files. The frontend has no project-specific interface or API requests.
- A read-only inline Node check compared manifest dependency declarations to the lockfile root, compared every installed package version with its lockfile entry, allowed absent optional platform packages, and validated the full dependency tree using `npm ls --all --json`.
- Added ignored cache/build patterns to the root `.gitignore`; no application source was manually changed.

Files/directories created: root `README.md`, `AGENTS.md`, `.gitignore`, and ignored `.npm-cache/`; `backend/requirements.txt` and ignored `backend/.venv/`; generated frontend `README.md`, `package.json`, `package-lock.json`, `index.html`, `jsconfig.json`, `vite.config.js`, `eslint.config.js`, `.oxlintrc.json`, `.editorconfig`, `.gitattributes`, `.gitignore`, `src/App.vue`, `src/main.js`, `public/favicon.ico`, `.vscode/extensions.json`, `.vscode/settings.json`, and ignored `node_modules/`, `.eslintcache`, and `dist/`. Existing assignment and setup prompt files were not modified. The README and root ignore file were updated during successive setup phases.

### Complete scaffold verification (step 8)

| Check | Result | Evidence |
| --- | --- | --- |
| Required project directories and root files | Passed | All present |
| README architecture, setup, verification, development, TODOs | Passed | Reviewed against assignment and verified commands; backend startup deferred because no module exists |
| AGENTS project, separation, permission, reporting rules | Passed | All required rules present |
| Backend interpreter ownership | Passed | `sys.executable` and `sys.prefix` belong to `backend/.venv` |
| Exact requested backend dependencies | Passed | Manifest contains only `fastapi[standard]` and `pytest` |
| Backend imports and dependency consistency | Passed | FastAPI 0.143.0, pytest 9.1.1, `pip check` succeeds |
| Node/npm versions and paths | Passed | v26.6.0 / 11.18.0, both under `/opt/homebrew/bin` |
| Current Vue Node requirement | Passed | v26.6.0 satisfies `^22.18.0 || >=24.12.0` |
| Vue and ESLint declarations | Passed | Vue 3.5.43 and ESLint 10.12.0 installed with generated lint tooling |
| Frontend lockfile and installed tree | Passed | Lockfile v3; all 222 installed versions match; 43 optional platform packages absent as expected; full `npm ls` succeeds |
| Frontend lint | Passed | Oxlint and ESLint pass, including verification without fixes or cache writes |
| Frontend production build | Passed | Vite 8.3.4 builds successfully |
| Ignore coverage and preserved manifests/lockfile | Passed | Generated environments, dependencies, builds, caches, secrets, editors and OS artifacts ignored; declarations and lockfile visible in inventory |
| No project-specific application implementation | Passed | Backend has only its manifest; frontend has only the two generated starter source files; no API calls or custom interface |
| Backend behavior/browser interaction | Not applicable | No backend application; browser interaction outside scaffold checks and not verified |

Step 8 changed no source files, dependency declarations, or installed dependencies. Verification used the documented non-mutating lint commands, `npm run build`, `npm ls --depth=0`, `backend/.venv/bin/python -m pip --no-cache-dir check`, Node/npm version/path checks, `cat AGENTS.md`, source inspection with `cat`/`rg`, and an inline project Python assertion script checking structure, interpreter ownership, exact declarations, omitted optional features, ignore patterns, and the absence of backend application files. The build regenerated only ignored output. After verification, this README was updated with the results.

### Initial Git checkpoint (step 9)

At the original setup checkpoint, no enclosing repository existed and author identity and commit approval were pending. The user subsequently supplied identity and authorized initialization and publication on October 15, 2026, as recorded in [the evidence log](docs/evidence-log.md).

Read-only inspection on October 21 confirms initial commit `d52a680` (`chore: initialize coursework scaffold and design documentation`), content commit `084981b`, and report-reference commit `010a9d9`. `origin` matches the repository above and `report.md` is tracked. Generated environments, dependencies, builds, caches, and secrets remain excluded. Remote availability and instructor access were not rechecked in this inspection.

## Open decisions

- TODO: refine feeling-slider labels and the burden of required feeling/color/graph inputs; reconcile the mockup's Help placeholder with the confirmed resource design when refining the interface.
- TODO: resolve adaptive UI, approved reply-setting values, age scope, crisis-input policy, and the proposed fourteen-pattern chat influence. No automatic sensing or contraction is approved.
- TODO: select model provider, reviewed retrieval corpus and rights, context permissions, privacy disclosure, embedding location, retention, and deletion semantics. Local SQLite does not establish fully local model processing.
- Entry and session schemas/contracts are implemented under `backend/app/features/`. TODO: define conversation/context/retention details before model integration.
- Independent Emergency, failures/exits, fixed breathing and entry/session history are implemented and checked. TODO: complete conversation history/model behavior and broader accessibility testing.
- TODO: measure guided exercise duration (no more than 90 seconds at the intended pace), including application delays and stated response assumptions; report entry/setup separately. The current breathing budget is a proposal, not a measured result. No forced chat timeout is planned.
- TODO: create the required fictional evaluation scenarios and repeatable checks; update AI-use disclosure and evidence with actual results as work proceeds.
- The report records the Part 1 content commit and uses file links pinned to it. A follow-up reference commit saves that hash in the report; no commit can contain its own hash. Confirm instructor access before uploading the report.
