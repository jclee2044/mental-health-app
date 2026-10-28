"""Strict application JSON shapes; provider settings are never request fields."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr


class TextMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    role: Literal["user", "assistant"]
    content: StrictStr


class SessionBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    sdp: StrictStr
    history: list[TextMessage] = Field(default_factory=list, max_length=16)


class ConfigResponse(BaseModel):
    status: Literal["configured", "unconfigured"]
    duration_seconds: int


class SessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    session_id: StrictStr
    sdp: StrictStr
    duration_seconds: int


class TextBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    message: StrictStr
    history: list[TextMessage] = Field(default_factory=list, max_length=16)


class TextResponse(BaseModel):
    reply: StrictStr


class SavedTurnBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    position: StrictInt
    user: StrictStr
    assistant: StrictStr


class SavedVoiceBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    position: StrictInt
    messages: list[TextMessage] = Field(min_length=1, max_length=50)
