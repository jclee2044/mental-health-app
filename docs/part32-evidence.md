# Part Two curated prompts and evidence

This supplements the [project evidence log](evidence-log.md) for the
[Part 3.2 report](../submissions/part3.2/report.md). User observations below were
supplied on October 28, 2026; they are separate from Codex's mocked checks.
Only selected project prompts are included, not a full chat export.

## Selected prompts and decisions

### Research and system prompt

User-supplied prompt excerpt, reproduced as evidence rather than a new research request:

> using web search, i need you to conduct research on the best mental health chatbots. what are the voices like, how do they talk, what tone do they use, and how do they respond to different types of user queries, including things like suicidal intimations and so on? what edge cases come up and how should it respond? also do extensive research on therapists and training on how to talk to patients. the purpose of this research is to figure out what the system prompt needs to include.

Follow-up:

> summarize your findings by category. what are the most important things and what are the decisions i have to make?

> can you create the system prompt using the research results

The user's policy choice:

> i think somewhere in the middle with room to move in either direction based on user inputs is best. for example, when the user asks a question, the bot should move more into offering interpretations and suggestions. if the user is mid-explanation, the bot should mostly reflect and mirror. when mirroring, it should strive to use the user's exact words as much as possible.

Example supplied by the user:

> user: "I'm having a really hard time figuring this out"
>
> bot: "figuring it out?"
>
> user: "yeah, i think it's... [continues explaining]"

**Change/decision:** research informed the separate server-owned Live and Responses
instructions. Listening/exploration and practical answers depend on the input;
there is no required mode selector. Sources and their limits remain in the
[communication research](chatbot-communication-research.md) and
[system-prompt documentation](chat-system-prompt.md).

### Revised approach: excessive echoing

The user reported that the bot was repeating words without probing or moving the
conversation along. They supplied a fuller example:

> other types of echoing too. example:
>
> "i love to play with my dog. its so much fun to spend time that way"
>
> "i get it. you love spending time playing with your dog. [relevant question]"

**Change:** `backend/app/features/voice/prompts.py` now requires one relevant
question with every echo/reflection/selective summary. Question-form echoes count;
requests for no questions or to stop take priority. The user found the revised
flow more natural. This is a reported observation, not a controlled comparison.
**Verification:** the existing log records 188 backend tests passing after the
prompt updates; those mocks verify wiring, not generated compliance. Planned
fictional prompt cases remain distinct from observed results.

### Revised approach: transcript spacing

**Observation:** the user saw leading spaces as voice messages appeared and found
the corrected bubbles cleaner and easier to read. **Change:** assembled bubble
starts are normalized in `frontend/src/features/chat/domain.js`; internal spaces
and raw fragments are preserved. **Verification:** the publication log records
101 frontend tests, lint and build passing, including rendered whitespace checks.
No new microphone check was made for this report.

### Revised approach: design and icon

The user described the desired style, used ChatGPT to ask clarifying questions
and generate multiple reference UIs, then provided feedback until satisfied.
Codex used that reference to redesign the app because the earlier design felt
generic. A verbal icon description produced an unexpected result; the user then
used Codex's sketch functionality to draw the desired icon and obtained a closer
match. **Decision:** use a drawn reference when a verbal description leaves too
much ambiguity. This sequence is user-reported; the original failed icon image,
exact prompts and image-generation model/version were not supplied here.
[Redesign implementation and screenshots](inspire-theme.md) document the code
and browser observations, without claiming the missing artifacts exist.

## Screenshot and observation index

| Evidence | What it shows | Source and limit |
| --- | --- | --- |
| [Six-cycle completion](evidence/part32-user-breathing-complete.png) | 6/6 cycles, 63.0s sequence, 63.9s instruction-to-finish, excluding pauses | User-supplied current-design screenshot; user reports repeated full/early-release runs. Entry/setup was not separately timed. |
| [SQLite conversation text](evidence/part32-user-sqlite.png) | `chat_voice_messages`, user/assistant roles, content, timestamps | User supplied and confirmed fictional. Used byte-for-byte as explicitly requested; local username/path and unrelated UI retained with permission. Shows rows, not independent proof of restart, completeness or model identity. |
| [Early release → Home](evidence/part32-current-breathing-exit.jpg) | Home, Emergency and “Breathing session saved” | Codex browser check of current production assets on mocked localhost server. |
| [Ended session](evidence/part32-current-ended-session.jpg), [SQLite fields](evidence/part32-current-exit.json) | `ended`, active 2.2137s, sequence 5.2137s, instruction-to-finish 9.6836s | Same hold/release run; about 5.2s hold includes countdown. Older fictional demo rows are also visible. |
| [Failed reply](evidence/part32-current-request-failure.jpg) | Retained `demo:fail` draft, explicit error, End chat and Emergency | Controlled mock returning HTTP 502; no provider call or invented assistant response. |
| [Emergency after failure](evidence/part32-current-failure-emergency.jpg) | Independent resource panel opens from failed chat | Opened panel only; no call links selected. |
| [Earlier save failure](evidence/part32-breathing-save-failure.png) | Returned Home, unsaved notice, Retry | October 26 mock check; previous visual design. See [original observations](part32-verification.md). |

## Commands and observed checks for this report revision

- Read `AGENTS.md`, `README.md`, assignment, design/research notes, current report,
  disclosure, verification and evidence files; inspected status, remote and log
  with `git status --short`, `git remote -v`, `git log`, `git rev-parse HEAD`,
  `git diff`, `rg`, `cat`, `sed` and `tail`.
- Ran `backend/.venv/bin/python scripts/serve_submission_demo.py --port 8013`.
  Initial sandbox bind failed; approved localhost execution succeeded. This
  project-owned mock replaces the provider and uses ignored
  `backend/data/submission-demo.sqlite3`, never the user's normal database.
- CUA in-app browser: held breathing for about 5.2s, released, observed Home and
  saved partial history; sent `demo:fail`, observed 502/error/draft retention;
  opened Emergency. Saved actual browser JPEGs without altering the UI/images.
  One AX click after a screenshot could not resolve its node; refreshed state
  and used the observed Emergency button's semantic locator successfully.
- Read the newest session using project Python `sqlite3` in `mode=ro`, selecting
  only its ID/status/durations; saved the matching JSON excerpt.
- Copied the two user images with `cp`, unedited. No image-generation call.
- Stopped only this task's demo process (PID 88446), then closed its browser tab.
- Documentation checks: `git diff --check`; project-Python validation of local
  Markdown references, pinned GitHub file targets against commit 3177e4d, image
  signatures and byte-identical supplied copies. No dependency or application
  changes; full runtime suites were not rerun for this documentation task.

The latest pre-existing publication checks are 188 backend tests, 101 frontend
tests, production build, non-mutating lint and three isolated cumulative
checkpoints. These were recorded earlier, not rerun here. No paid calls, real
microphone, model-output verification, real calls, dependency installation,
staging, commit or push occurred in this task. No private research-participant
or third-party content or credentials were added. The dialogue is fictional;
the user explicitly retained the local username/path in their screenshot.

## Remaining verification and publication

- The user authorized publishing the report and evidence and untracking the
  historical root report while retaining its local copy. Application baseline
  is `3177e4d7dc037a69f3eb7d1c073d466577a822b5`. Relative links work in GitHub's
  repository view; a standalone uploaded report needs full published URLs.
- A focused generated-model demonstration and actual configured backend model
  identifier remain unverified here. User identifies the coding model as
  GPT-6.1 Sol; this does not establish the app's backend configuration.
- No recording was supplied. Part 3.2 requires demonstration/evidence but does
  not explicitly require a recording; the demonstration/process screencast is
  explicit in Part 3.3. Entry/setup timing and instructor access remain unchecked.
- Further emotion-flow, accessibility and device checks and the broader
  fifteen-scenario/three-behavior-check evaluation remain for Part 3.3.
