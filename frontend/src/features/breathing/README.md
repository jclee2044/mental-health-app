# Guided breathing module — third commit

Owns the fixed browser clock, countdown, pacing view, circle motion, original Web Audio inhale/exhale cues, mute, reduced motion, pause/end/repeat, retryable session saves, session history, styles and tests. Registration is `index.js`; the shell discovers it automatically. It imports shared UI/date utilities and the HTTP client, never emotion code.

Backend counterpart: `backend/app/features/breathing/`. CONTRACT.md defines fixed-pattern session records. The browser handles timing; no network request paces a phase. SQLite saving remains outside the active exercise loop.

Before extraction, observed browser runs completed six cycles in 63.0s including the countdown: instruction-to-finish was 63.1s for an immediate start, then 64.0s on a run with media and pauses excluded. Ready-screen reading assumptions and actual delays matter; these are observed runs, not universal timing guarantees. Pauses, Emergency, mute, reduced motion and end/repeat were checked. DOM diagnostics showed matching active audio and circle phases, with AudioContext running; actual speaker loudness/quality is not established. Node tests check fixed phase boundaries, drift, pause/end, resumed sound offset and audio cleanup with a mocked audio context. Backend tests check durations and persistent/idempotent records. Extraction and isolated checkpoint results are recorded separately.

AI use: Codex authored the module using the user's 4/6/six-cycle requirements and requested Headspace-inspired presentation. Audio is original synthesized noise shaped by filters/envelopes; no Headspace assets, recordings, microphone, speech or external model is used. Tools: existing project runtimes, Node built-in test runner, pytest and CUA browser checks. No dependencies added. Exact served model identifier is unavailable. Root AI-USE/evidence notes cover the full session.

Limits: failed session records remain only in memory until Retry succeeds; reload/close can lose them. A forced browser exit can prevent saving an ended session. Session deletion and retention controls remain TODOs. No clinical or monitoring claims.
