# Chat: native voice and independent text

October 26, 2026. Self-registering feature: Vue presentation in `ChatView.vue`,
endpoint declarations in `api.js`, shared HTTP in `src/api/client.js`, native
resources in `voice.js`, lifecycle wiring in `lifecycle.js`, transient state in `useChat.js`, caption/context rules
in `domain.js`. No dependency additions. No audio/caption storage. Completed typed
pairs now persist through `useConversationRecords.js`, independently of generation.
`ConversationHistoryView.vue` / `useConversationHistory.js` provide read-only review
and confirmed deletion. The feature's registration owns the retry queue across
navigation. [Persistence contract](../../../../backend/app/features/voice/PERSISTENCE.md)
and [submission validation](../../../../docs/part32-validation.md) describe bounds,
failure behavior, retention and inspection. Old records are never automatically
used as model context. Provider configuration and voice behavior below are preserved.

The bordered chat frame contains a scrollable conversation and a composer. Voice
mode is integrated into the rounded message input; active/error status and voice controls appear
within the composer instead of a separate panel. Voice buttons use type=button
so they never submit the typed draft. End chat appears beneath Send after the
first message or voice-start attempt and stays available for that conversation.
The idle heading/opening follows the user’s chosen minimal invitation. A short
privacy line links to expandable transmission/context/storage details.

No API or device activity on mount. Selecting Voice mode checks config, then
requests exactly `getUserMedia({ audio: true, video: false })`. Add audio tracks
(disabled until readiness); create `RTCPeerConnection` and `oai-events` listeners
before the offer. Set the local offer, await complete ICE gathering, POST final
`localDescription.sdp`, apply the returned answer. Active requires both successful
answer application and the matching `session.started`. Channel open/ICE connected
alone are insufficient. Never send browser session configuration or `session.start`.

Lifecycle JSON (`session.started` / `session.closed`) may include resolved server
prompts and history. Accept these snapshots up to 128 KiB UTF-8, projecting only
the matching ID/readiness or finalization signal. Do not display/log the snapshot.
Other event envelopes retain the 16,000-character bound; caption text retains its
4,000-character bound. The former global 16,000-character guard could silently
discard readiness with the current prompts (startup configuration exceeds 17 KB).

States: Permission, Connecting, Active, Muted, Closing, Closed, Error. Mute/Unmute
toggle only local microphone tracks immediately, without network commands or
acknowledgments. Assistant playback, the provider session and billing continue;
the interface says so beside Mute and offers End. Remote audio plays through an audio element. If play fails, the
Enable assistant audio button retries play synchronously from its user gesture.
Captions/text stay usable. Captions are grouped by their speech timeline, never
packet arrival: separate same-speaker bubbles after a timeline gap following the
other speaker, or at least 1s silence. Contiguous/overlapping speech can grow
through a backchannel. Late fragments rebuild the session's bubbles, including
late speaker changes, preserving spaces/repeated words and event deduplication.
Live has no turn-completed marker, so these remain approximate speech groups,
not guaranteed exact utterances, completed turns or confirmed audio playback.

End releases capture/playback immediately, sends session.close when possible,
and waits at most 2 seconds for session.closed before releasing transports and
reporting finalization unconfirmed. End chat, navigation/unmount, overlays (including
Emergency), hidden document, hash navigation, pagehide/beforeunload and terminal
failures release immediately. Lifecycle listeners are removed on unmount.
Duplicate Start and repeated End are ignored; one close command/HTTP fallback
per run. Late permission tracks are stopped and stale callbacks cannot restart audio.
An already-sent creation request remains readable until its 15-second timeout.
Late SDP IDs are closed through POST /api/voice/sessions/{id}/end without applying
the answer or touching a newer conversation. Immediate/failed/unacknowledged
channel closure uses the same 5-second-bounded keepalive fallback. A confirmed
session.closed does not send a redundant HTTP close. Failed fallback never retries
or revives UI; finalization stays unconfirmed without the channel acknowledgment.
The backend attempts closure if it observes a disconnected creation requester.
Hangup's WebRTC applicability is unverified (the reference describes SIP), so
fallback termination must not be claimed as observed; see the backend contract.
Returning requires explicit microphone selection. Connection setup is bounded
to 25 seconds after permission; ignored permission remains cancellable. No retry
or reconnect. The server duration (currently 300 seconds) starts at Active and
ends voice only. Browser timers do not guarantee provider expiry or bound billing
after suspension/crashes; server reconciliation remains TODO.

The independent POST /api/chat/messages endpoint works without voice permission
or WebRTC. Sending text first stops voice, preserves drafts after errors and
never invents an assistant response. Context is at most 16 messages
and 6,000 UTF-8 bytes, shared between modes: completed typed messages and visible
approximate voice captions. Failed/pending typed messages are excluded. Voice
starts a fresh transport/session with server-projected initial history (or []).
It preserves all visible bubbles, including earlier voice captions; starting an
entirely new chat clears them. Sending text stops voice and passes the visible
conversation to Responses; explicitly selecting the microphone carries that
context back to Live. This is context continuity across transport changes, not
simultaneous text injection into an active Live session. The interface discloses
recent-context sharing and microphone behavior. Visible messages,
captions and drafts clear on leaving. Completed typed pairs are saved separately
to SQLite with explicit success/failure/Retry; failed model requests and voice
captions are excluded. Pending saves survive navigation within the loaded app,
but reload/close loses unsaved queues. Records remain until deleted in history;
deletion affects local SQLite only. No browser local storage, audio recording,
voice transcript database or offline API caching. Provider
store:false makes no general retention/no-training promise. Emergency and exits
remain application-owned, never dependent on a request/model decision.

Observed: Node tests use fake browser/media/peer/audio/timer APIs and fake endpoint
responses. The real SFC is rendered with mocked state using the existing Vue
compiler/server renderer, checking all seven states, enabled typing and End chat.
This is not actual browser/device evidence. Tests cover ordering, denial/cancel,
late completions, ICE/close timeouts, playback gesture recovery, local mute,
captions, duration and text fallback. No real microphone or paid calls. Browser
permission/autoplay, speaker quality, provider compatibility and model behavior
remain unverified. Demonstrations must simulate resource calls.

Commands: npm --prefix frontend test; non-mutating Oxlint/ESLint; npm --prefix
frontend run build; project pytest and checkpoint commands in the root README.
The existing three checkpoint scopes are unchanged and omit this new feature;
full-checkout tests/build cover chat separately.

The subsequent [verification record and manual checklist](../../../../docs/voice-verification.md)
contains observed rerun results and a planned one-attempt live test under 60s.
The live checklist is not evidence of an executed browser/provider conversation.

Sources: [OpenAI WebRTC](https://developers.openai.com/api/docs/guides/voice-webrtc),
[Live events](https://developers.openai.com/api/docs/guides/live-conversations),
[media playback](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/play).


## Historical browser-recognition attempt — October 27, 2026

Superseded by the OpenAI recording increment below.

The waveform button starts the existing OpenAI voice conversation. The separate
microphone to its left starts browser SpeechRecognition/webkitSpeechRecognition
in English (en-US), adding final recognized phrases to the current editable draft.
Nothing submits automatically. Duplicate/interim results are excluded; the existing
4,000-character/8,000-byte draft limits apply. Stop dictation aborts recognition
and keeps accepted text. Unaccepted/late fragments are discarded. Recognition
stops on Send, voice start, navigation, Emergency/overlays, hidden pages, unmount,
error or the 60-second dictation limit. No automatic restart. Permission/unsupported
failures keep typing available. Both controls overlay the compact textarea;
space is reserved so draft text does not run underneath them. Active voice controls
use a separate row inside the input to avoid covering text on narrow screens.

Browser recognition support and service availability vary. It may send audio to
the browser vendor's online speech service; it is not a promise of local/offline
processing. The disclosure names this separately from OpenAI voice/text. No new
backend endpoint, dependency, key, model call or app audio storage is involved.
Dictated words become normal typed content only when the user selects Send;
completed typed pairs then follow the existing persistence contract.

Reference: [MDN SpeechRecognition](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition).
Mocked checks cover final/deduplicated text, edited drafts, bounds, unsupported and
denied recognition, startup failure, timeout, late events, Send/voice switch and
all lifecycle exits. Actual microphone recognition/service availability and
physical-device layout remain unverified; no microphone or paid call was opened
for this increment.


## Current OpenAI dictation — October 27, 2026

The user approved replacing browser SpeechRecognition with MediaRecorder capture
and server-owned OpenAI transcription. Select the microphone, speak, then select
its check icon to finish and transcribe. Capture stops immediately; the transcript
is appended to the latest editable draft and never auto-sent. Cancel dictation
is visible during capture/upload. Typing stays usable. Recordings stop at 30s,
are capped at 2 MiB, and are kept only in browser/server memory. Exits, Emergency,
hidden pages, Send and starting voice cancel capture/upload and reject late work.
No browser vendor recognition service or fallback is used. No automatic retries,
new dependency, audio file/DB persistence or microphone checks were added.

MediaRecorder must support WebM/Opus or MP4. Unsupported/denied capture keeps
text available. State is idle/starting/recording/transcribing/error. The feature
api.js declares the new endpoint; shared api/client.js remains the only HTTP
transport. The backend fixes gpt-transcribe and sends no conversation/prompt/tools.
Existing server-only OPENAI_API_KEY is required; VOICE_BACKEND_MODEL is unrelated.
No store:false claim is made for the transcription API. Cancelling the HTTP
request does not guarantee provider-side cancellation or avoid usage charges.
[Full JSON/audio/error contract](../../../../backend/app/features/voice/DICTATION.md).

Verified with fake capture/chunks/API responses and mocked provider requests.
Actual recording, transcript quality, provider audio decoding and cancellation
remain unverified. Model visibility was checked read-only; no paid call was made.


## Unified saved chats — October 27, 2026

Typed pairs and spoken transcript text now share one history and conversation id.
Voice text queues when voice ends/errors or on leaving; current mixed-mode order
is preserved. History presents both as normal text conversations, with a top-right
New button and confirmed deletion. No recordings are saved. Save failures/retries
remain visible across navigation; reload can lose pending or in-progress text.
No historical context is automatically sent to the model. Old voice conversations
that were never persisted cannot be backfilled. This supersedes prior voice-text
transience notes, but not raw-audio non-persistence. See PERSISTENCE.md for bounds,
additive schema, idempotency, approximate-caption limits and ordering contract.
