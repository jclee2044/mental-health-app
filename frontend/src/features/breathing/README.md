# Guided breathing module — third commit

Owns the fixed browser clock, countdown, pacing view, circle motion, recorded human inhale/exhale cues played with Web Audio, mute, reduced motion, pause/end/repeat, retryable session saves, session history, styles and tests. Registration is `index.js`; the shell discovers it automatically. It imports shared UI/date utilities and the HTTP client, never emotion code.

Backend counterpart: `backend/app/features/breathing/`. CONTRACT.md defines fixed-pattern session records. The browser handles timing; no network request paces a phase. SQLite saving remains outside the active exercise loop.

Before extraction, observed browser runs completed six cycles in 63.0s including the countdown: instruction-to-finish was 63.1s for an immediate start, then 64.0s on a run with media and pauses excluded. Ready-screen reading assumptions and actual delays matter; these are observed runs, not universal timing guarantees. Pauses, Emergency, mute, reduced motion and end/repeat were checked. DOM diagnostics showed matching active audio and circle phases, with AudioContext running; actual speaker loudness/quality is not established. Node tests check fixed phase boundaries, drift, pause/end, resumed sound offset and audio cleanup with a mocked audio context. Backend tests check durations and persistent/idempotent records. Extraction and isolated checkpoint results are recorded separately.

AI use: Codex authored the module using the user's 4/6/six-cycle requirements and requested Headspace-inspired presentation. The user chose beerre’s CC0 human-breath recording after auditioning two candidates. Human recording cuts replace the initial synthesized noise: the user identified inhale at source 7–10s and confirmed the retained 25.35–28.90s clip as an exhale. At the user’s request, the three-second inhale plays at 75% speed to fill four seconds, lowering pitch slightly; the exhale plays at 71% speed for five seconds, with the final second quiet. An initial overlap-add stretch was removed after the user reported an unnatural sound. See `assets/CREDITS.md` for provenance, preparation and listening limits. No Headspace assets, microphone, speech service or external model is used. Tools: existing project runtimes, Node built-in test runner, pytest and CUA browser checks. No dependencies added. Exact served model identifier is unavailable. Root AI-USE/evidence notes cover the full session.

Limits: failed session records remain only in memory until Retry succeeds; reload/close can lose them. A forced browser exit can prevent saving an ended session. Session deletion and retention controls remain TODOs. No clinical or monitoring claims.


## Hold interaction — October 27, 2026

The user now requires holding the circle through the countdown and six cycles.
A primary mouse/touch/pen press or held Space/Enter begins the exercise; release,
pointer cancellation/lost capture, window blur, hidden page or Emergency ends an
unfinished session and returns Home through the existing save path. Releasing
after completion retains the completed result. Starting/repeating requires a
fresh hold; plain clicks cannot bypass it. Pointer capture keeps the changing
circle size from interrupting a hold. Pause/Resume remain available while the
pointer stays held (for example using another finger); releasing while paused
ends the session. Keyboard focus loss ends a keyboard hold. Mute, reduced motion,
fixed steps and independent Emergency remain in place. No API/schema change.

Observed checks: Node tests cover early release, full completion, repeating,
competing inputs, key repeat, cancellation, paused release and focus loss.
Frontend tests, production build and targeted non-mutating ESLint passed.
TODO: verify actual mouse/touch/pen and assistive-technology behavior in browsers;
these mocked checks do not establish physical-device usability or audio quality.


### Breathing text and remaining time — October 27, 2026

User requested clearer start instructions and time remaining. Updated
BreathingView.vue and styles.css with prominent “Tap and hold” text, an in-circle
start label, release-to-end explanation, a 3-second preparation explanation,
63-second total and seconds-remaining timer (including countdown, frozen during
pauses), plus completion/release wording and keyboard guidance. Existing pace
and hold behavior remain. No dependencies or contracts changed.
Commands/checks: npm --prefix frontend run build; npm --prefix frontend test
(72 passing); targeted non-mutating ESLint; git diff --check. CUA reloaded the
local app and opened Guided breathing; accessibility text and screenshot confirm
new ready-state instructions, 63-second total and visible Emergency. Screenshot:
docs/evidence/breathing-hold-instructions.png. Active countdown/full-duration
browser run and physical touch/assistive-technology checks remain unverified.
No provider/microphone/call actions. AI assistance: Codex authored the copy,
remaining-time computation and CSS using existing project tools.


### Breathing timer correction — October 27, 2026

User requested removing the visible keyboard note and excluding preparation from
time remaining. Codex updated BreathingView.vue: 60 seconds of breathing remains
during the separate 3-second countdown, then decreases during the fixed six
cycles. The underlying 63-second sequence and duration records remain accurate.
Keyboard hold support remains; only its visible explanatory paragraph was removed.
Checks: npm --prefix frontend run build, npm --prefix frontend test (72 passed),
targeted non-mutating ESLint and git diff --check passed. CUA reload confirmed
60-second ready display and removed paragraph; screenshot is
 docs/evidence/breathing-active-time.png. Active full-duration browser run remains
unverified. No dependencies/API changes or live model/microphone/call actions.

November 2 completion audio: the approved softened harp plays once after all six
cycles, independently of session saving. The existing Sound control mutes both
breath and completion audio. Early release remains silent. A fresh hold/repeat
arms a fresh cue; mute, overlay/hidden/unmount invalidate queued playback and
stop active sound. The fixed sequence clock still completes at 63s; the 4.1012s
notification tail does not hold the UI or delay recording. Including that tail
would nominally take 67.1012s from countdown start (calculation, not a new browser
timing observation; entry/reading and application delays remain separate).
Real-SFC mocked handlers verify early release and one full-cycle completion;
shared player mocks check cancellation, mute and decode failure. Source/license:
../../components/completion-sound/CREDITS.md. No real speaker/device check yet.


### November 2, 2026 — breathing early-end screen and open tones

User selected audition 10 (descending open tones) for early termination.
Release/End now stops the clock and breath audio, records once through the
existing retryable save path, and stays on “Breathing exercise ended.” with
“It’s okay to stop whenever you need. Take things at your own pace.” and a
Return home button. Emergency remains in the shell. No completion penalty,
required response or forced navigation. The exact 4.4s original synthesized
audition is bundled under breathing/assets/open-tones.wav; the existing harp
remains exclusive to completed six-cycle breathing and successful emotion saves.
The shared optional cue loader accepts a feature-owned bundled asset. Mute,
interruptions/hidden state, window blur and unmount invalidate pending sound;
turning sound back on at the ending screen does not replay it. Sequence timing
and API/storage contracts are unchanged.

Observed: 110 frontend tests passed, including real-SFC mocked early ending,
no Home navigation, duplicate protection, full completion and paused focus loss.
Existing shared-player tests cover mute/interruption/decode failures. Production
build, targeted non-mutating ESLint and all three cumulative checkpoint builds/
tests passed. Vite large-bundle and existing Starlette/httpx warnings remain.
Commands: npm --prefix frontend test; npm --prefix frontend run build; from
frontend, npm exec --offline -- eslint src/features/breathing/BreathingView.vue
src/features/breathing/tests/completion.test.js
src/components/completion-sound/useCompletionSound.js --no-cache;
backend/.venv/bin/python scripts/verify_checkpoints.py; git diff --check.

Local mock demo started via scripts/serve_submission_demo.py --port 8014
(after sandbox socket denial, approved escalation succeeded). CUA keyboard
press/release verified the ended message, Return home, Emergency, saved-session
notice and actual Home navigation. Screenshot: docs/evidence/breathing-ended-open-tones.png.
No provider/microphone/call actions. Speaker quality, physical touch-device
behavior and screen-reader announcement remain unverified. No dependencies,
staging or commits. Codex authored the code/copy and used existing Vue/Node/
Python/CUA tools; exact served coding-model identifier is unavailable.


### November 2, 2026 — persistent global output-sound control

Breathing now consumes the shell’s shared sound preference; its local sound
button is removed. Global mute stops breath audio and cancels pending/playing
completion/ending cues. Unmute can restore current phase audio, without replaying
a past cue. The approved open-tones early-end screen remains unchanged.

Observed: 113 frontend tests, production build, targeted ESLint and all three
cumulative checkpoints passed. Browser checks verified persisted mute and
controls in overlays; voice playback was mocked/DOM-verified, without real
microphone or provider calls. Full commands and limits: docs/evidence-log.md.

## Warm keys completion selection — November 2, 2026

The user replaced breathing completion's harp with the original warm keys
audition; emotion saves retain the softened harp. assets/warm-keys.wav is an
exact copy of docs/evidence/completion-sounds/01-warm-keys.wav, synthesized with
Python stdlib by Codex in this chat: G3 C4 D4 G4, 4.2s, unchanged from the audition.
No third-party samples. Reproduce with the audition folder's render.py.
Only the full-completion cue changes; the global output-sound control and the
separate descending early-end cue retain their behavior. Nominal countdown +
exercise + warm-keys tail is 67.2s (calculation, not a new browser measurement).
