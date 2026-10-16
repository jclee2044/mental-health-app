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
