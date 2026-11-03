"""Application-only consent/scope; never browser model configuration."""
from typing import Literal
from uuid import UUID
from pydantic import StrictBool, StrictStr, field_validator
from ...context_contracts import MemoryScope, StrictBody


class Preferences(StrictBody):
    emotions: StrictBool
    conversations: StrictBool
    facts: StrictBool


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
