"""Audio is bounded in memory and forwarded once; no audio persistence."""
import json
from fastapi import APIRouter, Request
from starlette.concurrency import run_in_threadpool
from starlette.requests import ClientDisconnect
from .dictation_domain import MAX_DICTATION_BODY, decode_audio
from .http import unique_object, reject_constant
from .routes import failure
from .domain import InvalidProviderResponse
from .provider import ProviderTimeout, ProviderUnavailable

dictation_router = APIRouter(prefix="/api/chat", tags=["chat"])


@dictation_router.post("/transcriptions")
async def transcribe(request: Request):
    if request.query_params:
        return failure(422, "validation_error", "Send only the recording and audio format.")
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        return failure(415, "unsupported_media_type", "Send the recording as JSON.")
    try:
        length = int(request.headers.get("content-length", "0"))
        if length < 0:
            raise ValueError()
        if length > MAX_DICTATION_BODY:
            return failure(413, "request_too_large", "The recording is too large.")
        chunks, size = [], 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > MAX_DICTATION_BODY:
                return failure(413, "request_too_large", "The recording is too large.")
            chunks.append(chunk)
        audio, mime, extension = decode_audio(json.loads(b"".join(chunks), object_pairs_hook=unique_object, parse_constant=reject_constant))
    except (ValueError, UnicodeError, RecursionError, ClientDisconnect):
        return failure(422, "validation_error", "Send a valid WebM or MP4 recording, up to 2 MiB.")
    if not request.app.state.voice_settings.api_key:
        return failure(503, "dictation_unconfigured", "Dictation is not configured on the local server.")
    try:
        text = await run_in_threadpool(request.app.state.voice_provider.transcribe, audio, mime, extension)
    except ProviderTimeout:
        return failure(504, "dictation_timeout", "Transcription timed out. Your existing draft is unchanged.")
    except ProviderUnavailable:
        return failure(502, "dictation_unavailable", "Transcription could not be completed. You can still type.")
    except InvalidProviderResponse:
        return failure(502, "dictation_invalid_response", "No usable transcript was returned. You can still type.")
    return {"text": text}
