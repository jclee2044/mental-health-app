"""HTTP shapes only; semantic validation belongs to domain.py."""
from pydantic import BaseModel, ConfigDict, StrictStr


class SessionBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    pattern: StrictStr
    status: StrictStr
    started_at: StrictStr
    ended_at: StrictStr
    local_date: StrictStr
    sequence_seconds: float
    active_seconds: float
    pause_seconds: float
    instruction_seconds: float
