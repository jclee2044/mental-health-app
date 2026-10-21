"""HTTP orchestration: shape → domain validation → storage → response."""
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, Response
from .domain import validate_entry
from .schemas import EntryBody

router = APIRouter(prefix="/api/entries", tags=["entries"])


@router.get("")
def list_entries(request: Request):
    return {"entries": request.app.state.emotion_store.entries()}


@router.get("/{entry_id}")
def get_entry(entry_id: UUID, request: Request):
    record = request.app.state.emotion_store.entry(str(entry_id))
    if record is None:
        raise HTTPException(404, "Entry not found.")
    return record


@router.put("/{entry_id}")
def put_entry(entry_id: UUID, body: EntryBody, request: Request, response: Response):
    values = validate_entry(body.model_dump())
    record, created = request.app.state.emotion_store.put_entry(str(entry_id), values)
    response.status_code = 201 if created else 200
    return record


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: UUID, request: Request):
    if not request.app.state.emotion_store.delete_entry(str(entry_id)):
        raise HTTPException(404, "Entry not found.")
    return Response(status_code=204)
