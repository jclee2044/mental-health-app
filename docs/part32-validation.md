# Part 3.2 browser and database validation

Focus the submission on guided breathing, with a short typed chat demonstrating
the model separately. Emotion logging is optional supporting evidence. The
breathing clock, exits and Emergency do not wait for a model or database.

## Run the version you are recording

From the project root, build the current frontend:

```sh
npm --prefix frontend run build
```

For a rehearsal with **no paid calls**, run:

```sh
backend/.venv/bin/python scripts/serve_submission_demo.py
```

Open `http://127.0.0.1:8001/`. Replies say **Mocked demonstration reply**.
The separate database is `backend/data/submission-demo.sqlite3`. This demonstrates
the interface/API/SQLite integration, not generated model behavior. Voice is not
supported in this rehearsal; do not select Start voice. Send `demo:fail` for a
controlled reply failure. Other typed input gets the fixed breathing explanation.

For the actual configured application, use the README's backend command and
`http://127.0.0.1:8000/`; its database is `backend/data/still.sqlite3`.
The backend process needs server-only `OPENAI_API_KEY` and `VOICE_BACKEND_MODEL`.
Never put credentials in Vue, screenshots, shell transcripts or the report.
Do not run an additional server on an occupied port or stop another chat's process.
Restart only your own server to load changed code. Reload/update the PWA after
building so the recording shows this version.

## Record a short sequence

| Step | Action and browser evidence | Database evidence |
| --- | --- | --- |
| 1 | Open DevTools Network, enable Preserve log, filter `/api/`. Start Home → Guided breathing directly. Explain that no emotion entry/chat is required. | Establish the session count before starting. |
| 2 | Show first instruction, click Begin promptly, complete six 4s/6s cycles. Capture the final sequence and instruction-to-finish times. Measure entry/setup separately with the recording or a stopwatch. | Find the new `completed` row and its UUID. Confirm `active_seconds=60`, `sequence_seconds=63`, and the observed `instruction_seconds`; inspect the matching `PUT /api/sessions/{uuid}` JSON and response. |
| 3 | Open past breathing sessions, reload, then stop/restart only your own server and reload. | The same UUID remains; this distinguishes SQLite persistence from Vue memory. Refresh/reopen the DB viewer if it holds a stale snapshot. |
| 4 | Start another exercise, Pause, open Emergency, close it, and show that Resume is explicit. End early. | A separate `ended` row has partial active time; it does not claim completion. |
| 5 | In typed chat, ask a fictional question such as “What are the breathing steps, and can I stop early?” Capture `POST /api/chat/messages` with bounded current-chat context and its reply. | After the separate `PUT /api/chat/conversations/{uuid}/turns/{uuid}`, there are two message rows in that conversation. |
| 6 | End chat → reopen chat → View saved typed chats. Reload, open the saved conversation and compare its text. Show a new chat starts empty. | Match `conversation_id`, turn UUID, roles, contents and UTC timestamps. Opening history makes only GET requests, never another model POST. |
| 7 | Simulate a request failure and show the error, retained draft/retry, End/Home and Emergency. Open the resource panel without clicking call links. | No invented assistant message or successful-save claim. After recovery/retry, inspect the resulting row count. |

For **model-contribution evidence**, use the normal configured application and a
small fictional typed exchange, for example the question in step 5 and one
follow-up. Record the actual configured model identifier privately from your
server setup and disclose it in AI-USE/report without credentials. Compare its
reply with the fixed skill requirements and refusal/exit boundaries. The existing
server prompt supplies reviewed breathing context; no RAG is connected. A mock
reply must never be presented as an actual model result. The coding agent did not
make live calls in this increment. Limit the recording to the small exchange you
need; do not enable voice to demonstrate this requirement.

## Inspect SQLite directly

Use the database inspection tool practiced in class to **open the correct file**,
select read-only mode if available, and browse `skill_sessions`,
`chat_conversations` and `chat_messages`. Do not expect these in browser
Local Storage or IndexedDB: SQLite is on the FastAPI side.

Run these queries in its SQL panel, or in an already-installed SQLite CLI:

```sql
SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;

SELECT id, status, started_at, ended_at, active_seconds, sequence_seconds,
       pause_seconds, instruction_seconds
FROM skill_sessions ORDER BY started_at DESC;

SELECT c.id, c.created_at, c.updated_at, COUNT(m.role) AS message_count
FROM chat_conversations c JOIN chat_messages m ON m.conversation_id=c.id
GROUP BY c.id ORDER BY c.updated_at DESC;

SELECT conversation_id, turn_id, position, role, content, created_at
FROM chat_messages
ORDER BY conversation_id, position, CASE role WHEN 'user' THEN 0 ELSE 1 END;
```

Without a GUI or CLI installation, the project also has a read-only inspector:

```sh
backend/.venv/bin/python scripts/inspect_submission_db.py
backend/.venv/bin/python scripts/inspect_submission_db.py --demo --messages
```

Default inspection omits message contents. Use `--messages` only for fictional
records you intend to show. The script cannot create a missing file. Start the
updated server first to create the new chat tables. Include the file path, SQL,
and relevant rows in evidence; redact unrelated content. Do not commit SQLite
files, credentials or unredacted HAR exports.

## Demonstrate failures without losing your work

For a breathing save failure, in DevTools Network request blocking, block
`*/api/sessions/*` before ending a short exercise. The exercise and Emergency
should still work. Show “hasn’t been saved,” unblock, then Retry session save.
The PUT repeats its UUID and creates one record. If your browser lacks request
blocking, use offline mode after the already-loaded page is ready, then restore
online before Retry. No reload while the save is pending: the retry queue is
memory-only.

For a typed save failure, block `*/api/chat/conversations/*` **before sending**
a fictional message. Leave `/api/chat/messages` unblocked. The reply appears,
but the app says “Typed exchange not saved.” End chat if desired: the Retry chat
save control stays available. Unblock and Retry. Network should show only a PUT,
not another `/api/chat/messages` POST; SQLite should contain exactly two rows for
that turn. This avoids another paid model call. Use the mock server for rehearsal.

For a failed reply, use `demo:fail` in the mock server, or block
`*/api/chat/messages` in the normal app. The draft remains editable, there is no
assistant reply, and Emergency/End remain usable. Disable request blocking when
finished. Check failures against expected results; do not label a planned check
as passed.

## Finish the submission

- Record the actual model exchange, browser/SQL walkthrough and timing assumptions.
- Replace the TODOs in `submissions/part3.2/report.md`; upload it as `report.md`.
  Preserve root `report.md` as the historical Part 3.1 submission.
- Review the changed/untracked files, commit the intended version, push it and
  put that commit/link in the report. Check instructor access to all evidence.
  Replace the draft's relative evidence links with accessible GitHub links pinned
  to that submitted commit before uploading the standalone report.
  Do not stage everything blindly; the original three checkpoint scopes remain.
- Disclose limitations: transient voice captions, approximate voice grouping,
  memory-only failed-save queues, no automatic historical context/personalization,
  no RAG, and no clinical or comprehensive accessibility validation.
- The fifteen-scenario evaluation with repeat live cases and process screencast
  belongs to Part 3.3. Existing tests can support this milestone, but do not claim
  its broader evaluation is complete.
