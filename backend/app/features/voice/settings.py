"""Server-owned configuration. Environment values are never returned to clients."""
import os
import re
from dataclasses import dataclass, field
from .prompts import BACKEND_INSTRUCTIONS, LIVE_INSTRUCTIONS

VOICE_DURATION_SECONDS = 300
PROVIDER_TIMEOUT_SECONDS = 10
PROVIDER_URL = "https://api.openai.com/v1/live/sessions"
MODEL = "gpt-live-1"

# Mute is a local track toggle; only close is sent over the data channel.
CLIENT_EVENTS = ("session.close",)
SERVER_EVENTS = (
    "session.started", "session.input_transcript.delta", "session.output_transcript.delta",
    "session.closed", "error",
)


@dataclass(frozen=True)
class VoiceSettings:
    api_key: str = field(default="", repr=False)
    backend_model: str = field(default="", repr=False)

    @classmethod
    def from_environment(cls):
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        # Avoid invalid/header-injecting credentials; never log the rejected value.
        if not key or len(key) > 4096 or any(not 33 <= ord(char) <= 126 for char in key):
            key = ""
        backend_model = os.environ.get("VOICE_BACKEND_MODEL", "").strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", backend_model):
            backend_model = ""
        return cls(api_key=key, backend_model=backend_model)

    @property
    def configured(self):
        return bool(self.api_key and self.backend_model)


def session_payload(sdp, backend_model, history=()):
    """Construct fresh policy containers; no browser configuration is merged."""
    return {
        "session": {
            "model": MODEL,
            "instructions": LIVE_INSTRUCTIONS,
            "audio": {"output": {"voice": "marin"}},
            "store": False,
            "input": [{
                "type": "message", "role": item["role"],
                "content": [{"type": "input_text" if item["role"] == "user" else "output_text", "text": item["content"]}],
            } for item in history],  # Only bounded, explicitly supplied current-chat text.
            "delegation": {
                "type": "responses",
                "responses": {
                    "model": backend_model,
                    "instructions": BACKEND_INSTRUCTIONS,
                    "tools": [],
                    "tool_choice": "none",
                },
            },
            "triggers": [],
            "client": {"data_channel": {
                "allowed_client_events": list(CLIENT_EVENTS),
                "allowed_server_events": [{"type": event} for event in SERVER_EVENTS],
            }},
        },
        "transport": {"type": "webrtc", "sdp": sdp},
    }
