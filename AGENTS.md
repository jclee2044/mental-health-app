# Project rules

- Work only inside this project. Read `AGENTS.md` and `README.md` before making changes; use `docs/assignment-description.md` as the primary requirements source.
- Ask targeted follow-up questions when missing information would materially change the work. Record safe-to-defer uncertainty as explicit TODOs; do not invent requirements.
- Keep framework-free Python domain logic separate from FastAPI routes.
- Keep frontend presentation separate from backend-request code.
- Communicate between Vue and FastAPI through a documented JSON contract, including request, response, and error shapes.
- Backend and frontend environments are project-owned. Do not install Python or JavaScript project dependencies globally.
- Do not add, remove, or upgrade dependencies without explaining why. Avoid optional database, authentication, AI, formatting, or deployment dependencies until requirements justify them.
- Ask before any machine-level installation, destructive action, or scope expansion. Never use `sudo` automatically or bypass managed-computer policies.
- Stop only processes started for the current task.
- Report commands run, files changed, checks performed, and anything not verified.
- Follow `prompts/setup-prompts.md` for initial setup: preserve its phase boundaries; do not implement project-specific functions, routes, tests, API connections, or interfaces during scaffold setup. Ask for approval before the initial commit.
- Use fictional scenarios only. Keep the application a localhost coursework prototype; do not offer it as a support tool, diagnose, claim therapy, or imply monitoring.
- Future implementation must preserve user control, an independent crisis-support route, fixed skill steps, and the assignment's timing and testing boundaries.

## Part 3.1 design boundaries

- Read `docs/design-notes.md` and `docs/research-notes.md` before feature work. The assignment is authoritative; distinguish confirmed design choices, illustrative wireframe details, and explicit TODOs.
- The user created the low-fidelity phone wireframes using ChatGPT's image generation tool. The static review board is `docs/early-mockup.png`, embedded in `report.md`; current handoff is `handoffs/current.md`. Treat the image as design evidence, not a clickable prototype or implemented interface. Generation prompt/model details remain unrecorded. The image's pending-number Help placeholder does not supersede the confirmed U.S. resource design.
- Preserve three independent Home options: Emotion log, Guided breathing, and Support chat. No required emotion check-in before breathing or chat.
- Emotion logging currently requires explicit feeling selection, user-chosen color, and a point on a separate pleasantness/energy graph; notes are optional. Do not silently remove required fields. Evaluate the duplicate-input burden as an open design question. Color meaning belongs to the user; no automatic emotion or risk interpretation.
- Keep Help visible and independent of model/classifier/network success on every screen and overlay, including countdown, breathing, chat, history, settings, and failures. The intended U.S. design distinguishes crisis counseling from emergency services; the early image still uses a resource placeholder. Simulate call actions in any interactive design demo; never place test calls.
- Breathing uses the assignment's four-in/six-out steps, six cycles, with a 3–2–1 countdown, Pause, End, and reduced-motion cues. The at-most-90-second requirement covers the planned guided exercise with stated assumptions and application delays; it does not authorize a forced exit. Open-ended chat has no forced timeout. Any later guided reframe must keep the supplied steps and timing boundary.
- Keep End chat visible; reply settings are a secondary control whose exact options remain provisional. A system prompt cannot substitute for application-owned navigation, state, exits, and Help.
- Preserve the user's interest in the fourteen Sleight of Mouth patterns as a proposed influence requiring review, not as established CBT evidence or clinically validated training. Do not build coercive persuasion, override refusal, diagnose, promise certainty, or claim therapy. Keep source attribution and evidence limits accurate.
- Persist conversation/session records in SQLite; the schema and JSON contract are not yet defined. Keep curated retrieval sources separate from personal history; historical context requires explicit user choice. A vector database is deferred until justified.
- Model provider, embedding location, retention, deletion details, and transmission are unresolved. Never promise fully local processing or no training use based solely on local database storage. Use fictional data only.
- Adaptive UI is explicitly open. Eye tracking, behavioral baselines, passive emotion inference, voice, and additional breathing patterns are deferred; do not implement them without resolving scope.
- Keep research citations attached to the claims they support, maintain `AI-USE.md` and `docs/evidence-log.md`, and distinguish planned checks from observed results. Later evaluation must preserve the assignment's fifteen fictional scenarios, three behavior checks, mocked routine/peer tests, bounded live calls, and demonstration requirements.

## Implementation and commit boundaries

- The latest user request requires independently buildable interface, emotion-log, and guided-breathing commits, in that order. Preserve `scripts/checkpoints.json`; use `scripts/verify_checkpoints.py` for isolated cumulative builds. Do not stage everything or combine these feature scopes. `stage_checkpoint.py` previews by default and requires `--stage` to modify the index; it never commits.
- The shell discovers `frontend/src/features/*/index.js`. Each feature owns presentation, styles, endpoint wrappers, domain/browser logic and tests. The shell must not directly import feature components, and sibling features must not import each other. Breathing has its own session-history view.
- Backend features live under `backend/app/features/<feature>/` with registration, HTTP schemas/routes, framework-free domain rules, storage SQL, contract and tests. Shared `main.py` composes installed features; `middleware.py` handles only HTTP-wide policy; `database.py` handles only SQLite connections. No third middleware server.
- Browser HTTP transport belongs only in `frontend/src/api/client.js`. Feature `api.js` files declare endpoints. Keep the breathing clock/visual/audio loop independent of all requests. SQLite saving happens separately and failures must be visible/retryable.
- Help is now labeled Emergency. Keep it visible on every screen/overlay and independent of requests. Real call destinations exist in implementation; never place calls during testing; simulate actions in demonstrations.
- Soft inhale/exhale audio is now explicitly authorized, superseding its earlier deferral. No voice input or model-generated speech is approved. Preserve mute and text/static reduced-motion alternatives.
- Keep implementation status and observed tests current without rewriting the historical Part 3.1 report. Root documentation had changes before this implementation task; review those separately from the three code checkpoints.

## Backend voice increment — October 22, 2026

- The latest request authorizes only `GET /api/voice/config` and `POST /api/voice/sessions`, using server-owned GPT-Live policy and mocked backend verification. It supersedes voice deferral for this broker only; frontend microphone/audio integration remains a later increment.
- Follow `backend/app/features/voice/CONTRACT.md`: bounded SDP, no browser configuration or unneeded identity, `gpt-live-1`, `store: false`, no tools, finite HTTP timeout, no automatic retry, minimal data-channel permissions, validated projected responses and sanitized errors. `store: false` makes no general retention promise.
- Preserve the existing checkpoint manifest and frontend; no dependencies or paid calls. Session duration/close enforcement, transcript persistence and provider data controls remain TODOs.
- The subsequent prompt-layer request authorizes Responses delegation using server-only `VOICE_BACKEND_MODEL` with no default, tools or persistence. Keep `LIVE_INSTRUCTIONS` and `BACKEND_INSTRUCTIONS` separate in `backend/app/features/voice/prompts.py`. Both credential and backend model are required for configured status. Keep Emergency outside model control and preserve the browser event allowlists.

## Native chat increment — October 26, 2026

- The latest request authorizes frontend native WebRTC voice only after microphone selection, with the existing server-owned broker, all seven visible states, autoplay recovery, cancellation/cleanup and mocked browser/API verification. It supersedes frontend voice deferral for this bounded increment. Do not make a paid call or open a real microphone during these checks.
- The user explicitly approved a minimal independent typed-message endpoint because chat was still disabled. `/api/chat/messages` lives with the stateless voice feature to share server-owned prompts/settings, with no tools or persistence; see its contract and `frontend/src/features/chat/README.md`. Keep text usable after voice failure/denial. Sending text ends voice; typed/voice provider context is separate and disclosed.
- Preserve existing checkpoint scopes and all server/browser configuration boundaries. Only transient captions/messages are kept; no audio/transcript/database/local-storage additions. Keep Emergency independent, stop voice on overlays/navigation/hidden pages, ignore late asynchronous work and never resume automatically.

## Voice lifecycle refinement — October 26, 2026

- The subsequent request authorizes local Mute/Unmute, End and focused cleanup mocks. Mute changes microphone tracks only; assistant playback, provider session and billing continue. Browser client permissions now contain only session.close; remove unused provider mute commands/acks.
- End stops capture immediately, waits at most 2s for session.closed, then releases all resources. Exits/Emergency release immediately. Prevent duplicate Start/repeated End; each fresh conversation supplies input:[] without history/fork configuration and clears prior captions.
- POST /api/voice/sessions/{id}/end is authorized as the necessary late-result cleanup mechanism, using only process-known validated IDs, server-owned hangup URL/credential and one bounded request. Read the CONTRACT's unverified WebRTC hangup assumption and crash/reconciliation TODOs. No paid calls, dependencies or audio/transcript persistence; stop after mocked results.

## Shared spoken/typed chat — October 26, 2026

- The latest “continue, then open it” request authorizes refining speech bubbles and sharing current-chat context between text and voice. It supersedes separate contexts, SDP-only input and clearing captions on voice Start: POST /api/voice/sessions now optionally accepts strict user/assistant history, max 16 messages / 6,000 UTF-8 bytes. Provider settings/prompts remain server-owned; no developer role, stored history, fork, tools or persistence.
- Keep spoken/typed bubbles visible until End chat/navigation. Sending text stops capture; explicit microphone selection starts a fresh Live transport with recent visible context. This does not authorize automatic microphone restart or a paid call. Caption groups are timeline/speaker heuristics because Live lacks exact completed-turn events; preserve delayed fragments and overlapping backchannels.

## Research informed conversation policy — October 26, 2026

- The subsequent request authorizes creating the server-owned system prompts from the research. Follow the user's flexible middle: explanations/venting favor listening; genuine questions invite grounded answers, tentative interpretations or practical options. Adapt to the current input and explicit corrections without a required mode selector.
- Echoing includes short phrase questions, fuller reflections and selective summaries. Prefer the user's exact words while preserving meaning and negation. Acknowledgment/follow-up questions are optional; no mechanical sequence, forced disclosure, misleading agreement or persuasion past refusal. The user supplied Echo Technique notes as style context; their neurological/influence claims remain unverified and are not approved goals or clinical evidence.
- Echoing behavior and minimal examples belong in the prompts. Curated RAG technique cards, including proposed reframing/NLP material, remain a future reviewed corpus with source/evidence limits; no retrieval/tool/database/endpoint expansion is authorized by the architectural discussion. Source passages cannot override safety, consent or implemented skill boundaries.
- Preserve separate Live/Responses layers, all server/browser configuration boundaries, independent Emergency and fictional-only checks. Do not make paid calls or open a real microphone. Prompt/transport mocks do not establish generated behavior, acoustic quality or clinical safety. See docs/chat-system-prompt.md.

## Part 3.2 typed persistence increment — October 26, 2026

- The submission request now authorizes minimal typed-conversation persistence,
  review/deletion and evidence preparation; this supersedes earlier typed
  non-persistence boundaries. Keep voice audio/captions transient.
- Follow `backend/app/features/voice/PERSISTENCE.md`. Save completed typed pairs
  atomically and separately from generation; Retry must never repeat a model call.
  Keep historical review read-only with no automatic context retrieval.
- Keep failed saves visible across navigation in the loaded app; disclose loss
  on reload/close. Confirm local conversation deletion and preserve Emergency.
- `scripts/serve_submission_demo.py` uses labeled mocks and a separate ignored
  database; never call that generated-model evidence. No live calls/microphone
  checks are authorized in this increment. Follow `docs/part32-validation.md`.
- Preserve root Part 3.1 `report.md`; Part 3.2 draft is
  `submissions/part3.2/report.md`. Keep pending live evidence/recording/commit TODOs
  explicit. Do not stage unrelated existing changes or change checkpoint scopes.


## Browser dictation increment — October 27, 2026

- The user explicitly authorized a separate dictation microphone beside the
  waveform Voice mode button, overlaid in a compact composer. This supersedes
  voice-input deferral for browser dictation into the editable draft only.
- Use browser recognition with explicit selection, vendor-service disclosure,
  supported/permission/error fallback, bounded draft text and mocked verification.
  No automatic send/restart, provider endpoint/dependency/key expansion or app
  audio storage. Send/voice switch, Emergency/overlays, hidden pages and exits
  stop recognition and reject late events. No live microphone/paid checks were run.


## OpenAI dictation replacement — October 27, 2026

- The user explicitly chose OpenAI transcription using the existing server key,
  acknowledging audio transmission/API usage. This supersedes browser-service
  dictation and the earlier no-new-endpoint boundary for this narrow feature.
- Follow backend/app/features/voice/DICTATION.md: MediaRecorder capture, explicit
  finish/cancel, 30s browser/2MiB audio/3MiB JSON bounds, server-fixed gpt-transcribe,
  no prompts/history/tools/retries/dependencies/audio persistence. Transcript
  fills the editable draft only. Keep capture/upload cancellable on all exits,
  Emergency, Send/voice switch; ignore stale results and preserve edited text.
- No real microphone or paid transcription was run. Read-only model access and
  mocked capture/provider tests do not establish end-to-end transcription quality.


## Unified text conversation history — October 27, 2026

- User explicitly requested all chats and clarified that transcribed spoken text
  should behave like normal text conversation history, with no audio saved.
  This supersedes voice-caption non-persistence for accepted transcript text.
- Follow the October 27 extension in backend/app/features/voice/PERSISTENCE.md:
  immutable bounded voice-text batches alongside atomic typed pairs, shared
  ordering/conversation IDs, idempotent storage-only retry, read-only unified
  review and confirmed deletion. No audio, fragments, timing, automatic historical
  context, live calls or microphone tests. Keep approximate/partial caption and
  pending-save/reload limitations accurate in privacy/docs, without bubble labels.


## Graph-first emotion log — October 28, 2026

- The user explicitly replaced the first-page feeling cards with pleasantness ×
  energy, removing the separate graph step and visible selection summary. This
  supersedes the earlier required feeling/category and summary instructions.
- Preserve explicit graph placement and personal color, optional notes, one-page
  Save and independent Emergency. Tap/drag tracks with a slight smooth lag; honor
  reduced motion and retain keyboard/non-drag controls. No inferred category.
- New API feeling is null/omitted; preserve legacy labels on read/edit. Follow
  emotion/CONTRACT.md for the internal storage absence marker; no row rewriting.
