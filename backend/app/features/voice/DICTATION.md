# OpenAI dictation contract — October 27, 2026

User explicitly approved replacing failing browser speech recognition with
OpenAI transcription using the existing backend-only key. This is independent
of Live/Responses; no browser model/key/prompt/history or automatic retry.

POST /api/chat/transcriptions requires application/json, no query parameters,
and exactly {"audio":"<strict base64>","mime_type":"audio/webm"} or audio/mp4.
No data URL, filename, identity, settings, tools or extra fields. Duplicate keys,
non-finite JSON constants and invalid base64 are rejected. Wire cap: 3 MiB,
checked before/while reading even without Content-Length. Decoded cap: 2 MiB;
nonempty WebM EBML prefix or MP4 ftyp prefix required. Prefix checking is not a
full media decoder/duration check. Browser recording stops at 30 seconds; backend
validates size/format, not actual encoded duration. Keep this localhost only.

200 returns exactly {"text":"<nonempty transcript>"}, at most 4,000 characters /
8,000 UTF-8 bytes, stripped. Browser appends to the current editable draft within
those same bounds. No automatic chat generation or persistence. Only choosing
Send makes the draft normal typed-chat input and eligible for typed-pair storage.

Server sends one multipart POST to https://api.openai.com/v1/audio/transcriptions
with model=gpt-transcribe, response_format=json, server-named dictation.webm/mp4
and canonical content type. Server owns a random boundary and Authorization.
No SDK/dependencies; reuse standard-library bounded transport, no redirects,
no retries, 20-second socket I/O timeout (not strict wall clock), 128-KiB provider
response cap, require 200 JSON and validate/project text. Only api_key is required;
VOICE_BACKEND_MODEL is unrelated. No history, prompts, tools or retention setting
is sent to transcription. Do not invent a store:false option or privacy promise.
Audio is in process/browser memory only; this app writes no recording/file/DB/log.
Provider retention/data controls remain separate and unverified.

All responses use existing Cache-Control:no-store and fixed error envelope:
{"error":{"code":"dictation_unavailable","message":"Transcription could not be completed. You can still type.","fields":{}}}
413 request_too_large; 415 unsupported_media_type; 422 validation_error;
503 dictation_unconfigured; 502 dictation_unavailable/dictation_invalid_response;
504 dictation_timeout. No raw exception/provider body/credential is returned.

Browser requires MediaRecorder and an encodable WebM/Opus or MP4 format.
Explicit microphone action only; unsupported/denied errors preserve typing.
States: idle, starting, recording, transcribing, error. Mic again finishes recording;
click while starting/transcribing cancels. Capture tracks stop before upload.
Chunks are bounded while recording; audio conversion/upload is separately bounded
and cancellable. Exits, Emergency/overlays, hidden pages, Send and voice start
abort capture/upload and reject stale work. No automatic restart or retry.
A 30-second finalization/transcription timer prevents stuck local state. Network
abort cannot guarantee provider cancellation, retention deletion or no charge.

Checks use fictional bytes, fake capture/recorders and mocked provider requests.
No paid calls or real microphone checks. Actual transcription quality, key model
entitlement, WebM/MP4 decode compatibility and provider cancellation remain TODOs.
Sources: https://developers.openai.com/api/docs/guides/speech-to-text and
https://developers.openai.com/api/reference/resources/audio/subresources/transcriptions/methods/create
