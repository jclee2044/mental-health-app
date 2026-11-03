"""Shared HTTP scope only; no feature imports or selection logic."""
from datetime import date, datetime, timezone
from uuid import UUID
from pydantic import BaseModel, ConfigDict, StrictStr, field_validator


class StrictBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class MemoryScope(StrictBody):
    local_date: StrictStr
    conversation_id: StrictStr

    @field_validator("local_date")
    @classmethod
    def valid_date(cls, value):
        day = date.fromisoformat(value)
        if day.isoformat() != value or abs((day - datetime.now(timezone.utc).date()).days) > 1:
            raise ValueError("Use today's local calendar date.")
        return value

    @field_validator("conversation_id")
    @classmethod
    def valid_id(cls, value):
        return str(UUID(value))
