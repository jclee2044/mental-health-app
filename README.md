# Mental Health Skills Application

IST 402 Assignment 3: a localhost coursework prototype exploring short, user-controlled mental health skills experiences informed by the supplied R1–R4 and D1–D6 study findings. The source of truth is [the assignment](docs/assignment-description.md). Test only with fictional scenarios; this prototype must not be offered as a mental health support tool or claim to provide therapy, diagnosis, or monitoring.

Repository: [mental-health-app](https://github.com/jclee2044/mental-health-app.git) (URL supplied by the user; local remote configuration was not changed).

## Chat history update — October 27, 2026

Saved chats now includes typed and spoken conversation text in the same history.
Spoken text saves when voice ends or you leave chat; no audio recordings are
saved. Both modes display as ordinary chat messages. New is at the top right of
history. Review does not resend history to a model. Spoken text can be approximate;
pending/in-progress text may be lost on reload/close. Earlier unsaved voice chats
cannot be recovered. The older notes below are historical where superseded.
See [persistence contract](backend/app/features/voice/PERSISTENCE.md).

### Run the current application

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

The design/scaffold descriptions below record earlier milestones.

## Part 3.1 research and design

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

The user used ChatGPT's image generation tool to create the low-fidelity wireframes. The supplied review board has been visually inspected and linked in the report. Its Help panel still shows a pending-number placeholder; the confirmed design uses separate U.S. crisis-counseling and emergency-services options. Static images do not demonstrate working navigation or animation. No project-specific UI, backend, model, SQLite persistence, or API integration has been implemented. Existing setup evidence below records earlier scaffold checks and is not a new verification of application behavior.

## Architecture

- `backend/`: Python domain logic, independent of frameworks, with FastAPI as the JSON API boundary. SQLite will eventually persist conversations and skill sessions using Python's standard library; no database package is needed for this scaffold.
- `frontend/`: Vue presentation, with backend-request code kept separate from components. Node.js and npm provide development tooling and builds, not a separate application server.
- `docs/`: project requirements and design/verification notes.
- `prompts/`: the ordered setup instructions used to prepare this scaffold.
- `handoffs/`: current project handoff and continuation notes.

Backend and frontend dependencies are project-owned: `backend/.venv` and `frontend/node_modules`. Do not install project dependencies globally. Future Vue–FastAPI communication must use a documented JSON contract covering payloads, responses, and errors before integration.

## Setup and verification

Setup follows [the setup prompts](prompts/setup-prompts.md) in order. No backend application or API exists yet.

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

TODO: add the exact backend development and test commands when an application module and tests exist. There is no FastAPI server to start at this stage.

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

The build writes ignored `frontend/dist/`. The development server serves the starter locally; no backend connection exists. Stop it with Ctrl-C in the terminal that started it. A production build can be served locally with `npm run preview -- --host 127.0.0.1`. Browser rendering and interactive behavior have not been checked; scaffold verification covers imports, dependency consistency, lint, and compilation.

## Setup evidence (October 8, 2026)

Steps 1–8 of the setup guide are complete. The user approved the current generator's bundled Oxlint on October 8, 2026. Step 9 awaits Git identity and initial commit approval.

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

Read-only commands used: `pwd`, `ls -la`, `rg --files` (including hidden files and targeted patterns), `find docs -maxdepth 2 -type f -print`, `cat prompts/setup-prompts.md`, `cat docs/assignment-description.md`, ancestor `AGENTS.md` checks, `cat AGENTS.md README.md`, `uname -a`, `sw_vers`, `whence -a`/`whence -pa` for Python/Node/npm/Git, individual executable `--version` calls, `command -v node npm`, `git rev-parse --show-toplevel`, `git rev-parse --is-inside-work-tree`, and `git config --get user.name`, `git config --get user.email`, `git config --get-regexp '^user\.(name|email)$'`. Python inline inspection enumerated executable names on PATH and checked whether the environment, manifests, lockfile, and dependency directory existed. Git identity is currently unset; it must be resolved before a commit. No global configuration was changed.

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

Confirmed project root: `/Users/jlee/Desktop/psu4/ist402/a3_mental_health`. No enclosing repository exists. Requested the missing author name/email; no identity has been invented or configured globally. A remote will not be configured or pushed during setup.

Proposed commit: `chore: initialize verified FastAPI and Vue scaffold`. Scope: root documentation/rules/ignore file, backend dependency manifest, generated Vue starter/configuration and npm lockfile, original assignment documentation, and original setup prompts. Generated environments, node_modules, build output, caches, editor settings, OS artifacts, and secrets are excluded. Git initialization/staging and the commit remain pending; a commit requires explicit approval under the setup guide.

## Open decisions

- TODO: refine feeling-slider labels and the burden of required feeling/color/graph inputs; reconcile the mockup's Help placeholder with the confirmed resource design when refining the interface.
- TODO: resolve adaptive UI, approved reply-setting values, age scope, crisis-input policy, and the proposed fourteen-pattern chat influence. No automatic sensing or contraction is approved.
- TODO: select model provider, reviewed retrieval corpus and rights, context permissions, privacy disclosure, embedding location, retention, and deletion semantics. Local SQLite does not establish fully local model processing.
- TODO: turn the proposed SQLite records into a schema and document the JSON API request/response/error contract before implementing or integrating routes.
- TODO: implement and verify independent persistent Help, failure/exit behavior, fixed breathing steps, and conversation/session history in a later milestone.
- TODO: measure guided exercise duration (no more than 90 seconds at the intended pace), including application delays and stated response assumptions; report entry/setup separately. The current breathing budget is a proposal, not a measured result. No forced chat timeout is planned.
- TODO: create the required fictional evaluation scenarios and repeatable checks; update AI-use disclosure and evidence with actual results as work proceeds.
- The report records the Part 1 content commit and uses file links pinned to it. A follow-up reference commit saves that hash in the report; no commit can contain its own hash. Confirm instructor access before uploading the report.
