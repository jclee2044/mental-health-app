# Current project handoff

## Current state

Part 3.1 Research and Design. Read [AGENTS.md](../AGENTS.md), [README](../README.md), and [the assignment](../docs/assignment-description.md) before work. Detailed decisions are in [design notes](../docs/design-notes.md), sources in [research notes](../docs/research-notes.md), and work evidence in [the evidence log](../docs/evidence-log.md).

[report.md](../report.md) is the current submission draft. It includes the simple nine-node Mermaid flow, all ten R/D findings, references, and the supplied [early mockup](../docs/early-mockup.png). Repository/commit fields remain placeholders. No app-specific interface, backend, API integration, SQLite records, or live chat has been implemented. The prior scaffold verification is recorded in README. Git identity and the initial commit still require their documented checkpoint and approval.

## User writing preferences

- Prioritize the user's own phrasing, content, first-person voice, and tone; requested balance is roughly 75% user material with AI support, not a measured authorship claim.
- Keep feature descriptions together in Scope. Retain Research notes, Design considerations with R/D findings, a simple Flow diagram, Early mock up, and Open questions.
- No feature-by-feature subsections, complex flowchart, mockup table, or NLP-evidence paragraph in the report.
- Latest report is 1,619 words, about 74% of the preceding 2,198-word draft. Five requested questions and the submission-reminder closing paragraph were removed. The five remaining questions concern affective/adaptive UI, anxiety/stress metrics, baselines, eye-tracking consent/reliability, and slider/graph effort.

## Confirmed design

- Phone layout: brief skippable logo entry, then three wide buttons stacked vertically: Emotion log, Guided breathing, Support chat. No required check-in before other activities.
- Logging requires feeling, user-defined color, and a point on a separate pleasantness/energy graph; narrative text is optional. Calendar/day views support multiple entries and edit/delete.
- Breathing: Begin, 3–2–1, six four-in/six-out cycles. Fixed steps, Pause/End, reduced motion, and persistent Help. Sixty seconds of breathing; roughly 75-second instruction-to-completion budget needs actual measurement. No forced exit.
- Open-ended chat with visible End chat, secondary reply settings/history, curated retrieval context, and the user's interest in CBT plus the fourteen Sleight of Mouth patterns. Do not turn it into a mandatory timed conversation.
- User-controlled appearance; adaptive UI remains unresolved. Eye tracking, behavioral baselines, other passive metrics, voice, additional breathing patterns, and a vector database are deferred.
- Vue presentation separate from request code; framework-free Python logic separate from FastAPI routes; SQLite persistence. Define the JSON request/response/error contract before integration. Provider, corpus, privacy/transmission, retention, and schema details remain in the design notes; their removal from the report's question list did not supply implementation decisions.
- Fictional coursework only, localhost, no diagnosis/therapy/monitoring claims. Help and exits must work independently of the model, classifier, and request success. Preserve assignment timing and later testing boundaries.

## Mockup evidence

The user generated `docs/early-mockup.png` with ChatGPT image generation, not Figma Make. The unused tool-specific prompt was removed; do not recreate it. The image is embedded with a repository-relative path so it travels with the repository. It was visually inspected, not modified.

The board shows the main activities and secondary states. The Help panel still says the country/number is pending, while the user confirmed U.S. resources and the design notes record the verified crisis-counseling/emergency-services distinction. The graph also says its axes are provisional, although pleasantness/energy are confirmed. Reconcile those annotations when refining the interface; do not treat the image as a new requirements change. Static imagery does not verify navigation, animation, persistence, accessibility, or failure handling.

## Next work and verification

Follow the next user request rather than automatically starting implementation. For implementation, resolve genuinely blocking choices, define the contract/schema, then build the bounded experience and independent Help. Later milestones need actual timing, persistence, exits/failures, fictional evaluation cases, and clearly separated mocked/live-model evidence. Do not install dependencies or expand scope without explaining the need.

This update changes documentation only. Inspection used `cat`, `rg --files`, `ls -la handoffs`, and the local image viewer; edits used a shell heredoc and `apply_patch`. Project-owned Python checks report length, retained sections/findings, removed questions/paragraph, image existence/signature, and local links. No new application checks, dependencies, processes, calls, commits, or publishing occurred. Mermaid rendering remains unverified.
