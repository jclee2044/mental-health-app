"""Separate bounded post-chat task; GET and chat/voice setup never generate it."""
from threading import Lock
from uuid import UUID
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import StrictBool
from starlette.concurrency import run_in_threadpool
from ...provider_errors import InvalidProviderResponse, ProviderTimeout, ProviderUnavailable
from .routes import body, no_query
from .schemas import StrictBody
from .summary_storage import SummaryStorage
from .summary_domain import validate_summary

summary_router = APIRouter(prefix='/api/personal-memory/conversations', tags=['personal-memory'])
_generation_lock = Lock()


class SummaryBody(StrictBody):
    retry: StrictBool = False


def failure(status, code, message):
    return JSONResponse(status_code=status, content={'error': {'code': code, 'message': message, 'fields': {}}})


def generate(app, conversation_id, retry):
    store = SummaryStorage(app.state.personal_memory.database)
    if not _generation_lock.acquire(blocking=False):
        return failure(409, 'memory_summary_busy', 'Another memory summary is being prepared. You can retry this summary later.')
    try:
        claim = store.claim(conversation_id, retry)
        if claim['status'] != 'claimed':
            return JSONResponse(status_code=202 if claim['status'] == 'pending' else 200, content=claim)
        if not app.state.voice_settings.configured:
            store.finish(conversation_id, claim['token'], failed=True)
            return failure(503, 'memory_summary_unconfigured', 'Memory summaries need model configuration. Recent chat excerpts still work.')
        try:
            result = validate_summary(app.state.voice_provider.summarize_memory(claim['input']))
        except (ProviderUnavailable, InvalidProviderResponse, ValueError, UnicodeError, RecursionError) as exc:
            result = store.finish(conversation_id, claim['token'], failed=True)
            if result['status'] == 'discarded':
                return result
            return failure(504 if isinstance(exc, ProviderTimeout) else 502, 'memory_summary_unavailable',
                           'The memory summary could not be prepared. Recent chat excerpts still work.')
        return store.finish(conversation_id, claim['token'], summary=result)
    finally:
        _generation_lock.release()


@summary_router.get('/{conversation_id}/summary')
def status(conversation_id: UUID, request: Request):
    no_query(request)
    return SummaryStorage(request.app.state.personal_memory.database).status(str(conversation_id))


@summary_router.post('/{conversation_id}/summary')
async def summarize(conversation_id: UUID, request: Request):
    values = await body(request, SummaryBody)
    return await run_in_threadpool(generate, request.app, str(conversation_id), values.retry)
