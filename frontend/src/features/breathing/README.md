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
