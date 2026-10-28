"""Bounded JSON input and sanitized errors; no provider details reach the browser."""
import re
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool
from starlette.requests import ClientDisconnect
from .domain import InvalidProviderResponse, InvalidSdp, OversizedSdp, validate_sdp, validate_text_input, validate_history, validate_saved_turn
from .http import RequestTooLarge, read_json
from .lifecycle import UnknownSession
from .provider import ProviderTimeout, ProviderUnavailable
from .schemas import ConfigResponse, SessionBody, SessionResponse, TextBody, TextResponse, SavedTurnBody, SavedVoiceBody
from .storage import ConversationConflict
from .settings import VOICE_DURATION_SECONDS
from .domain import validate_saved_voice

router = APIRouter(prefix="/api/voice", tags=["voice"])
text_router = APIRouter(prefix="/api/chat", tags=["chat"])


def failure(status, code, message):
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message, "fields": {}}})


@router.get("/config", response_model=ConfigResponse)
def config(request: Request):
    if request.query_params:
        return failure(422, "validation_error", "Voice configuration is controlled by the server.")
    return {"status": "configured" if request.app.state.voice_settings.configured else "unconfigured", "duration_seconds": VOICE_DURATION_SECONDS}


@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(request: Request):
    if request.query_params:
        return failure(422, "validation_error", "Send an SDP offer and optional recent conversation.")
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        return failure(415, "unsupported_media_type", "Send the SDP offer as JSON.")
    try:
        data = await read_json(request)
        body = SessionBody.model_validate(data)
        history = validate_history([item.model_dump() for item in body.history], max_bytes=6000)
    except RequestTooLarge:
        return failure(413, "request_too_large", "The voice request is too large.")
    except (ValueError, UnicodeError, ValidationError, RecursionError, ClientDisconnect):
        return failure(422, "validation_error", "Check the SDP offer and recent conversation.")
    try:
        sdp = validate_sdp(body.sdp)
    except OversizedSdp:
        return failure(413, "sdp_too_large", "The SDP offer is too large.")
    except InvalidSdp:
        return failure(422, "invalid_sdp", "Send a valid audio SDP offer.")
    if not request.app.state.voice_settings.configured:
        return failure(503, "voice_unconfigured", "Voice is not configured on the local server.")
    try:
        session_id, answer = await run_in_threadpool(request.app.state.voice_provider.create_session, sdp, history)
    except ProviderTimeout:
        return failure(504, "voice_provider_timeout", "Voice setup timed out. The session outcome is unknown; do not retry automatically.")
    except ProviderUnavailable:
        return failure(502, "voice_provider_unavailable", "Voice setup could not be completed. The session outcome may be unknown; do not retry automatically.")
    except InvalidProviderResponse:
        return failure(502, "voice_provider_invalid_response", "Voice setup returned an invalid response. Do not retry automatically.")
    if await request.is_disconnected():
        # A browser that exited cannot receive the ID and close its late session.
        try:
            await run_in_threadpool(request.app.state.voice_provider.end_session, session_id)
        except (ProviderUnavailable, InvalidProviderResponse):
            pass  # No confirmed finalization; never expose provider details.
        return failure(409, "voice_start_abandoned", "Voice setup was abandoned.")
    return {"session_id": session_id, "sdp": answer, "duration_seconds": VOICE_DURATION_SECONDS}


@router.post("/sessions/{session_id}/end")
async def end_session(session_id: str, request: Request):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", session_id) or request.query_params:
        return failure(422, "validation_error", "Check the voice session identifier.")
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        return failure(415, "unsupported_media_type", "Send an empty JSON object.")
    try:
        if await read_json(request) != {}:
            raise ValueError()
    except RequestTooLarge:
        return failure(413, "request_too_large", "The voice request is too large.")
    except (ValueError, UnicodeError, RecursionError, ClientDisconnect):
        return failure(422, "validation_error", "Send an empty JSON object.")
    try:
        state = await run_in_threadpool(request.app.state.voice_provider.end_session, session_id)
    except UnknownSession:
        return failure(404, "voice_session_unknown", "This server does not know that voice session.")
    except ProviderTimeout:
        return failure(504, "voice_close_unconfirmed", "Voice session closure could not be confirmed.")
    except (ProviderUnavailable, InvalidProviderResponse):
        return failure(502, "voice_close_unconfirmed", "Voice session closure could not be confirmed.")
    return Response(status_code=204) if state == "closed" else JSONResponse(status_code=202, content={"status": "closing"})


@text_router.post("/messages", response_model=TextResponse)
async def send_text(request: Request):
    if request.query_params:
        return failure(422, "validation_error", "Send only a message and the current text conversation.")
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        return failure(415, "unsupported_media_type", "Send the message as JSON.")
    try:
        body = TextBody.model_validate(await read_json(request))
        message, history = validate_text_input(body.model_dump())
    except RequestTooLarge:
        return failure(413, "request_too_large", "The chat request is too large.")
    except (ValueError, UnicodeError, ValidationError, RecursionError, ClientDisconnect):
        return failure(422, "validation_error", "Check the message and current text conversation.")
    if not request.app.state.voice_settings.configured:
        return failure(503, "chat_unconfigured", "Chat is not configured on the local server.")
    try:
        reply = await run_in_threadpool(request.app.state.voice_provider.reply_text, message, history)
    except ProviderTimeout:
        return failure(504, "chat_provider_timeout", "The reply timed out. It has not been retried.")
    except ProviderUnavailable:
        return failure(502, "chat_provider_unavailable", "The reply could not be completed. It has not been retried.")
    except InvalidProviderResponse:
        return failure(502, "chat_provider_invalid_response", "The reply was unavailable. It has not been retried.")
    return {"reply": reply}


@text_router.put("/conversations/{conversation_id}/turns/{turn_id}")
async def save_turn(conversation_id: UUID, turn_id: UUID, request: Request):
    if request.query_params:
        return failure(422, "validation_error", "Send only the typed exchange.")
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        return failure(415, "unsupported_media_type", "Send the exchange as JSON.")
    try:
        body = SavedTurnBody.model_validate(await read_json(request))
        values = validate_saved_turn(body.model_dump())
    except RequestTooLarge:
        return failure(413, "request_too_large", "The saved exchange is too large.")
    except (ValueError, UnicodeError, ValidationError, RecursionError, ClientDisconnect):
        return failure(422, "validation_error", "Check the typed exchange.")
    try:
        created = await run_in_threadpool(request.app.state.chat_store.save_turn, str(conversation_id), str(turn_id), values)
    except ConversationConflict:
        return failure(409, "conversation_conflict", "This saved exchange conflicts with an existing record.")
    return JSONResponse(status_code=201 if created else 200, content={
        "conversation_id": str(conversation_id), "turn_id": str(turn_id), "saved": True})


@text_router.put("/conversations/{conversation_id}/voice-turns/{turn_id}")
async def save_voice_turn(conversation_id: UUID, turn_id: UUID, request: Request):
    if request.query_params:
        return failure(422, "validation_error", "Send only the transcript batch.")
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        return failure(415, "unsupported_media_type", "Send the transcript as JSON.")
    try:
        body = SavedVoiceBody.model_validate(await read_json(request))
        values = validate_saved_voice(body.model_dump())
    except RequestTooLarge:
        return failure(413, "request_too_large", "The transcript batch is too large.")
    except (ValueError, UnicodeError, ValidationError, RecursionError, ClientDisconnect):
        return failure(422, "validation_error", "Check the transcript batch.")
    try:
        created = await run_in_threadpool(request.app.state.chat_store.save_voice_turn, str(conversation_id), str(turn_id), values)
    except ConversationConflict:
        return failure(409, "conversation_conflict", "This transcript conflicts with an existing record.")
    return JSONResponse(status_code=201 if created else 200, content={
        "conversation_id": str(conversation_id), "turn_id": str(turn_id), "saved": True})


@text_router.get("/conversations")
def list_conversations(request: Request):
    return {"conversations": request.app.state.chat_store.conversations()}


@text_router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: UUID, request: Request):
    record = request.app.state.chat_store.conversation(str(conversation_id))
    if record is None:
        raise HTTPException(404, "Conversation not found.")
    return record


@text_router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: UUID, request: Request):
    if not request.app.state.chat_store.delete(str(conversation_id)):
        raise HTTPException(404, "Conversation not found.")
    return Response(status_code=204)
