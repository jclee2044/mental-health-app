"""Application-only consent/scope; never browser model configuration."""
from datetime import date, datetime, timezone
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, StrictBool, StrictStr, field_validator


class StrictBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Preferences(StrictBody):
    emotions: StrictBool
    conversations: StrictBool
    facts: StrictBool


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


class PreviewBody(MemoryScope):
    query: StrictStr = ""

    @field_validator("query")
    @classmethod
    def valid_query(cls, value):
        if len(value.encode("utf-8")) > 1000:
            raise ValueError("Shorten the search.")
        return value


class FactBody(StrictBody):
    text: StrictStr
    conversation_id: StrictStr | None = None

    @field_validator("text")
    @classmethod
    def valid_text(cls, value):
        value = value.strip()
        if not value or len(value.encode("utf-8")) > 500 or any(ord(char) < 32 for char in value):
            raise ValueError("Use 1–500 UTF-8 bytes without control characters.")
        return value

    @field_validator("conversation_id")
    @classmethod
    def valid_source(cls, value):
        return str(UUID(value)) if value is not None else None


class ExclusionBody(StrictBody):
    kind: Literal["emotion", "conversation"]
    source_id: StrictStr

    @field_validator("source_id")
    @classmethod
    def valid_id(cls, value):
        return str(UUID(value))
