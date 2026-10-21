# Implementation boundaries

One Vue frontend and one FastAPI backend, running on localhost. Middleware lives inside FastAPI. Node supplies development/build tooling; there is no third application server. SQLite uses Python's standard library. No dependencies were added.

## Layers inside independently committable features

| Layer | Location | Owns | Must not own |
| --- | --- | --- | --- |
| Interface shell | `frontend/src/App.vue`, `components/`, `views/`, `composables/usePreferences.js` | Navigation, shared controls, Emergency, appearance, chat stub, PWA status | Feature imports, HTTP, SQL, emotion or breathing rules |
| Feature presentation | `frontend/src/features/<feature>/*View.vue` | Accessible forms/screens, in-memory drafts | Fetch, SQL, model requests |
| Feature request methods | `frontend/src/features/<feature>/api.js` | Endpoint names and payload forwarding | HTTP implementation, rendering, skill timing |
| Shared HTTP client | `frontend/src/api/client.js` | Fetch, timeout, response/error envelope | UI, SQL, breathing timing |
| Browser feature logic | Feature `domain.js` / `clock.js` / `audio.js` | Explicit input labels; fixed timing; sound and visual coordination | Database access, emotion/risk inference |
| Middleware | `backend/app/middleware.py` | `Cache-Control: no-store` transport policy | Feature imports, skill rules, SQL |
| Feature routes and schemas | `backend/app/features/<feature>/routes.py`, `schemas.py` | HTTP shapes, statuses, domain/storage orchestration | SQL or business rules |
| Python domain | Feature `domain.py` | Framework-free validation and semantic rules | FastAPI, Pydantic, SQLite, HTTP |
| Feature storage | Feature `storage.py` | Its own table/schema, parameterized SQL and transactions | HTTP, interpreting emotion/colors |
| Shared database | `backend/app/database.py` | Opening/closing SQLite connections | Feature schemas, domain or HTTP logic |

Data path: Vue view → feature API methods → shared HTTP client → FastAPI middleware → feature route → domain checks → feature storage → SQLite.

Breathing uses a monotonic browser clock for counts, circle scale and audio. Requests only save/retrieve session records. Emergency and exits never wait for requests. No request is sent for each inhale/exhale. Storage does not determine where a future model will run.

## Feature boundaries and commit order

`frontend/src/features.js` discovers `features/*/index.js` using Vite's static glob. An empty feature directory is valid: the shell shows an honest pending screen. Each feature's entry point registers its own routes, state, styling and optional notices. The shell has no hard imports of feature components.

The backend composition root discovers local packages under `app/features/`. Each registers its router and storage initializer. Shared code imports no feature directly; sibling features import none of each other's code. Adding the breathing package creates only its own table. Routine tests enforce HTTP confinement, framework-free domain logic and feature independence.

1. **Interface**: shared shell, responsive Home, Emergency, appearance, chat stub, PWA shell. No backend required; use Vite development/preview.
2. **Emotion**: shared API/database foundations plus emotion frontend/backend modules. Includes logging, graph, calendar, edit/delete and its contract/tests.
3. **Breathing**: only the breathing frontend/backend modules. Includes clock, motion/audio, retryable session saves, its own history, contract/tests. No edits to interface or emotion files are required to install it.

Exact staging scopes and isolated verification are documented in `implementation-checkpoints.md` and `scripts/checkpoints.json`. No commit or index mutation is performed automatically. Root documentation already modified before implementation stays outside these scopes.

## Decisions and limits

Still is a provisional visual name. The supplied wireframes guide layout; original CSS/vector art supplies polish. Emergency replaces Help. Repeated prototype labels are removed from activity screens; About accurately describes the coursework role. Audio is now explicitly authorized. Calls are never placed during tests and must be simulated during interactive demonstrations.

Chat stays a frontend stub, with no sending/model/conversation persistence. Those Part 3.2 requirements remain unfinished. No inference/adaptation, authentication, external model, speech service, microphone, or analytics. Failed session saves are retryable only within the current app instance. Forced closing/reloading can lose them. Target-device audio quality and native install behavior require direct checks.
