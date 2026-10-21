from uuid import UUID
from fastapi import APIRouter, Request, Response
from .domain import validate_session
from .schemas import SessionBody

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("")
def list_sessions(request: Request):
    return {"sessions": request.app.state.breathing_store.sessions()}


@router.put("/{session_id}")
def put_session(session_id: UUID, body: SessionBody, request: Request, response: Response):
    record, created = request.app.state.breathing_store.put_session(str(session_id), validate_session(body.model_dump()))
    response.status_code = 201 if created else 200
    return record
