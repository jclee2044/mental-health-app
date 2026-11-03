"""Explicit consent, user-confirmed facts and source exclusions, all local."""
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from pydantic import ValidationError
from starlette.requests import ClientDisconnect
from ..voice.http import read_json, RequestTooLarge
from ...errors import ValidationError as DomainError
from .schemas import Preferences, PreviewBody, FactBody, ExclusionBody
from .storage import MemoryConflict
from .context import prepare

router = APIRouter(prefix="/api/personal-memory", tags=["personal-memory"])


def no_query(request):
    if request.query_params:
        raise DomainError({"request": "Query parameters are not supported."})


async def body(request, schema):
    no_query(request)
    if request.headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
        raise HTTPException(415, "Send JSON.")
    try:
        return schema.model_validate(await read_json(request))
    except RequestTooLarge:
        raise HTTPException(413, "The memory request is too large.") from None
    except (ValueError, UnicodeError, ValidationError, RecursionError, ClientDisconnect):
        raise DomainError({"request": "Check the memory fields and limits."}) from None


@router.get("/preferences")
def preferences(request: Request):
    no_query(request)
    return request.app.state.personal_memory.preferences()


@router.put("/preferences")
async def set_preferences(request: Request):
    values = await body(request, Preferences)
    return request.app.state.personal_memory.set_preferences(values.model_dump())


@router.get("/facts")
def facts(request: Request):
    no_query(request)
    return {"facts": request.app.state.personal_memory.facts()}


@router.put("/facts/{fact_id}")
async def put_fact(fact_id: UUID, request: Request):
    values = await body(request, FactBody)
    try:
        return request.app.state.personal_memory.put_fact(str(fact_id), **values.model_dump())
    except MemoryConflict as exc:
        raise HTTPException(409, str(exc)) from None


@router.delete("/facts/{fact_id}", status_code=204)
def delete_fact(fact_id: UUID, request: Request):
    no_query(request)
    if not request.app.state.personal_memory.delete_fact(str(fact_id)):
        raise HTTPException(404, "Memory not found.")
    return Response(status_code=204)


@router.get("/exclusions")
def exclusions(request: Request):
    no_query(request)
    return {"exclusions": request.app.state.personal_memory.exclusions()}


@router.put("/exclusions")
async def exclude(request: Request):
    values = await body(request, ExclusionBody)
    request.app.state.personal_memory.exclude(values.kind, values.source_id)
    return {"excluded": True}


@router.delete("/exclusions/{kind}/{source_id}", status_code=204)
def restore(kind: str, source_id: UUID, request: Request):
    no_query(request)
    if kind not in {"emotion", "conversation"}:
        raise HTTPException(404, "Memory source not found.")
    request.app.state.personal_memory.restore(kind, str(source_id))
    return Response(status_code=204)


@router.post("/preview")
async def preview(request: Request):
    scope = await body(request, PreviewBody)
    _, report = await prepare(request.app.state.personal_memory, scope, scope.query)
    return report


@router.get("/sources/{kind}/{source_id}")
def original(kind: str, source_id: UUID, request: Request):
    no_query(request)
    if kind == "conversation":
        record = request.app.state.chat_store.conversation(str(source_id))
    elif kind == "emotion":
        record = request.app.state.emotion_store.entry(str(source_id))
    else:
        raise HTTPException(404, "Memory source not found.")
    if record is None:
        raise HTTPException(404, "The original record is no longer saved.")
    return {"kind": kind, "record": record}
