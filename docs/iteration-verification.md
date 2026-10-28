# First iteration: observed verification

October 21, 2026. Fictional data only. No real calls, live-model requests, peer testing, or clinical evaluation. This is software verification, not evidence of effectiveness. See the exact layer/feature boundaries in [architecture](architecture.md), [checkpoint scopes](implementation-checkpoints.md), and feature-owned contracts/READMEs.

## Independently buildable checkpoints

`scripts/verify_checkpoints.py` constructs each checkpoint from the recorded scaffold commit plus only its cumulative manifest paths. It does not merely disable features in the full checkout.

| Scope | Frontend tests | Backend tests | Non-mutating Oxlint / ESLint | Production build |
| --- | --- | --- | --- | --- |
| Interface only | 4 passed | No backend application in this scope | Passed | Passed, no feature imports required |
| Interface + emotion | 4 passed | 7 passed | Passed | Passed, no breathing imports required |
| Interface + emotion + breathing | 10 passed | 9 passed | Passed | Passed |

These counts include checks for layer/feature boundaries and offline-cache exclusions. Backend tests use temporary SQLite databases and actual FastAPI TestClient requests. Audio tests use a mocked AudioContext. Existing TestClient emits a Starlette/httpx deprecation warning; tests pass and no dependency was installed to suppress it. Existing project-owned dependencies are borrowed by checkpoint snapshots; clean installation on another machine is not established.

Exact per-run snapshots/results live in ignored `.checkpoints/` and can be regenerated. The verifier was also run from the interface-only snapshot: it passed the interface checks and skipped absent future modules. The staging helper was exercised in preview mode; `git diff --cached --name-only` remained empty. No commits/pushes or branch/index changes occurred.

## Fictional scenarios

| # | Scenario and expected behavior | Observed result and evidence type |
| --- | --- | --- |
| 1 | Home offers independent log, breathing, chat paths | Browser navigated to all three without an emotion prerequisite; chat clearly unavailable, End chat returns Home. |
| 2 | Continue with no feeling/color | Browser showed both missing-field messages; did not advance. |
| 3 | Choose feeling/color and leave optional meaning blank | Browser accepted explicit choices; domain/API roundtrip accepted an empty optional meaning. |
| 4 | Save with untouched graph | Browser blocked save and requested point/sliders. |
| 5 | Place graph point using keyboard | ArrowRight selected pleasantness 5 / energy 0; Enter selected the center in another scenario. |
| 6 | Save a valid fictional entry | Browser displayed saved confirmation only after API success; calendar showed a saved entry. |
| 7 | Edit an entry, then reload/restart | Browser retained edited note/coordinates after reload; API tests confirmed restart persistence and preserved original date/time. |
| 8 | Repeat a save after ambiguous delivery | Temporary-database API test reused UUID: 201 then 200, one row. |
| 9 | Multiple daily entries and deletion | API tests cover persistent CRUD; calendar count/day selection exists. Browser checked deletion dialog cancel and Emergency over that dialog. Final destructive deletion was checked through temporary-database tests, not by deleting user records. |
| 10 | Stop backend while saving an entry | Browser showed an unavailable message, retained feeling/color/note/graph on Back, and kept Emergency accessible. |
| 11 | Pause during countdown | Browser showed paused state; closing Emergency did not resume; Resume continued the countdown. Deterministic clock test preserved exact offset. |
| 12 | Pause mid-phase and end early | Clock tests preserved phase/offset; browser End returned Home and SQLite history distinguished ended from completed. |
| 13 | Finish all six fixed cycles | Browser completed two real-time sequences at 63.0s including countdown; actual SQLite completed records retained 60s breathing. |
| 14 | Synchronize circle and original audio | Browser DOM showed matching inhale/exhale phase keys and running AudioContext, circle scale changes, and successful completion. Mocked audio tests checked remaining-phase scheduling after resume and cleanup. Listening quality is unverified. |
| 15 | Mute and reduced motion | Browser mute cleared active audio phase while other cues remained; reduced-motion circle stayed at scale 1.000 while text/audio timing continued. |
| 16 | Open Emergency during exercise/overlay/error | Browser sampled countdown, paused practice, emotion/save failure, settings, delete overlay and offline history failure. Dialog Escape restored focus; returning to breathing required Resume. No calls placed. |
| 17 | Restart with persistent records after module extraction | Production browser loaded the edited emotion entry and distinct completed/ended breathing sessions through independently registered features. Emotion history requested only entries. |
| 18 | Reload PWA after stopping FastAPI | Browser reloaded the cached production shell at port 8000; history explicitly failed, Emergency opened, and offline breathing displayed exhale with matching active audio phase. |
| 19 | End offline, then restore server and Retry | Browser showed “hasn’t been saved”; after restart Retry displayed saved confirmation and session history included the ended record. No background replay claimed. |
| 20 | Backend database unavailable at startup | API/static test loaded the shell while entry requests returned a 503 JSON envelope; unknown API paths returned JSON 404 rather than HTML. |

## Cross-cutting behavior checks

1. **Independent Emergency and user exits:** shared shell renders Emergency for every route; modal component includes its own access. Sampled browser paths above pass without backend/model decisions. This is not an exhaustive accessibility audit of every browser/screen-size combination.
2. **Fixed skill and timing:** pure clock tests check all six exact 4s/6s boundaries, 3–2–1, pause exclusion and frame drift. Healthy real-time browser sequences reached completion at 63.0s. No 90-second forced exit exists; reading/voluntary pauses do not remove control.
3. **No false persistence or personal cache fallback:** API responses have no-store headers; unit tests verify the service worker excludes `/api`, writes, other origins and unknown resources. Real offline history showed an error, failed saves stayed explicit, and Retry succeeded after recovery.
4. **Commit/layer independence:** isolated builds omitted later modules entirely. Tests check HTTP confinement, pure-domain imports, middleware/storage responsibilities and sibling-feature independence.

## Timing assumptions and limits

The first instruction appears on the breathing ready screen. Two observed instruction-to-finish values were **63.1s** for an immediate Begin and **64.0s** on a media-enabled run, excluding chosen pauses. Both include the countdown and actual application delays. The conservative design budget remains 8s reading + 2s choosing Begin + 3s countdown + 60s breathing + 2s transition = 75s; this is an assumption, not a measured population result. Entry/splash/navigation occur before this measurement. Repeat starts a fresh instruction interval. Main-thread stalls pause pacing rather than skipping phases; their application delay remains in instruction time, while the subsequent explicit pause is excluded.

Native phone install/standalone relaunch, audible quality/loudness, long-duration background suspension, crash recovery, large datasets, complete WCAG conformance, clean dependency installation on another machine, and model behavior are unverified. The localhost URL on this computer is not a phone-accessible deployment. Session saves are memory-only until successful and may be lost on reload/close. No conversation/model contribution is implemented, so those Part 3.2 requirements remain outstanding.

## Revised approaches

The initial full implementation imported feature views directly and mixed breathing history into emotion history. The user's requirement for independent commits exposed that dependency. Features now self-register, own their SQL/tests/styles/contracts, and use separate history screens. The three actual checkpoint builds pass without later feature files.

A lint failure caught an unnecessary GET body property in the shared fetch client; conditional payload construction corrected it. Snapshot lint initially skipped files because snapshots are intentionally Git-ignored; the verifier now lints explicit source roots with ignore bypass only inside those generated snapshots. Temporary hot-reload failures during file moves were resolved by completing extraction/reloading; production builds and browser navigation passed afterward.

## Commands and changed files

Inspection: `pwd`, `rg --files`, `cat`, `head`, `tail`, `wc`, `git status --short`, `git diff --check`, image viewing, CUA DOM/screenshot inspection, official documentation lookup. Environment check: project `.venv` imports/version inspection. Edits: apply_patch, project Python/pathlib and shell heredocs. Icon PNGs were generated from original geometric code with Python standard-library `struct`/`zlib`; no imaging dependency or downloaded asset.

Checks: `npm test` (Node built-in runner), `npm exec --offline -- oxlint .`, `npm exec --offline -- eslint . --no-cache`, `npm run build`, `.venv/bin/python -m pytest -q` from backend, `scripts/verify_checkpoints.py`, `scripts/stage_checkpoint.py interface` in preview mode, `git diff --cached --name-only`, `git diff --check`, localhost curl readiness, SQLite read-only aggregate inspection, and local Markdown target checks. Some commands were run from the appropriate project subdirectory as documented in README. Initial CSS/build failed from a wrong working-directory-relative output path; it was corrected before the first gate passed.

Runtime checks started only this task's localhost Vite/FastAPI servers, stopped/restarted them to exercise failures, and use the production build for offline checks. No other processes were stopped. No dependency/global/machine installation or Git mutation was performed. Final teardown stopped only this task’s FastAPI/Vite servers; restart commands are in README.

Code/feature files changed are enumerated exactly in [the scope manifest](../scripts/checkpoints.json). Root README, AGENTS, AI-USE, design notes, evidence log and handoff were updated for current behavior while preserving prior edits; these documentation changes remain outside code staging scopes. The Part 3.1 report and original wireframe were preserved.

Visual evidence: [current interface](evidence/interface.jpg). Machine-readable scope outcomes: [checkpoint results](evidence/checkpoints.json). These files contain fictional/interface evidence only.
