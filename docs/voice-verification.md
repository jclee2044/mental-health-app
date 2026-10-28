# Voice verification and one manual conversation

October 26, 2026. Automated results below were observed. The live procedure is
prepared only: no microphone, browser session or paid provider call was started.
Use fictional coursework content only. This check does not replace the assignment's
fifteen scenarios, three behavior checks, mocked peer testing or later evaluation.

Latest prompt-policy revision: the full backend suite passed **143 tests in 0.82s**
after the research-informed prompt changes, with the same existing deprecation
warning. The typed integration check confirms the complete server-owned policy
is sent; existing Live checks confirm its separate prompt/delegation wiring.
Documentation copies match both effective source constants. This verifies mocked
integration, not echoing quality, generated safety behavior, acoustic timing or
clinical suitability. The 15 prompt-review cases remain planned/not run.
No frontend/build/checkpoint rerun, paid call, microphone or process restart was
needed for the prompt-only implementation change.

Subsequent shared-chat update: 59 frontend tests, 143 backend checks, both linters
and the production build passed. The UI was opened on localhost without a
microphone/provider call; configuration reported unconfigured. Current Start
retains visible bubbles and supplies recent text/captions as bounded history
(16 messages / 6,000 UTF-8 bytes). End chat/navigation starts a fresh conversation.
This supersedes the older empty-input/clear-on-Start and typed-only context
descriptions below. The under-60s live procedure is still planned, not executed.

## Observed automated checks

Run from the repository root, using the existing project environments:

```sh
backend/.venv/bin/python -m pytest -p no:cacheprovider -q -c backend/pytest.ini backend/tests backend/app/features
```

**134 passed in 0.74s**, with the existing Starlette/TestClient httpx deprecation
warning. No dependency was installed to silence it. All existing backend tests
were included, including voice/text, emotion, breathing and layer/shell checks.
Provider HTTP is mocked, with real HTTP-connection tripwires in provider tests.

Run from `frontend/`:

```sh
node --test src/features/chat/tests/voice.test.js src/features/chat/tests/chat.test.js src/features/chat/tests/api.test.js src/features/chat/tests/view.test.js
```

**41 passed in 144.5ms**. Native media, WebRTC, audio, timers and API responses
are fake; the actual Vue SFC is server-rendered with mocked state. This is not
an actual browser/device observation. Existing tests were rerun without changes.

| Requested case | Observed mocked evidence |
| --- | --- |
| Missing configuration | Missing/invalid key or backend model reports unconfigured without provider HTTP; frontend displays a safe error without creating a peer/session. |
| Microphone denial | NotAllowedError becomes a sanitized error, no session request, typed draft retained and text still sends. |
| Offer/answer success | oai-events precedes offer; complete ICE precedes POST; returned answer is applied; only matching session.started makes voice Active and enables tracks. |
| Mute versus End | Mute disables tracks without stopping them, playback, channel or duration timer; Unmute re-enables them. End stops tracks/playback immediately, sends one close, waits for acknowledgment or a 2s limit, then releases transports/timers/listeners. |
| Provider failure | Mocked HTTP errors, timeout, malformed/oversized responses and channel errors are sanitized, never automatically retried; local resources are released. |
| Text after voice failure | Rejected voice creation leaves independent typed HTTP usable and produces a mocked assistant bubble. A failed text reply preserves the draft without inventing a reply. |

Also passed: duplicate Start, repeated End, close failure, late answers after
End/unmount/a newer conversation, permission/ICE cancellation, playback recovery,
unmount, hash navigation, hidden document, pagehide, beforeunload, Emergency and
duration cleanup. SQLite dumps before/after mocked creation/end are identical.
Source: [frontend mocks](../frontend/src/features/chat/tests/),
[backend mocks](../backend/app/features/voice/tests/).

From the repository root:

```sh
npm --prefix frontend run build
```

**Passed in 87ms; 47 modules transformed.** Existing dependency declarations,
lockfile and checkpoint manifest were unchanged. No runtime code was changed in
this verification pass; ignored `frontend/dist/` was regenerated. Original
isolated checkpoints passed in the preceding lifecycle increment; they were not
rerun for this documentation-only pass.

## Server-owned models and prompts

| Purpose | Location | Configuration |
| --- | --- | --- |
| Spoken interaction | [settings.py](../backend/app/features/voice/settings.py), MODEL | gpt-live-1; fixed marin voice; bounded current-chat input or []; store:false; no tools. |
| Delegated Responses | settings.py, VoiceSettings.from_environment / session_payload | VOICE_BACKEND_MODEL from the backend process, with no default. Both it and OPENAI_API_KEY are needed for configured status. No actual environment value or provider access was checked in this pass. |
| Live prompt | [prompts.py](../backend/app/features/voice/prompts.py), LIVE_INSTRUCTIONS | Flexible listening/answering; brief echoes, fuller reflections and selective summaries; at most one useful question; backchannels, interruption/refusal, minimum safety and SpawnThinking guidance. |
| Delegated prompt | prompts.py, BACKEND_INSTRUCTIONS | Same conversation/safety core plus reviewed scope, permission, age-sensitive wording, context/privacy limits and nuanced cases; no diagnosis, therapy/treatment/medical advice, monitoring or unsupplied records. |
| Independent typed replies | [provider.py](../backend/app/features/voice/provider.py), reply_text | Same server backend model and BACKEND_INSTRUCTIONS, plus: “For this typed turn, reply to the user in text, following the conversation policy above.” |

The browser supplies no model, prompt, key, tools, provider URL or policy. Emergency
and navigation remain application-owned, independent of any model/request outcome.
The earlier verification inspected prompts without changing them. The subsequent
research-informed prompt revision is documented in [the readable system
prompt](chat-system-prompt.md). No prompt behavior has been validated against a
live model, and an existing running backend/session was not restarted by that revision.

## Manual preflight — before the stopwatch

Perform this section yourself only when ready to authorize the one paid attempt.
No step below has been executed by Codex. A live session can delegate multiple
Responses requests; one conversation does not mean exactly one model call.
Keep the assignment's host-owned call budget (no more than fifty model calls per
session); this UI does not enforce/count delegated requests. No text sends or
second voice attempt are part of this procedure.

1. Ensure the intended backend terminal has OPENAI_API_KEY and an explicitly
   selected, authorized VOICE_BACKEND_MODEL. Keep credentials out of the browser
   and evidence. If they are in the repository-root `.env`, add `--env-file .env`
   to the Uvicorn command below; the app does not auto-load that file. The existing
   project environment already supports this flag. Do not install dependencies.
2. From the repository root, manually start the existing build on localhost:

   ```sh
   backend/.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
   ```

   If this exact app is already served there, use it; do not stop an unrelated
   process to take the port. The production build has already been generated.
3. In a separate terminal, optionally verify local configuration without a paid
   provider request:

   ```sh
   curl --fail --silent --show-error http://127.0.0.1:8000/api/voice/config
   ```

   Expect `{"status":"configured","duration_seconds":300}`. Otherwise stop and
   configure the backend; do not select Start. Configured checks only presence/
   shape, not provider credit, model availability, key validity or access.
4. Open `http://127.0.0.1:8000/`, ensure it loads the current production build and
   choose Support chat. Do not click Send. Confirm Emergency and End chat are
   visible, state is Closed, and this site has no active microphone capture.
   Prepare headphones/speakers and a stopwatch. Keep Chat visible; switching tabs
   or opening a panel intentionally ends voice. Permission is requested only by
   selecting Start voice. Do not open Emergency during this same conversation;
   its cleanup is already mocked, and no resource call should be placed.

## One attempt: finish at 55 seconds or earlier

Use stopwatch time from the first Start click, including permission/connection
delays. End at 45 seconds at the latest; do not wait for the app's 300s limit.
If a step cannot fit, record it as untested and End without another attempt.

| Stopwatch | Exact action | Expected observation — not yet observed |
| --- | --- | --- |
| 0–15s | Start the stopwatch and click the microphone / Start voice **once**. Allow microphone access promptly. | Permission → Connecting → Active. No speech is transmitted until matching session.started. If not Active by 15s, select Cancel voice setup, verify capture stops, and mark the attempt aborted. Do not retry. |
| 15–25s | Once Active, say: “This is a fictional software test. Greet me in two short sentences.” As soon as the assistant starts speaking, interrupt: “Please stop and just say hello.” If Enable assistant audio appears, click it once, staying within this time budget. | Audible reply and approximate user/assistant caption bubbles. The assistant yields to the interruption and follows the changed request. If it finishes before interruption or cannot be heard, mark interruption untested/failed; do not claim a pass or extend the deadline. |
| 25–30s | Click Mute once. Say: “Muted microphone test.” | State Muted; no new microphone audio should reach the assistant. Assistant playback may continue, session stays open and billing continues. Capture indicator can remain on because tracks are disabled, not released. Previously queued captions can still arrive. |
| 30–40s | Click Unmute once. Say: “I’m back. Acknowledge briefly.” | State Active and a brief audible acknowledgment. Do not ask for an activity or send typed text. |
| 40–45s | Click End voice once, regardless of whether the assistant is still speaking. | Microphone capture and assistant playback stop immediately. Closing → Closed within about 2s. Missing session.closed is reported as finalization unconfirmed; local Closed alone is not proof of provider termination. |
| 45–55s | Check the site's **active microphone-use** indicator has stopped, and assistant audio remains silent. Stop the stopwatch. | Record the active-use indicator off separately from retained site permission (Allow may remain). If available, inspect the browser's per-site capture status; another app can keep the OS-wide indicator lit. If this site still captures, close this prototype tab immediately and record a release failure. Do not start again to check it. |

At most one connection attempt is authorized by this checklist. If any error occurs,
End/cancel immediately, verify microphone release and mark the remaining steps
untested. If the deadline arrives in Connecting, cancel setup; a late ID will be
handled by the cleanup path. Under 60 seconds is a manual local test target, not
a guaranteed provider expiry or billing cap. Do not treat fallback HTTP success
as confirmed final usage; no automatic retry or cost reconciliation is implemented.

Record only date/browser, elapsed seconds, step pass/fail/untested, microphone
release observed yes/no, and whether finalization was confirmed or unconfirmed.
Do not record audio, copy transcripts, credentials, SDP, HAR or provider bodies.
This document intentionally contains no claimed live result.

## Cleanup, persistence and remaining limits

End stops all local tracks, stops remote tracks, pauses/detaches the audio element,
clears timers/listeners, and closes channel/peer after a 2s maximum acknowledgment
wait. Unmount/navigation, hidden/page exit and Emergency release immediately;
duration cleanup ends voice only. Already-sent creation remains readable within
15s so a late ID can receive one 5s-bounded keepalive cleanup request; stale SDP
never restores UI. FastAPI attempts cleanup for an observed disconnected requester.
The provider hangup adapter has a 3s I/O timeout and no retry/redirects.

Each new voice transport starts with the current chat's bounded history or input:[].
Old captions stay visible until the chat ends.
Messages/captions/drafts stay in memory and clear on leaving chat. Neither audio
nor transcripts nor typed messages are written to SQLite/local storage/offline
API caches. Only validated IDs/close outcomes are tracked in backend process
memory. Context in either mode includes recent visible voice captions and completed
typed messages; failed/pending typed messages are excluded. store:false is a retrieval setting, not a promise about
general provider retention, training or fully local processing.

Still unverified: actual browser permission/autoplay, ICE/NAT/provider access,
speech quality, spoken interruption/backchannels, caption accuracy, prompt/scope
adherence and Responses delegation, device release and live finalization/billing.
The [hangup reference](https://developers.openai.com/api/reference/resources/live/subresources/sessions/methods/hangup)
describes SIP; using it for orphaned WebRTC sessions remains an explicit unverified
assumption. The [management guide](https://developers.openai.com/api/docs/guides/live-conversations)
requires session.closed to confirm finalization. Crashes, suspension, request
timeouts/disconnect races and unknown session IDs can defeat cleanup; no hard
provider expiry/cost enforcement exists. The process ledger is lost on restart,
has no authentication and needs bounded retention/multiworker handling before
broader use. No clinical or deployment-readiness result is established.

## Changes in this verification pass

Created this document; linked it from the root README and chat README; appended
observed results to AI-USE.md and docs/evidence-log.md and updated the current
handoff. Application code, tests, models/prompts, dependencies, SQLite schema,
checkpoint scopes and prior dirty files were preserved. No server was started,
no real microphone/provider/resource call occurred, and no Git staging/commit/push
was performed. Ignored build output was regenerated by the requested build.
