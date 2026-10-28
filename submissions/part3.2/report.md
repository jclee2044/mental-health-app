# Assignment 3 Part 2 Working Application and Safety

## Scope and project access

I focused this version on completing guided breathing through the running Vue
interface, with FastAPI and SQLite on localhost. Emotion logging is also available,
but breathing is the chosen skill for this submission. Home offers breathing,
logging and chat independently; no emotion entry or conversation is required
before starting an exercise.

Repository: [mental-health-app](https://github.com/jclee2044/mental-health-app).

Submitted version: **TODO: reviewed and pushed commit URL**. This draft is not yet
ready to upload. Replace relative evidence links with accessible repository URLs
pinned to that commit before uploading this standalone file. Preserve the earlier
Part 3.1 report separately.

## Working breathing experience

The exercise provides a 3–2–1 countdown followed by six cycles of four seconds in
and six seconds out. Text, circle motion and optional recorded breath cues carry
the pace. Pause, End, mute and reduced-motion alternatives preserve user control.
The browser owns the fixed sequence; model requests and SQLite saves cannot
change or delay a breath. This follows the assignment's R1 timing concern, R3/R4
permission and choice, and D2/D3/D4 focus, low input burden and persistent safety.

The observed October 26 browser run completed **60 seconds of breathing** with a
**63.0-second sequence** including countdown. First instruction to final step was
**66.6 seconds**, including about 3.6 seconds before Begin and application delays,
with no pauses. Entry/Home navigation was outside that interval. TODO: report
separately measured entry/setup time from my final recording. User-chosen pauses
and accessing support are excluded; the app does not force completion or exit.
[Timing screenshot](../../docs/evidence/part32-breathing-complete.png).

## Model contribution and saved records

The typed model interface can explain the fixed breathing instructions and respond
to the current fictional conversation. Server-owned instructions supply reviewed
application facts, preserve refusal and prevent the model from controlling exits,
safety access or the exercise. No RAG is connected. The useful contribution is
optional explanation/conversation; pacing remains deterministic application code.

**TODO: link a short actual fictional model exchange, identify the configured
model, and explain its observed contribution and one limit.** The current browser
evidence uses replies explicitly labeled as mocks. These demonstrate integration,
not generated model quality or prompt obedience. No paid calls were made for
these checks.

SQLite stores completed/ended breathing sessions with timestamps and duration
fields in `skill_sessions`. Completed typed exchanges save separately as atomic
user/assistant pairs in `chat_conversations` and `chat_messages`. Saved sessions
and typed chats can be reviewed after reload/server restart. Typed chats can be
deleted after confirmation; old chats are not automatically reused as model
context. Voice audio/captions and failed reply requests are not persisted. Local
SQLite storage does not establish local processing or provider retention/training
policies. [Database evidence](../../docs/evidence/part32-database.json),
[saved-chat view](../../docs/evidence/part32-saved-chat.png).

## Safety and failure behavior

Emergency stays available during exercises, history, confirmation and failures,
independently of model/classifier/network success. It opens separately labeled
U.S. crisis-counseling and emergency-service resources. No call was placed in
testing. With the backend stopped, the cached shell and Emergency still worked;
history showed an explicit error. [Offline safety evidence](../../docs/evidence/part32-offline-emergency.png).

Opening Emergency during breathing paused the exercise; closing it required
explicit Resume. Early End returned Home and saved a partial `ended` record.
A simulated save failure displayed “hasn’t been saved” and Retry. Successful
recovery saved the same UUID once. Typed-save failure kept the received reply
and allowed storage-only Retry after ending chat, without repeating generation.
A failed reply kept the draft and did not invent an assistant message.
[Observed checks and failure evidence](../../docs/part32-verification.md).

## Verification and unfinished work

The full mocked checks passed 157 backend and 66 frontend tests, non-mutating
linters, the production build and all three isolated original checkpoint builds.
Real browser checks covered completion/timing, early exit, Emergency, save/reply
failures, recovery and SQLite persistence after server restart. Browser/SQL steps
are reproducible in the [validation guide](../../docs/part32-validation.md).

TODO: add an accessible recording link showing the running app, matching browser
requests and SQLite rows; replace the submitted-version and live-model TODOs.
Failed-save queues remain memory-only and can be lost on reload/close. Voice
caption persistence, historical personalization, RAG, session deletion controls,
clean installation on another machine and comprehensive accessibility checks
remain unfinished. These are software checks with fictional scenarios, not
clinical evaluation. The prototype is not therapy, diagnosis, monitoring or a
support service. The broader fifteen-scenario/live-variation evaluation belongs
to Part 3.3.

AI assistance, commands, revisions and evidence limits are disclosed in
[AI-USE.md](../../AI-USE.md) and [the evidence log](../../docs/evidence-log.md).
