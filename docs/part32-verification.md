# Part 3.2 observed verification

October 26, 2026, Eastern. Guided breathing and typed conversation persistence.
Browser checks used the production build, the local mocked rehearsal server on
port 8001, and **separate** `backend/data/submission-demo.sqlite3`. No paid model,
microphone or resource call was made. All content is fictional. The existing
normal database was inspected read-only, without modifying its records.

## Observed browser and SQLite results

| Check | Observed result | Evidence |
| --- | --- | --- |
| Complete the chosen skill | Six four-in/six-out cycles completed, 60s breathing, 63.0s including countdown, **66.6s first instruction to finish**, no pauses. The saved row has instruction_seconds 66.6121 and wall-clock Begin-to-record approximately 63.01s. | [Completion](evidence/part32-breathing-complete.png), [SQLite snapshot](evidence/part32-database.json) |
| Pause and leave | Emergency interrupted a repeat; closing it left Resume visible. Early End returned Home and saved `ended`, active 3.6859s, pause 13.5791s. | [Session history](evidence/part32-session-history.png), SQLite snapshot |
| Breathing save failure | A temporary failure trigger on the isolated demo table produced 503. End still returned Home; unsaved notice and Retry appeared. Emergency opened. Removing the trigger and Retry created one ended row using the same UUID. | [Failure](evidence/part32-breathing-save-failure.png), [HTTP trace](evidence/part32-http.txt) |
| Typed conversation save/review | A fictional typed question and labeled mock reply saved as two rows; history retained the exact text after reload. | [Saved chat](evidence/part32-saved-chat.png), SQLite snapshot |
| Chat save failure | A temporary trigger failed the assistant insert: transaction left no partial pair. The reply remained visible with an unsaved notice. End chat retained Retry on Home. Removing the trigger and Retry sent a PUT only, no second generation POST. | [Failure](evidence/part32-chat-save-failure.png), HTTP trace |
| Model-request failure | `demo:fail` produced 502. The draft remained; no assistant bubble or new saved conversation appeared. Emergency opened from the failure state. | [Reply failure](evidence/part32-model-failure.png), HTTP trace |
| History and deletion control | New chat started empty. Saved history displayed two conversations. Delete showed confirmation; Cancel preserved the record. Emergency opened during confirmation. Actual deletion was checked in temporary-database/API tests, not performed on browser records. | Browser observations and backend tests |
| Server restart and independent safety | Stopped only this task's demo server. Cached shell reloaded, session history failed explicitly, Emergency still opened. Restarting the same server restored all three breathing rows and two conversations in the browser. | [Offline Emergency](evidence/part32-offline-emergency.png), SQLite snapshot |

The 66.6s measure begins when the ready screen mounts and includes about 3.6s
before Begin, the countdown, pacing and application delays. Entry/Home navigation
was outside that interval and was not separately timed in this check; the user's
final recording should report it separately. The earlier observed 63.1s/64.0s
runs and 75s design budget are in [iteration verification](iteration-verification.md).
Voluntary pauses/support access are excluded; long voluntary reading can exceed
90s and does not force an exit. Browser timings are software measurements, not
evidence that a person followed the breathing or benefited from it.

## Automated checks

- Full backend: **157 passed**, including actual temporary SQLite restart,
  atomic rollback, concurrent identical writes, changed retries/position conflicts,
  role/settings rejection, UTF-8/JSON limits, storage failure and deletion.
- Full frontend: **66 passed**, including storage-only Retry after navigation,
  duplicate Retry, malformed save acknowledgments, stale/failed/late replies,
  saved-history races/deletion and existing voice lifecycle/clock checks.
- Non-mutating Oxlint and ESLint pass. Production Vite build passes (51 modules).
- Original interface → emotion → breathing isolated cumulative checkpoints pass
  with unchanged manifest. Final generated result is copied to
  [checkpoint evidence](evidence/part32-checkpoints.json).
- Existing Starlette/TestClient httpx deprecation warning remains. No dependency
  changes were made to suppress it. Network-connection tripwires protect backend
  mock checks. The browser mock server replaces the provider entirely.

Commands: `backend/.venv/bin/python -m pytest -p no:cacheprovider -q -c
backend/pytest.ini backend/tests backend/app/features`; `npm --prefix frontend
test`; from frontend, `npm test`, `npm exec --offline -- oxlint .`,
`npm exec --offline -- eslint . --no-cache`; `npm --prefix frontend run build`;
`backend/.venv/bin/python scripts/verify_checkpoints.py`;
`backend/.venv/bin/python scripts/serve_submission_demo.py --port 8001`;
`backend/.venv/bin/python scripts/inspect_submission_db.py --demo --messages`;
read-only sqlite3/Python inspection; CUA browser controls/screenshots; `git diff
--check`; local Markdown/JSON/Python-source checks. Final teardown stops only the
demo process started here.

## Revisions and remaining evidence

One malformed-Unicode test initially failed in httpx's serializer before reaching
the app. Sending escaped JSON corrected the test, which now verifies server 422.
An npm check used the root-style prefix while already inside frontend; it failed
before running checks, then passed with the correct working directory. The first
local bind was sandbox-blocked; the approved localhost launch succeeded. A
nonmatching initial contract patch changed nothing; the full persistence contract
was then added. Browser review exposed stale Home “coming soon” copy and the
need to show measured timing in saved session history; both were corrected.

The code and mocked/provider-request wiring are verified; **actual generated
model behavior remains unobserved**. Before submission, record a bounded fictional
typed exchange with the configured model, report its identifier and observed
behavior, attach a recording, review/commit/push the intended version and confirm
instructor access. See [the validation walkthrough](part32-validation.md).
No clean dependency install on another machine, native phone installation,
full accessibility review, real voice behavior or clinical evaluation is claimed.
Pending saves remain memory-only; captions are not saved; historical context and
RAG remain deferred. The Part 3.3 evaluation is not completed by these checks.
