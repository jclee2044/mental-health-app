# Part 3.1 design notes

Design decisions as of October 15, 2026. The [assignment](assignment-description.md) is the requirements source; [research notes](research-notes.md) separate outside evidence from project interpretations. The user created the [early mockup](early-mockup.png) using ChatGPT's image generation tool. This static review board has been visually inspected and embedded in [the report](../report.md). The repository contains the existing scaffold, not this application. See [the current handoff](../handoffs/current.md) for continuation notes.

## Purpose and imagined audience

The imagined audience is someone experiencing anxiety, intrusive thoughts, or other emotional difficulties who may face financial barriers to therapy or feel apprehensive about seeking it. These motivations inform low-effort interaction and nonjudgmental language. They do not make this prototype a substitute for a therapist. Age-specific behavior is unresolved; do not infer suitability for minors.

The product concept has three independently chosen activities: emotion logging, guided breathing, and open-ended support chat. Actual use is limited to fictional coursework scenarios on localhost. No therapy, diagnosis, clinical effectiveness, or monitoring claims. Do not recruit or test with people who are distressed.

## Confirmed scope and illustrative details

| Area | Confirmed decision | Still illustrative or unresolved |
| --- | --- | --- |
| Format | Phone interface; static low-fidelity wireframes created with ChatGPT image generation | Name and branding remain placeholders; static image reviewed |
| Entry | Logo block on a mostly blank screen; about one-second fade; skip; reduced motion | Exact fade duration |
| Home | Three wide buttons stacked vertically; top-right Help | Final wording and spacing |
| Log | Required feeling selection, personal color, and point on a separate 2D graph; optional text | Feeling-slider labels; duplicate effort between slider and graph |
| Graph | Horizontal pleasantness; vertical energy | Coordinate range and granularity |
| History | Calendar; multiple logs/day; latest color; daily details; edit/delete | Final calendar navigation |
| Breathing | Begin, 3–2–1 countdown, four-in/six-out, six cycles; pause/end | Measured timing and browser behavior |
| Chat | Open-ended; bare-bones wireframe; visible End chat and Help; reply-settings button | Exact settings, provider, content policy, and allowed pattern subset |
| Help | United States; immediate call-options panel | Eventual device call-link behavior |
| Personalization | Optional accent color, text size, reduced motion; usable defaults | Adaptive UI explicitly remains open |
| Storage | SQLite for persistent records; separate history views and deletion | Schema, retention, and context-selection details |
| Retrieval | Curated skill content, examples, and additional reviewed materials | Corpus contents, rights, retrieval strategy; vector database deferred |

The earlier proposed automatic emotion/behavior baseline, eye tracking, mouse monitoring, voice input, and four or five breathing patterns are deferred. No approved adaptive mechanism exists; do not implement automatic contraction or a “Simpler view” based on an earlier recommendation the user did not accept.

## Main experience

```text
Splash -> Home
           |-> Emotion log -> Graph -> Save confirmation -> Home or Calendar
           |                                  Calendar -> Day entries -> Edit or Delete
           |-> Breathing ready -> 3-2-1 -> Six 4-6 cycles -> Completion
           |                           |-> Pause -> Resume or End -> Home
           |-> Support chat -> Reply settings / Chat history / End -> Home
           |-> Appearance settings -> Return

Every screen and overlay -> Help -> U.S. call options -> Simulated call or Return
```

### Home and entry

The splash communicates branding only, adds no required task, and can be skipped. Keep Help available even there so the transition never becomes a barrier. Returning home does not replay the splash. Home presents Emotion log, Guided breathing, and Support chat equally; no emotion-based routing and no prerequisite check-in. Appearance is secondary. A remembered last-used activity may support a future “Use again” shortcut without launching it automatically; its exact placement remains a design detail.

### Emotion log and calendar

First page: “Hi, how are you feeling today?”, a still voice-mode-inspired bubble, a feeling slider, circular user-selected colors, optional personal color meaning, and optional “Tell me about it” text. This is a visual bubble, not a microphone or an emotion sensor. Require explicit feeling and color choices rather than saving untouched defaults. The initial wireframe uses provisional five-position feeling labels, not an approved clinical scale.

Continue opens a separate neutral graph with pleasantness left-to-right and energy bottom-to-top. Graph placement is required to save. Tap-to-place and keyboard/tap controls must edit the same point; show a text summary. Back preserves the draft. Leaving without saving discards it. Logging is optional as an activity, even though these fields are required within that activity. Missing-field messages should identify the missing input calmly. Do not force disclosure of text.

The original slider and graph are currently separate inputs. They may duplicate pleasantness ratings, and the color adds another required decision. Preserve the user's current design for the wireframe, document the D3 tradeoff, and use fictional walkthroughs to decide whether to combine inputs later. Do not silently change required fields because a lighter design seems preferable.

Save confirms “Entry saved,” with Home and View past logs. Calendar days show the latest entry's color, an entry marker/count, and a text alternative. Multiple entries on a day open as a timestamped list. Entry details include the chosen feeling, color and its meaning if supplied, point, and optional text. Edit preserves identity; Delete asks for confirmation. Include an empty state. No inferred diagnosis, anxiety score, streak, improvement judgment, or cross-user color dictionary.

### Breathing and timing

Show a short ready instruction and Begin. After Begin, display 3–2–1, then six cycles of four-second inhalation and six-second exhalation. Circle expansion/contraction, phase labels, and counts carry the pace. Do not add holds or let the model alter timing. Pause, End exercise, and Help remain usable during countdown and practice. End returns home immediately; no completion gate or penalty. Opening Help pauses practice; returning requires explicit Resume.

The planned breathing portion is 6 × (4 + 6) = 60 seconds. A conservative design budget from the first instruction on the ready screen through the final planned screen is 8 seconds reading + 2 seconds to select Begin + 3 seconds countdown + 60 seconds breathing + 2 seconds completion transition = 75 seconds. These are design assumptions, not measurements. Report splash/navigation/setup separately; do not exclude the ready instruction just to improve the number. User-chosen pauses and time in Help are excluded under the assignment. Measure actual application delays in Part 3.2.

No 90-second forced-exit timer is proposed. The assignment limits the planned guided exercise, not a person's right to stay or stop. Completion offers Repeat or Home. Reduced motion preserves text/count timing with a static circle; it also skips the opening fade. Audio, vibration, and voice are outside this initial scope.

### Open ended chat

Chat is open-ended, rather than a mandatory timed reframe. The reviewed image depicts short fictional sample messages, reply settings, history, and illustrative failure/crisis states. Reply settings replace the earlier proposal for several inline controls; the image's length and wording choices remain illustrative. They must not enable judgmental or coercive replies. End chat stays visible and ends pending work without demanding a reason. Proposed persistence retains completed messages while discarding unsent input; do not store partial streamed output as a completed response. History has a secondary entry point and conversation deletion.

The proposed model contribution is brief, nonjudgmental reflection and optional reframing using reviewed context. The user specifically wants to explore fourteen Sleight of Mouth patterns described by Dilts and O'Brien, modeled from Bandler. Preserve that interest while distinguishing it from CBT and from evidence of clinical benefit. Additional research material is a candidate corpus, not permission to ingest an unreviewed library or copyrighted books.

If a guided cognitive reframe is later added, keep the assignment's sequence intact: identify a thought, consider supporting evidence, and consider an alternative interpretation. Its planned duration must also be at most 90 seconds, with response assumptions and model delays documented. Do not relabel a long guided exercise as open chat to evade timing requirements. Breathing is the selected supplied skill for the initial core experience; a guided reframe is not required to make chat open-ended.

### Help and crisis related input

Help is designed to open directly from every screen, including inside chat, settings, history, and failure states. No model request, classifier decision, login, emotion log, or assessment can gate it. The intended local panel offers separately labeled U.S. crisis counseling and emergency-services options, plus Back. The supplied early image still shows a pending-country/number placeholder; use the confirmed resource design for later implementation. Any interactive design demo must simulate call actions.

Verified October 15, 2026: the local-hotline lookup returned [988](tel:988?oai_link_source=model_response_hotline) for crisis counseling and [the Lifeline website](https://988lifeline.org?oai_link_source=model_response_hotline). The [National 911 Program](https://www.911.gov/calling-911/frequently-asked-questions/) confirms 911 for emergency services. These resources are outside the app; do not call them therapy or imply the app has notified anyone. Final device-link behavior needs checking without placing test calls.

The accepted design response to crisis-related chat input is to interrupt ordinary reframing with a brief fixed notice, visible Help access, and an option to leave. Detection method, trigger criteria, wording, and tests remain TODOs. Detection can miss cases and misclassify statements; it must not claim to assess safety or equate intrusive thoughts with intent. Help remains usable even if detection and the model fail. A wireframe can depict the proposed state; detection and response behavior require later implementation and checks.

## Model and application responsibilities

| Application controls | Model may contribute | Model must not control |
| --- | --- | --- |
| Navigation, visible Help, exits, countdown, fixed breathing sequence, persistence, retrieval permissions, error states | Short conversational wording; reflection; optional alternatives grounded in reviewed context | Whether Help appears, whether a person can leave, breathing steps, diagnosis, inferred risk scores, forced disclosure, automatic UI contraction |
| Server-side constraints and reviewed source selection | A response that follows requested length/style within fixed boundaries | Persuading past refusal, claiming certainty, inventing therapeutic exercises, treating color as objective emotion evidence |

A system prompt should request low-stimulus, nonjudgmental language, permission before reframing, respect for refusal, and accurate prototype limits. It is one layer. Implementations also need application-controlled state and independent support access. The exact prompt and output checks remain future work.

On a request failure, show a concise message and Retry; preserve existing completed messages and keep End chat and Help available. Leaving must cancel local pending work and ignore late results for the ended view; provider-side cancellation capabilities are unresolved. Opening Help must not wait for a network timeout.

## Data and personalization proposal

Use Vue presentation, a separate frontend request layer, framework-free Python domain logic, FastAPI JSON routes, and SQLite on localhost. The following records describe intent rather than an implemented schema or API contract.

| Record | Proposed information | Purpose and user control |
| --- | --- | --- |
| Emotion entry | ID, timestamp/local date context, feeling selection, color, optional color meaning, graph coordinates/axis version, optional note | Calendar/day review; edit/delete; retain user-defined meaning without diagnosis |
| Conversation and message | IDs, completed message text/role/timestamps, completion state, source references used | Review/delete conversations; distinguish actual messages from errors and unsent drafts |
| Skill session | Fixed pattern/version, start/end, completed or ended status, active duration, pauses separately | Review sessions and verify timing without grading emotional improvement |
| Preference | Accent, text size, reduced motion, future approved reply settings, last-used activity | Remember explicit choices; usable defaults and ability to change |
| Corpus item | Source/title/URL, version/date, reviewed passage or original summary, permitted use, scope | Auditable retrieval; separate from personal records |
| Context choice | Which past records the user has explicitly chosen to include | No automatic unrestricted history access; ability to remove context |

Local SQLite persistence does not determine where model requests run. Provider, hosted versus local processing, embedding location, retention, and deletion behavior remain unresolved. Do not promise “nothing leaves the device” or “never used for training” without verifying the entire selected service configuration. The design should explain selected context and destination before it is sent. No real personal data belongs in this prototype's testing or evidence.

RAG means supplying retrieved context, not clinical training. Curated skill material and personal history serve different purposes and need separate controls. A vector database remains deferred; do not replace required SQLite or add a dependency simply because retrieval is planned. Define a JSON contract with request, response, and error shapes before Vue–FastAPI integration. Coordinate ranges, nullability, dates, validation, and error semantics are contract TODOs.

## Assignment research traceability

| Finding | Decision and rationale | Tradeoff or check |
| --- | --- | --- |
| R1 Short exercises | Fixed 60-second breathing; conservative 75-second total design budget | Measure actual delays; open chat has no forced timeout |
| R2 Frictionless crisis access | Help on every screen opens call options directly | Verify no prerequisite or model dependency |
| R3 Permission to stop | Leave log, End exercise, End chat; no penalty | Exits discard unsaved drafts; communicate persistence clearly |
| R4 User controls journey | Three equal Home options; no mandatory check-in or automatic routing | More choice on Home; one activity after selection |
| D1 Interface contraction | Explicit open design question; no detector inferred | No adaptive implementation promised for Part 1 |
| D2 One atomic skill | One breathing pattern and pacing action per exercise view | Three-option Home is a navigation tradeoff, not the exercise screen |
| D3 Minimize emotional cost | Optional text; no forced mood improvement report; bare chat | Required feeling/color/graph adds effort; evaluate rather than call it proven |
| D4 Visible safety | Help persists during countdown, practice, overlays, and errors | Test with keyboard and mobile viewport; avoid overlay occlusion |
| D5 Light personalization | Defaults; remembered explicit appearance choices and last-used skill | Configuration stays optional; automatic adaptation unresolved |
| D6 Low stimulus and neutral tone | Muted layout, still log bubble, short language, reduced motion | Soft colors still need contrast; breathing motion has a functional purpose |

## Fictional review and later verification

The supplied image was visually reviewed: it contains the three Home choices, emotion form, graph, saved/calendar/day-entry views, breathing states, chat/settings/history and illustrative failure/crisis states, appearance settings, and Help. Its Help panel still has a pending-number placeholder, and its graph labels the axes as provisional despite the user's confirmed pleasantness/energy choice. These early-image details do not replace confirmed decisions. Static images cannot verify navigation, validation, keyboard/tap operation, edit/delete, timing, pause/end, failure handling, reduced motion, or text resizing; check those behaviors when an interactive implementation exists.

Part 3.2 must demonstrate one complete skill, model contribution, SQLite conversation/session persistence, measured exercise duration, independent Help, request failure, and leaving. Part 3.3 requires at least fifteen fictional scenarios and three explicit behavior checks, expected/observed results, ordinary/interruption/failure cases, a surprising finding, an untested limitation, and repeatable mocked checks plus a small relevant live-model selection. Peer testing defaults to mocks; any live session has at most fifty model calls. Software checks do not establish clinical effectiveness.

## Open decisions and submission work

- The supplied image is linked and visually reviewed. TODO: record the actual generation prompt and tool/model identifier if available; reconcile the Help placeholder and provisional axis annotation when refining the interface.
- TODO: refine feeling selection labels and decide whether the graph duplicates them after a fictional walkthrough. Keep current required fields until a deliberate revision.
- TODO: define approved reply-setting values and age scope; adaptive UI remains unresolved.
- TODO: review the proposed fourteen-pattern influence; select any permitted subset and original examples without pressure, invalidation, or persuasion past refusal. Review repetitive reassurance and crisis-related wording before live use.
- TODO: select provider, retrieval corpus/rights, embedding approach, privacy disclosure, context consent, retention, and deletion semantics. No automatic color interpretation.
- TODO: define SQLite schema and JSON contract before integration; preserve fixed steps in domain logic.
- TODO: verify timing, accessibility, failure/exit behavior, and clean-checkout commands when implemented.
- The initial Git checkpoint is complete, and the tracked Part 3.1 `report.md` supplies repository/version/design/evidence links. TODO: confirm instructor access and submission rendering; local Git inspection does not establish either.
- TODO: update [AI use disclosure](../AI-USE.md) and [evidence log](evidence-log.md) as tools and artifacts are actually used.

## First iteration decisions — October 21, 2026

The latest user instructions now authorize implementation, synchronized original inhale/exhale audio, PWA shell support, and Emergency wording in place of Help. A discreet About description preserves the assignment's required role description; repeated fictional/prototype labels do not appear on activity screens. Still is a provisional visual name. No clinical capabilities or automatic adaptation were added.

Implementation is divided into independently buildable interface, emotion and breathing scopes. Modules own their domain/storage/contracts/tests and import no sibling feature; the shell discovers installed entry points. Breathing session history is independent of emotion calendar history to preserve those commit boundaries. See `docs/architecture.md`, `docs/implementation-checkpoints.md`, and feature contracts under `backend/app/features/`.

Logging retains explicit feeling/color/graph selection; provisional five-position feeling labels and integer −100..100 axes are documented, not asserted as validated measures. Color meaning and notes are optional, with no inference. SQLite saves are idempotent by client UUID; entries retain original date/time on edit. Domain validation, API errors, retries and persistence are implemented.

The browser owns countdown, fixed six four-in/six-out cycles and shared timing for visual/audio cues. Pause/end/Emergency work independently of network requests. Healthy browser sequences measured 63.0s including countdown; instruction-to-finish observations were 63.1s and 64.0s with stated immediate/brief-reading assumptions. The earlier 75-second budget remains an estimate. No forced timeout. Original Web Audio cues can be muted; reduced motion preserves text/static pacing. Main-thread stalls pause pacing, retaining the application delay in instruction timing. Native phone/audio listening checks remain TODOs.

The PWA caches only the built shell. Browser checks confirmed offline reload, Emergency and breathing with FastAPI stopped; history fails explicitly and personal responses are never substituted from cache. Session-save Retry works after recovery, but pending records are only in memory and can be lost on reload/close. No background synchronization promise. Local database storage does not resolve future model/provider/transmission decisions.

Chat remains a frontend stub by user scope; model contribution and persistent conversations remain outstanding Part 3.2 requirements. Original Part 3.1 report/image evidence is preserved. Actual checks, failures, commands and remaining limitations are in `docs/iteration-verification.md`; the old design descriptions above are historical where superseded here.
